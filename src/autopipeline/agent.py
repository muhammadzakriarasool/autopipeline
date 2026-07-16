"""LangChain agent — uses DataHub tools to explore metadata and generate pipeline code."""

import os
from datahub.sdk.main_client import DataHubClient
from datahub_agent_context.langchain_tools import build_langchain_tools
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from autopipeline.context import PipelineContext, short_name
from autopipeline.composer import compose_pipeline_prompt
from autopipeline.generator import PipelineGenerator

SYSTEM_PROMPT = """You are AutoPipeline, an expert data engineer agent that generates production-ready
pipeline code (dbt models, SQL transformations, Airflow DAGs) grounded in real DataHub metadata.

## Workflow
1. Search DataHub for relevant datasets using the search tool
2. Get schema details using list_schema_fields
3. Explore lineage using get_lineage
4. Generate production-quality code with CTEs, type casting, source() refs
5. Write back: tag generated models, add documentation

## Rules
- Use CTEs (WITH clauses), not subqueries
- One CTE per source table
- Column descriptions from DataHub metadata
- dbt tests: not_null for IDs, unique for emails
- Handle NULL values explicitly
- Output code directly, no markdown fences"""


def build_agent(api_key: str, server: str, token: str, model: str = "openrouter/free"):
    client = DataHubClient(server=server, token=token)
    tools = build_langchain_tools(client, include_mutations=True)
    llm = ChatOpenAI(model=model, openai_api_key=api_key,
                      openai_api_base="https://openrouter.ai/api/v1", temperature=0.2, max_tokens=8000,
                      default_headers={"HTTP-Referer": "https://github.com/muhammadzakriarasool/autopipeline", "X-Title": "AutoPipeline"})
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT), MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"), MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                             max_iterations=15, handle_parsing_errors=True, return_intermediate_steps=True)
    return executor, client


def generate_with_agent(pipeline_ctx: PipelineContext, query: str, framework: str,
                        api_key: str, server: str, token: str, output_dir: str) -> dict:
    model_name = query.lower().replace(" ", "_").replace("/", "_")[:60]
    task = (
        f"Generate a production {framework} pipeline for: {query}\n\n"
        f"Target: {pipeline_ctx.target_dataset.name} ({pipeline_ctx.target_dataset.urn})\n"
        f"Upstreams: {len(pipeline_ctx.upstream_datasets)} datasets\n"
        f"Use DataHub tools to explore metadata, then generate the code and write it back."
    )
    try:
        executor, _ = build_agent(api_key, server, token)
        result = executor.invoke({"input": task})
        output = result.get("output", "")
        # Parse artifacts if present
        import re
        artifacts = {}
        if "<artifacts>" in output:
            parts = re.findall(r'<artifact type="(\w+)" name="([^"]+)">(.*?)</artifact>', output, re.DOTALL)
            for atype, aname, content in parts:
                ext = {".sql": ".sql", ".yaml": ".yml", ".yml": ".yml"}.get(atype, ".txt")
                artifacts[f"{aname}{ext}"] = content.strip()
        if artifacts:
            import os as _os
            out_path = _os.path.join(output_dir, "models")
            _os.makedirs(out_path, exist_ok=True)
            written = {}
            for fname, content in artifacts.items():
                fpath = _os.path.join(out_path, fname)
                with open(fpath, "w") as f:
                    f.write(content)
                written[fname] = fpath
            return {"method": "agent", "model_name": model_name, "artifacts": written, "agent_output": output[:2000]}
        else:
            gen = PipelineGenerator()
            arts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output_dir, framework=framework)
            return {"method": "template_fallback", "model_name": model_name, "artifacts": arts, "agent_output": output[:2000]}
    except Exception as e:
        gen = PipelineGenerator()
        arts = gen.write_artifacts(pipeline_ctx, model_name, output_dir=output_dir, framework=framework)
        return {"method": "template_error_fallback", "error": str(e), "model_name": model_name, "artifacts": arts}
