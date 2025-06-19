#!/usr/bin/env python3
"""
StarGuide AI Mentor - Backend API Test Suite
This script tests all the backend API endpoints to ensure they are working correctly.
"""

import requests
import json
import time
import random
import string
from datetime import datetime
import sys

# Backend URL from frontend .env
BACKEND_URL = "https://e91b54c6-bec2-4ded-a41c-137fdc639c72.preview.emergentagent.com"
API_BASE_URL = f"{BACKEND_URL}/api/v1"

# Test user credentials
TEST_USER = {
    "email": f"test.user.{int(time.time())}@example.com",
    "username": f"testuser{int(time.time())}",
    "full_name": "Test User",
    "password": "TestPassword123!",
    "role": "student",
    "grade_level": "10th Grade",
    "school": "Test High School"
}

# Global variables to store test data
access_token = None
refresh_token = None
user_id = None
conversation_id = None
study_group_id = None
study_group_code = None
session_id = None
quiz_room_id = None
quiz_room_code = None

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 80}")

def print_response(response):
    """Print formatted response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_health_check():
    """Test the health check endpoint"""
    print_test_header("Health Check")
    
    response = requests.get(f"{BACKEND_URL}/health")
    print_response(response)
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    return True

def test_register():
    """Test user registration"""
    print_test_header("User Registration")
    
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json=TEST_USER
    )
    print_response(response)
    
    assert response.status_code == 201
    assert response.json()["email"] == TEST_USER["email"]
    assert response.json()["username"] == TEST_USER["username"]
    
    global user_id
    user_id = response.json()["id"]
    
    return True

def test_login():
    """Test user login"""
    print_test_header("User Login")
    
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    
    global access_token, refresh_token
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    
    return True

def test_get_current_user():
    """Test getting current user info"""
    print_test_header("Get Current User")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/auth/me",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert response.json()["email"] == TEST_USER["email"]
    assert response.json()["username"] == TEST_USER["username"]
    
    return True

def test_refresh_token():
    """Test refreshing access token"""
    print_test_header("Refresh Token")
    
    response = requests.post(
        f"{API_BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    global access_token
    access_token = response.json()["access_token"]
    
    return True

def test_ai_models():
    """Test getting available AI models"""
    print_test_header("Get AI Models")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/ai/models",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    return True

def test_ai_chat():
    """Test AI chat functionality"""
    print_test_header("AI Chat")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test with OpenAI
    chat_request = {
        "message": "What is the capital of France?",
        "model": "openai_gpt4",
        "subject": "Geography",
        "topic": "European Capitals",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    response = requests.post(
        f"{API_BASE_URL}/ai/chat",
        json=chat_request,
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "response" in response.json()
    assert "conversation_id" in response.json()
    
    global conversation_id
    conversation_id = response.json()["conversation_id"]
    
    # Test with existing conversation
    chat_request = {
        "message": "Tell me more about Paris.",
        "conversation_id": conversation_id,
        "model": "openai_gpt4"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/ai/chat",
        json=chat_request,
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "response" in response.json()
    
    # Test with Claude
    chat_request = {
        "message": "What is the capital of Germany?",
        "model": "claude_3_sonnet",
        "subject": "Geography",
        "topic": "European Capitals"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/ai/chat",
        json=chat_request,
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "response" in response.json()
    
    # Test with Gemini
    chat_request = {
        "message": "What is the capital of Italy?",
        "model": "gemini_pro",
        "subject": "Geography",
        "topic": "European Capitals"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/ai/chat",
        json=chat_request,
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "response" in response.json()
    
    return True

def test_get_conversations():
    """Test getting user conversations"""
    print_test_header("Get Conversations")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/ai/conversations",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    return True

def test_get_conversation():
    """Test getting a specific conversation"""
    print_test_header("Get Specific Conversation")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/ai/conversation/{conversation_id}",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert response.json()["id"] == conversation_id
    
    return True

def test_rate_message():
    """Test rating an AI message"""
    print_test_header("Rate Message")
    
    # First get the message ID
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/ai/conversation/{conversation_id}",
        headers=headers
    )
    
    messages = response.json()["messages"]
    ai_message = next((m for m in messages if m["role"] == "assistant"), None)
    
    if ai_message:
        message_id = ai_message["id"]
        
        response = requests.post(
            f"{API_BASE_URL}/ai/rate-message",
            json={"message_id": message_id, "rating": 5},
            headers=headers
        )
        print_response(response)
        
        assert response.status_code == 200
        assert "message" in response.json()
        
        return True
    else:
        print("No AI message found to rate")
        return False

def test_start_learning_session():
    """Test starting a learning session"""
    print_test_header("Start Learning Session")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    session_data = {
        "session_type": "practice",
        "subject": "Mathematics",
        "topic": "Algebra",
        "difficulty": "beginner",
        "question_count": 5
    }
    
    response = requests.post(
        f"{API_BASE_URL}/learning/start-session",
        json=session_data,
        headers=headers
    )
    print_response(response)
    
    # This might fail if no questions are in the database
    if response.status_code == 200:
        assert "session_id" in response.json()
        assert "questions" in response.json()
        
        global session_id
        session_id = response.json()["session_id"]
        
        return True
    else:
        print("Warning: Could not start learning session. This might be due to missing questions in the database.")
        return False

def test_submit_answer():
    """Test submitting an answer"""
    print_test_header("Submit Answer")
    
    if not session_id:
        print("Skipping test_submit_answer as no session_id is available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get questions from session
    response = requests.post(
        f"{API_BASE_URL}/learning/start-session",
        json={
            "session_type": "practice",
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "beginner",
            "question_count": 1
        },
        headers=headers
    )
    
    if response.status_code == 200 and "questions" in response.json() and len(response.json()["questions"]) > 0:
        question = response.json()["questions"][0]
        session_id = response.json()["session_id"]
        
        submission = {
            "question_id": question["id"],
            "user_answer": question["answer_options"][0]["id"] if question["question_type"] == "multiple_choice" else "42",
            "time_taken_seconds": 30,
            "hints_used": 0,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/learning/submit-answer",
            json=submission,
            headers=headers
        )
        print_response(response)
        
        assert response.status_code == 200
        assert "is_correct" in response.json()
        
        return True
    else:
        print("Warning: Could not submit answer. This might be due to missing questions in the database.")
        return False

def test_daily_challenge():
    """Test getting daily challenge"""
    print_test_header("Daily Challenge")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/learning/daily-challenge",
        headers=headers
    )
    print_response(response)
    
    # This might fail if no daily challenge is set up
    if response.status_code == 200:
        assert "challenge_id" in response.json()
        assert "questions" in response.json()
        return True
    else:
        print("Warning: Could not get daily challenge. This might be due to missing setup.")
        return False

def test_create_study_group():
    """Test creating a study group"""
    print_test_header("Create Study Group")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    group_data = {
        "name": f"Test Study Group {int(time.time())}",
        "description": "A test study group for API testing",
        "subject": "Computer Science",
        "group_type": "public",
        "grade_level": "10th Grade",
        "max_members": 20
    }
    
    response = requests.post(
        f"{API_BASE_URL}/groups/create",
        json=group_data,
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert response.json()["name"] == group_data["name"]
    assert "join_code" in response.json()
    
    global study_group_id, study_group_code
    study_group_id = response.json()["id"]
    study_group_code = response.json()["join_code"]
    
    return True

def test_get_my_groups():
    """Test getting user's study groups"""
    print_test_header("Get My Groups")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/groups/my-groups",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    
    return True

