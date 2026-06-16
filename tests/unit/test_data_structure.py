"""
Unit tests for data structure validation
"""

import pytest
from src.app import activities


class TestDataStructure:
    """Test that the activities data structure is valid"""

    def test_activities_is_dict(self):
        """Verify that activities is a dictionary"""
        assert isinstance(activities, dict)

    def test_activities_not_empty(self):
        """Verify that activities dictionary is not empty"""
        assert len(activities) > 0

    def test_activity_has_required_fields(self):
        """Verify each activity has the required fields"""
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity in activities.items():
            assert isinstance(activity, dict), f"Activity '{activity_name}' is not a dict"
            assert required_fields.issubset(activity.keys()), \
                f"Activity '{activity_name}' missing required fields"

    def test_activity_field_types(self):
        """Verify that activity fields have correct types"""
        for activity_name, activity in activities.items():
            assert isinstance(activity["description"], str), \
                f"Activity '{activity_name}' description must be a string"
            assert isinstance(activity["schedule"], str), \
                f"Activity '{activity_name}' schedule must be a string"
            assert isinstance(activity["max_participants"], int), \
                f"Activity '{activity_name}' max_participants must be an integer"
            assert activity["max_participants"] > 0, \
                f"Activity '{activity_name}' max_participants must be positive"
            assert isinstance(activity["participants"], list), \
                f"Activity '{activity_name}' participants must be a list"

    def test_participants_are_strings(self):
        """Verify that all participants are email addresses (strings)"""
        for activity_name, activity in activities.items():
            for participant in activity["participants"]:
                assert isinstance(participant, str), \
                    f"Participant in '{activity_name}' is not a string"
                assert "@" in participant, \
                    f"Participant '{participant}' in '{activity_name}' is not a valid email"

    def test_participants_within_max_limit(self):
        """Verify that no activity has more participants than max_participants"""
        for activity_name, activity in activities.items():
            assert len(activity["participants"]) <= activity["max_participants"], \
                f"Activity '{activity_name}' has too many participants"

    def test_no_duplicate_participants_in_activity(self):
        """Verify that each activity has no duplicate participants"""
        for activity_name, activity in activities.items():
            participants = activity["participants"]
            assert len(participants) == len(set(participants)), \
                f"Activity '{activity_name}' has duplicate participants"
