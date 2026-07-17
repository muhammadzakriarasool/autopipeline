"""Tests for AutoPilot Streamlit UI."""
from unittest.mock import patch

from autopipeline.ui.styles import DARK_THEME
from autopipeline.ui.pages.dashboard import _kpi_card, _health_chart, _timeline_chart


class TestStyles:
    def test_dark_theme_has_css(self):
        assert ".stApp" in DARK_THEME
        assert "--bg:" in DARK_THEME
        assert "@keyframes" in DARK_THEME
        assert "Inter" in DARK_THEME


class TestDashboardKpiCard:
    def test_renders_value(self):
        with patch("autopipeline.ui.pages.dashboard.st") as mock_st:
            mock_st.markdown.return_value = None
            _kpi_card("42", "Issues")
            call_args = mock_st.markdown.call_args[0][0]
            assert "42" in call_args
            assert "Issues" in call_args

    def test_with_delta(self):
        with patch("autopipeline.ui.pages.dashboard.st") as mock_st:
            mock_st.markdown.return_value = None
            _kpi_card("10", "Healed", "+5")
            call_args = mock_st.markdown.call_args[0][0]
            assert "+5" in call_args

    def test_with_delay(self):
        with patch("autopipeline.ui.pages.dashboard.st") as mock_st:
            mock_st.markdown.return_value = None
            _kpi_card("1", "Test", delay=2)
            call_args = mock_st.markdown.call_args[0][0]
            assert "animate-in-delay-2" in call_args


class TestHealthChart:
    def test_returns_figure(self):
        fig = _health_chart(100, 5, 2)
        assert fig is not None
        assert len(fig.data) == 1

    def test_zero_values(self):
        fig = _health_chart(0, 0, 0)
        assert fig is not None


class TestTimelineChart:
    def test_returns_figure(self):
        history = [{"timestamp": "2026-07-17T12:00:00", "issues_found": 3}]
        fig = _timeline_chart(history)
        assert fig is not None

    def test_empty_history(self):
        result = _timeline_chart([])
        assert result is None

    def test_multiple_points(self):
        history = [
            {"timestamp": "2026-07-17T12:00:00", "issues_found": 3},
            {"timestamp": "2026-07-17T13:00:00", "issues_found": 1},
            {"timestamp": "2026-07-17T14:00:00", "issues_found": 5},
        ]
        fig = _timeline_chart(history)
        assert fig is not None
        assert len(fig.data[0].x) == 3