def test_discover_groups():
    """Test discovering public study groups"""
    print_test_header("Discover Groups")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/groups/discover",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    return True

def test_get_group_details():
    """Test getting group details"""
    print_test_header("Get Group Details")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/groups/{study_group_id}",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert response.json()["id"] == study_group_id
    
    return True

def test_create_quiz_room():
    """Test creating a quiz room"""
    print_test_header("Create Quiz Room")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    quiz_data = {
        "title": f"Test Quiz {int(time.time())}",
        "description": "A test quiz for API testing",
        "subject": "Science",
        "difficulty": "beginner",
        "question_count": 5,
        "time_limit_minutes": 10,
        "max_participants": 10
    }
    
    response = requests.post(
        f"{API_BASE_URL}/quizzes/create-room",
        json=quiz_data,
        headers=headers
    )
    print_response(response)
    
    # This might fail if no questions are in the database
    if response.status_code == 200:
        assert "room_id" in response.json()
        assert "room_code" in response.json()
        
        global quiz_room_id, quiz_room_code
        quiz_room_id = response.json()["room_id"]
        quiz_room_code = response.json()["room_code"]
        
        return True
    else:
        print("Warning: Could not create quiz room. This might be due to missing questions in the database.")
        return False

def test_get_active_quiz_rooms():
    """Test getting active quiz rooms"""
    print_test_header("Get Active Quiz Rooms")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/quizzes/active-rooms",
        headers=headers
    )
    print_response(response)
    
    assert response.status_code == 200
    assert "active_rooms" in response.json()
    
    return True

