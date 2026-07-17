"""Tests for AutoPilot Streamlit UI."""
from unittest.mock import patch

from autopipeline.ui.app import render_metric_card, render_status_badge, render_health_chart


class TestRenderMetricCard:
    def test_returns_html(self):
        with patch("autopipeline.ui.app.st") as mock_st:
            mock_st.markdown.return_value = None
            render_metric_card("42", "Issues Found")
            call_args = mock_st.markdown.call_args[0][0]
            assert "42" in call_args
            assert "Issues Found" in call_args

    def test_with_delta(self):
        with patch("autopipeline.ui.app.st") as mock_st:
            mock_st.markdown.return_value = None
            render_metric_card("10", "Healed", "+5 today")
            call_args = mock_st.markdown.call_args[0][0]
            assert "+5 today" in call_args


class TestRenderStatusBadge:
    def test_healthy(self):
        badge = render_status_badge("healthy")
        assert "status-success" in badge
        assert "Healthy" in badge

    def test_warning(self):
        badge = render_status_badge("warning")
        assert "status-warning" in badge
        assert "Warning" in badge

    def test_critical(self):
        badge = render_status_badge("critical")
        assert "status-danger" in badge
        assert "Critical" in badge


class TestRenderHealthChart:
    def test_returns_figure(self):
        fig = render_health_chart(100, 5, 2)
        assert fig is not None
        assert len(fig.data) == 1

    def test_zero_values(self):
        fig = render_health_chart(0, 0, 0)
        assert fig is not None
