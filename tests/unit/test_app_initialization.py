"""
Unit tests for app initialization and basic functionality
"""

import pytest
from src.app import app


class TestAppInitialization:
    """Test that the FastAPI app initializes correctly"""

    def test_app_is_created(self):
        """Verify that the FastAPI app object is created"""
        assert app is not None

    def test_app_has_title(self):
        """Verify that the app has the correct title"""
        assert app.title == "Mergington High School API"

    def test_app_has_description(self):
        """Verify that the app has a description"""
        assert app.description == "API for viewing and signing up for extracurricular activities"

    def test_app_has_routes(self):
        """Verify that the app has at least the required routes"""
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/activities" in routes
        assert "/activities/{activity_name}/signup" in routes
        assert "/activities/{activity_name}/participants" in routes