def test_join_quiz_room():
    """Test joining a quiz room"""
    print_test_header("Join Quiz Room")
    
    if not quiz_room_code:
        print("Skipping test_join_quiz_room as no quiz_room_code is available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    join_data = {
        "room_code": quiz_room_code
    }
    
    response = requests.post(
        f"{API_BASE_URL}/quizzes/join-room",
        json=join_data,
        headers=headers
    )
    print_response(response)
    
    # This might fail if the room is already started or ended
    if response.status_code == 200:
        assert "room_id" in response.json()
        assert "message" in response.json()
        return True
    else:
        print("Warning: Could not join quiz room. This might be due to room state.")
        return False

def test_get_analytics_dashboard():
    """Test getting analytics dashboard"""
    print_test_header("Get Analytics Dashboard")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/analytics/dashboard",
        headers=headers
    )
    print_response(response)
    
    # This might return 404 if the endpoint is not implemented
    if response.status_code == 200:
        return True
    else:
        print("Warning: Analytics dashboard endpoint might not be implemented.")
        return False

def test_get_user_profile():
    """Test getting user profile"""
    print_test_header("Get User Profile")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{API_BASE_URL}/users/profile",
        headers=headers
    )
    print_response(response)
    
    # This might return 404 if the endpoint is not implemented
    if response.status_code == 200:
        assert response.json()["email"] == TEST_USER["email"]
        return True
    else:
        print("Warning: User profile endpoint might not be implemented.")
        return False

def run_all_tests():
    """Run all tests and report results"""
    test_results = {}
    
    # Health check
    test_results["Health Check"] = test_health_check()
    
    # Authentication
    test_results["User Registration"] = test_register()
    test_results["User Login"] = test_login()
    test_results["Get Current User"] = test_get_current_user()
    test_results["Refresh Token"] = test_refresh_token()
    
    # AI
    test_results["Get AI Models"] = test_ai_models()
    test_results["AI Chat"] = test_ai_chat()
    test_results["Get Conversations"] = test_get_conversations()
    test_results["Get Specific Conversation"] = test_get_conversation()
    test_results["Rate Message"] = test_rate_message()
    
    # Learning
    test_results["Start Learning Session"] = test_start_learning_session()
    test_results["Submit Answer"] = test_submit_answer()
    test_results["Daily Challenge"] = test_daily_challenge()
    
    # Groups
    test_results["Create Study Group"] = test_create_study_group()
    test_results["Get My Groups"] = test_get_my_groups()
    test_results["Discover Groups"] = test_discover_groups()
    test_results["Get Group Details"] = test_get_group_details()
    
    # Quizzes
    test_results["Create Quiz Room"] = test_create_quiz_room()
    test_results["Get Active Quiz Rooms"] = test_get_active_quiz_rooms()
    test_results["Join Quiz Room"] = test_join_quiz_room()
    
    # Analytics & User
    test_results["Get Analytics Dashboard"] = test_get_analytics_dashboard()
    test_results["Get User Profile"] = test_get_user_profile()
    
    # Print summary
    print("\n\n")
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n")
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed / len(test_results) * 100:.2f}%")
    
    return passed, failed, test_results

if __name__ == "__main__":
    passed, failed, results = run_all_tests()
    sys.exit(1 if failed > 0 else 0)