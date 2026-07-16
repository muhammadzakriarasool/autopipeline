{{ config(
    materialized='table',
    description='Contains information about marketing promotions and campaigns',
    tags=[' None})']
) }}

/*
  AutoPipeline Generated: promotion_analysis
  Generated at: 2026-07-16T14:46:49.713141+00:00
  Target: urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.promotions,PROD)
  Sources: order_entry_db.order_entry.promotions
*/

WITH

PROMOTIONS AS (
    SELECT
        promotion_id::NUMBER(38,0) AS promotion_id,        promotion_name::VARCHAR(16777216) AS promotion_name,        promotion_start_date::VARCHAR(16777216) AS promotion_start_date,        promotion_end_date::VARCHAR(16777216) AS promotion_end_date,        promotion_description::VARCHAR(16777216) AS promotion_description,        promotion_cost::FLOAT AS promotion_cost    FROM {{ source('order_entry_db', 'PROMOTIONS') }}
),


final AS (
    SELECT
        promotion_id,        promotion_name,        promotion_start_date,        promotion_end_date,        promotion_description,        promotion_cost    FROM PROMOTIONS)

SELECT * FROM final