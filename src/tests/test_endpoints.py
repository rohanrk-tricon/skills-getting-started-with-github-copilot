"""
Test suite for the High School Activities Management System API

This module contains comprehensive tests for all API endpoints using the
Arrange-Act-Assert (AAA) pattern to ensure clear test structure.

Tests cover:
- GET /activities: Verify activities retrieval
- GET /: Verify redirect to static index
- POST /activities/{activity_name}/signup: Verify activity signup functionality
- DELETE /activities/{activity_name}/participants/{email}: Verify participant removal
"""

import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app


class TestGetActivities:
    """
    Test suite for GET /activities endpoint.
    
    Tests that the endpoint returns all available activities with proper structure.
    """
    
    @pytest.mark.asyncio
    async def test_get_activities_returns_all_activities(self):
        """
        Test that GET /activities returns all 9 pre-configured activities.
        
        Arrange: Set up the test client
        Act: Make GET request to /activities
        Assert: Verify status code and number of activities returned
        """
        # Arrange
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.get("/activities")
            
            # Assert
            assert response.status_code == 200
            activities = response.json()
            assert len(activities) == 9
            assert "Chess Club" in activities
            assert "Programming Class" in activities
            assert "Gym Class" in activities

    @pytest.mark.asyncio
    async def test_get_activities_returns_activity_structure(self):
        """
        Test that each activity has the correct structure.
        
        Arrange: Set up the test client
        Act: Make GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.get("/activities")
            activities = response.json()
            
            # Assert
            for activity_name, activity_data in activities.items():
                assert isinstance(activity_name, str)
                assert "description" in activity_data
                assert "schedule" in activity_data
                assert "max_participants" in activity_data
                assert "participants" in activity_data
                assert isinstance(activity_data["participants"], list)

    @pytest.mark.asyncio
    async def test_get_activities_participants_list(self):
        """
        Test that participants are returned as a list of emails.
        
        Arrange: Set up the test client
        Act: Make GET request to /activities
        Assert: Verify participants contain expected emails
        """
        # Arrange
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.get("/activities")
            activities = response.json()
            chess_club = activities["Chess Club"]
            
            # Assert
            assert "michael@mergington.edu" in chess_club["participants"]
            assert "daniel@mergington.edu" in chess_club["participants"]


class TestRootRedirect:
    """
    Test suite for GET / endpoint.
    
    Tests that the root endpoint redirects to the static index page.
    """
    
    @pytest.mark.asyncio
    async def test_root_redirects_to_static_index(self):
        """
        Test that GET / redirects to /static/index.html.
        
        Arrange: Set up the test client with follow_redirects=False to capture redirect
        Act: Make GET request to /
        Assert: Verify redirect status code and location header
        """
        # Arrange
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.get("/", follow_redirects=False)
            
            # Assert
            assert response.status_code == 307
            assert "/static/index.html" in response.headers["location"]


class TestSignupForActivity:
    """
    Test suite for POST /activities/{activity_name}/signup endpoint.
    
    Tests signup functionality including success cases and error scenarios.
    """
    
    @pytest.mark.asyncio
    async def test_signup_new_participant_success(self):
        """
        Test that a new participant can successfully sign up for an activity.
        
        Arrange: Create test data with a new email and existing activity
        Act: Make POST request with activity name and email
        Assert: Verify response status and participant added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "neustudent@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": new_email}
            )
            
            # Assert
            assert response.status_code == 200
            
            # Verify participant was added
            activities_response = await client.get("/activities")
            activities = activities_response.json()
            assert new_email in activities[activity_name]["participants"]

    @pytest.mark.asyncio
    async def test_signup_activity_not_found(self):
        """
        Test that signup fails with 404 when activity doesn't exist.
        
        Arrange: Create test data with non-existent activity name
        Act: Make POST request to non-existent activity
        Assert: Verify 404 status code and error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            
            # Assert
            assert response.status_code == 404
            assert "Activity not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_signup_already_signed_up(self):
        """
        Test that signup fails with 400 when student is already signed up.
        
        Arrange: Create test data with existing participant
        Act: Try to sign up the same participant again
        Assert: Verify 400 status code and error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": existing_email}
            )
            
            # Assert
            assert response.status_code == 400
            assert "already signed up" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_signup_multiple_participants(self):
        """
        Test that multiple different participants can sign up for the same activity.
        
        Arrange: Create test data with multiple different emails
        Act: Sign up multiple participants sequentially
        Assert: Verify all participants are in the activity
        """
        # Arrange
        activity_name = "Programming Class"
        email1 = "testuser1@mergington.edu"
        email2 = "testuser2@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act - Sign up first participant
            response1 = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email1}
            )
            
            # Act - Sign up second participant
            response2 = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email2}
            )
            
            # Assert both signups successful
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Verify both are in participants list
            activities_response = await client.get("/activities")
            activities = activities_response.json()
            assert email1 in activities[activity_name]["participants"]
            assert email2 in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """
    Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint.
    
    Tests participant removal functionality including success cases and error scenarios.
    """
    
    @pytest.mark.asyncio
    async def test_remove_participant_success(self):
        """
        Test that a participant can be successfully removed from an activity.
        
        Arrange: Create test data with activity and participant
        Act: Make DELETE request with activity name and email
        Assert: Verify response status and participant removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.delete(
                f"/activities/{activity_name}/participants/{email_to_remove}"
            )
            
            # Assert
            assert response.status_code == 200
            
            # Verify participant was removed
            activities_response = await client.get("/activities")
            activities = activities_response.json()
            assert email_to_remove not in activities[activity_name]["participants"]

    @pytest.mark.asyncio
    async def test_remove_participant_activity_not_found(self):
        """
        Test that removal fails with 404 when activity doesn't exist.
        
        Arrange: Create test data with non-existent activity name
        Act: Make DELETE request to non-existent activity
        Assert: Verify 404 status code
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            
            # Assert
            assert response.status_code == 404
            assert "Activity not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_remove_participant_not_found(self):
        """
        Test that removal fails with 404 when participant is not in the activity.
        
        Arrange: Create test data with existing activity and non-participant email
        Act: Try to remove email that's not a participant
        Assert: Verify 404 status code
        """
        # Arrange
        activity_name = "Chess Club"
        non_participant_email = "notinactivity@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act
            response = await client.delete(
                f"/activities/{activity_name}/participants/{non_participant_email}"
            )
            
            # Assert
            assert response.status_code == 404
            assert "Participant not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_remove_then_readd_participant(self):
        """
        Test that a participant can re-sign up after being removed.
        
        Arrange: Create test data with activity and participant
        Act: Remove participant, then sign them up again
        Assert: Verify participant can be added again after removal
        """
        # Arrange
        activity_name = "Gym Class"
        email = "testuser@mergington.edu"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Act - First signup
            signup_response = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert signup_response.status_code == 200
            
            # Act - Remove participant
            remove_response = await client.delete(
                f"/activities/{activity_name}/participants/{email}"
            )
            assert remove_response.status_code == 200
            
            # Act - Re-add participant
            readd_response = await client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            
            # Assert
            assert readd_response.status_code == 200
            
            # Verify participant is back
            activities_response = await client.get("/activities")
            activities = activities_response.json()
            assert email in activities[activity_name]["participants"]
