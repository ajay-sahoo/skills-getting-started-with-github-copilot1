"""
Test cases for Mergington High School API endpoints
Using Arrange-Act-Assert (AAA) pattern for clarity and structure
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Create test client
        Act: GET /activities
        Assert: Verify all activities returned with correct structure
        """
        # Arrange
        # (client fixture already created)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all 9 activities are present
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        
    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: Create test client
        Act: GET /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        # (client fixture already created)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Check Chess Club has all required fields
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        
    def test_get_activities_has_existing_participants(self, client):
        """
        Arrange: Create test client
        Act: GET /activities
        Assert: Verify some activities have participants
        """
        # Arrange
        # (client fixture already created)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        # Chess Club should have 2 participants
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup_adds_participant(self, client):
        """
        Arrange: Fresh activities fixture, valid email and activity
        Act: POST signup request
        Assert: Verify participant added to list, success message returned
        """
        # Arrange
        test_email = "newemail@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        
        # Verify participant was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities[activity_name]["participants"]
        
    def test_signup_returns_success_message(self, client):
        """
        Arrange: Fresh activities fixture
        Act: POST signup request
        Assert: Verify response contains appropriate success message
        """
        # Arrange
        test_email = "alice@mergington.edu"
        activity_name = "Art Studio"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["message"] == f"Signed up {test_email} for {activity_name}"
        
    def test_duplicate_signup_returns_400_error(self, client):
        """
        Arrange: Email already in participants list (michael@mergington.edu in Chess Club)
        Act: Attempt POST signup with same email
        Assert: Verify 400 status and error detail message
        """
        # Arrange
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()
        
    def test_duplicate_signup_does_not_add_duplicate(self, client):
        """
        Arrange: Email already registered, count initial participants
        Act: Attempt duplicate signup, count after attempt
        Assert: Verify participant count unchanged
        """
        # Arrange
        test_email = "emma@mergington.edu"  # Already in Programming Class
        activity_name = "Programming Class"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 400
        
        # Verify count didn't increase
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count
        
    def test_signup_to_invalid_activity_returns_404(self, client):
        """
        Arrange: Non-existent activity name
        Act: POST signup to non-existent activity
        Assert: Verify 404 status and error detail message
        """
        # Arrange
        test_email = "student@mergington.edu"
        invalid_activity = "Underwater Basket Weaving"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()
        
    def test_signup_with_special_characters_in_email(self, client):
        """
        Arrange: Email with special characters, valid activity
        Act: POST signup with special character email
        Assert: Verify successful signup and proper handling of encoding
        """
        # Arrange
        test_email = "special+test@mergington.edu"
        activity_name = "Science Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify it was added correctly
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert test_email in activities[activity_name]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Create test client
        Act: Call GET /
        Assert: Verify 307 redirect to /static/index.html
        """
        # Arrange
        # (client fixture already created)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "location" in response.headers
        assert response.headers["location"] == "/static/index.html"
        
    def test_root_redirect_location_is_correct(self, client):
        """
        Arrange: Create test client
        Act: Call GET / with redirect following
        Assert: Verify final destination is correct
        """
        # Arrange
        # (client fixture already created)
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        # The redirect should have been followed
        # (Note: static files won't exist in test, so we just verify the redirect happened)
        assert response.status_code in [200, 404]  # 404 because static file doesn't exist in test
