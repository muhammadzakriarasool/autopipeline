"""Tests for AutoPilot Streamlit UI."""
from unittest.mock import patch

from autopipeline.ui.styles import PREMIUM_CSS
from autopipeline.ui.pages.dashboard import _kpi, _donut, _area_chart


class TestStyles:
    def test_premium_css_has_foundation(self):
        assert ".stApp" in PREMIUM_CSS
        assert "--bg-primary" in PREMIUM_CSS
        assert "backdrop-filter" in PREMIUM_CSS

    def test_premium_css_has_animations(self):
        assert "@keyframes fadeInUp" in PREMIUM_CSS
        assert "@keyframes statusPulse" in PREMIUM_CSS

    def test_premium_css_has_glass(self):
        assert "glass-card" in PREMIUM_CSS
        assert "backdrop-filter: blur" in PREMIUM_CSS


class TestDashboardKpi:
    def test_renders_value(self):
        with patch("autopipeline.ui.pages.dashboard.st") as m:
            m.markdown.return_value = None
            _kpi("42", "Issues")
            html = m.markdown.call_args[0][0]
            assert "42" in html
            assert "Issues" in html

    def test_with_change(self):
        with patch("autopipeline.ui.pages.dashboard.st") as m:
            m.markdown.return_value = None
            _kpi("10", "Healed", "+5")
            html = m.markdown.call_args[0][0]
            assert "+5" in html
            assert "positive" in html

    def test_with_delay(self):
        with patch("autopipeline.ui.pages.dashboard.st") as m:
            m.markdown.return_value = None
            _kpi("1", "Test", delay=3)
            html = m.markdown.call_args[0][0]
            assert "delay-3" in html


class TestDonut:
    def test_returns_figure(self):
        fig = _donut(100, 5, 2)
        assert fig is not None
        assert len(fig.data) == 1

    def test_zero_values(self):
        fig = _donut(0, 0, 0)
        assert fig is not None


class TestAreaChart:
    def test_returns_figure(self):
        history = [{"timestamp": "2026-07-17T12:00:00", "issues_found": 3}]
        fig = _area_chart(history)
        assert fig is not None

    def test_empty(self):
        assert _area_chart([]) is None
