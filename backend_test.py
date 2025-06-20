#!/usr/bin/env python3
import requests
import json
import time
import random
import string
import uuid
from datetime import datetime
import sys

# Base URL from frontend/.env
BASE_URL = "https://3d42ac3c-4273-40a1-b5a9-12f70afc90ba.preview.emergentagent.com/api"

# Test users
ADMIN_USER = {
    "username": f"admin_{uuid.uuid4().hex[:6]}",
    "email": f"admin_{uuid.uuid4().hex[:6]}@starguide.com",
    "password": "Admin@123",
    "role": "admin",
    "full_name": "Admin User"
}

TEACHER_USER = {
    "username": f"teacher_{uuid.uuid4().hex[:6]}",
    "email": f"teacher_{uuid.uuid4().hex[:6]}@starguide.com",
    "password": "Teacher@123",
    "role": "teacher",
    "full_name": "Teacher User"
}

STUDENT_USER = {
    "username": f"student_{uuid.uuid4().hex[:6]}",
    "email": f"student_{uuid.uuid4().hex[:6]}@starguide.com",
    "password": "Student@123",
    "role": "student",
    "full_name": "Student User"
}

# Test data
TEST_QUESTION = {
    "question_text": "What is the capital of France?",
    "question_type": "multiple_choice",
    "difficulty": "beginner",
    "subject": "Geography",
    "topic": "European Capitals",
    "options": ["Paris", "London", "Berlin", "Madrid"],
    "correct_answer": "Paris",
    "explanation": "Paris is the capital and most populous city of France.",
    "points": 10,
    "tags": ["geography", "europe", "capitals"]
}

TEST_STUDY_GROUP = {
    "name": f"Study Group {uuid.uuid4().hex[:6]}",
    "description": "A test study group for geography enthusiasts",
    "subject": "Geography",
    "max_members": 20,
    "is_private": False
}

TEST_QUIZ_ROOM = {
    "name": f"Quiz Room {uuid.uuid4().hex[:6]}",
    "subject": "Geography",
    "difficulty": "beginner",
    "max_participants": 10,
    "questions_per_game": 10,
    "time_per_question": 30
}

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

# Helper functions
def log_test(name, passed, details=""):
    status = "PASSED" if passed else "FAILED"
    print(f"[{status}] {name}")
    if details and not passed:
        print(f"  Details: {details}")
    
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "details": details
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def register_user(user_data):
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return None

def login_user(email, password):
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# Test functions
def test_health_check():
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        log_test("Health Check", passed, response.text if not passed else "")
        return passed
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False

def test_root_endpoint():
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200 and "StarGuide API" in response.json().get("message", "")
        log_test("Root Endpoint", passed, response.text if not passed else "")
        return passed
    except Exception as e:
        log_test("Root Endpoint", False, str(e))
        return False

def test_user_registration():
    # Test admin registration
    admin_result = register_user(ADMIN_USER)
    admin_passed = admin_result is not None and "access_token" in admin_result
    log_test("Admin Registration", admin_passed, "Failed to register admin user" if not admin_passed else "")
    
    # Test teacher registration
    teacher_result = register_user(TEACHER_USER)
    teacher_passed = teacher_result is not None and "access_token" in teacher_result
    log_test("Teacher Registration", teacher_passed, "Failed to register teacher user" if not teacher_passed else "")
    
    # Test student registration
    student_result = register_user(STUDENT_USER)
    student_passed = student_result is not None and "access_token" in student_result
    log_test("Student Registration", student_passed, "Failed to register student user" if not student_passed else "")
    
    return {
        "admin": admin_result,
        "teacher": teacher_result,
        "student": student_result
    }

def test_user_login(users):
    login_results = {}
    
    # Test admin login
    if users.get("admin"):
        admin_login = login_user(ADMIN_USER["email"], ADMIN_USER["password"])
        admin_passed = admin_login is not None and "access_token" in admin_login
        log_test("Admin Login", admin_passed, "Failed to login as admin" if not admin_passed else "")
        login_results["admin"] = admin_login
    
    # Test teacher login
    if users.get("teacher"):
        teacher_login = login_user(TEACHER_USER["email"], TEACHER_USER["password"])
        teacher_passed = teacher_login is not None and "access_token" in teacher_login
        log_test("Teacher Login", teacher_passed, "Failed to login as teacher" if not teacher_passed else "")
        login_results["teacher"] = teacher_login
    
    # Test student login
    if users.get("student"):
        student_login = login_user(STUDENT_USER["email"], STUDENT_USER["password"])
        student_passed = student_login is not None and "access_token" in student_login
        log_test("Student Login", student_passed, "Failed to login as student" if not student_passed else "")
        login_results["student"] = student_login
    
    return login_results

def test_current_user(login_results):
    for role, login_data in login_results.items():
        if login_data and "access_token" in login_data:
            try:
                headers = get_auth_header(login_data["access_token"])
                response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                passed = response.status_code == 200 and response.json().get("role") == role
                log_test(f"{role.capitalize()} Get Current User", passed, response.text if not passed else "")
            except Exception as e:
                log_test(f"{role.capitalize()} Get Current User", False, str(e))

def test_learning_engine(login_results):
    # Test question creation (teacher/admin only)
    created_question_id = None
    
    # Try with teacher
    if login_results.get("teacher") and "access_token" in login_results["teacher"]:
        try:
            headers = get_auth_header(login_results["teacher"]["access_token"])
            response = requests.post(f"{BASE_URL}/questions", json=TEST_QUESTION, headers=headers)
            passed = response.status_code == 200 and "id" in response.json()
            log_test("Teacher Create Question", passed, response.text if not passed else "")
            if passed:
                created_question_id = response.json()["id"]
        except Exception as e:
            log_test("Teacher Create Question", False, str(e))
    
    # Try with admin if teacher failed
    if not created_question_id and login_results.get("admin") and "access_token" in login_results["admin"]:
        try:
            headers = get_auth_header(login_results["admin"]["access_token"])
            response = requests.post(f"{BASE_URL}/questions", json=TEST_QUESTION, headers=headers)
            passed = response.status_code == 200 and "id" in response.json()
            log_test("Admin Create Question", passed, response.text if not passed else "")
            if passed:
                created_question_id = response.json()["id"]
        except Exception as e:
            log_test("Admin Create Question", False, str(e))
    
    # Test question retrieval
    if login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.get(f"{BASE_URL}/questions", headers=headers)
            passed = response.status_code == 200 and isinstance(response.json(), list)
            log_test("Get Questions", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Get Questions", False, str(e))
        
        # Test question retrieval with filters
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.get(f"{BASE_URL}/questions?subject=Geography&difficulty=beginner", headers=headers)
            passed = response.status_code == 200 and isinstance(response.json(), list)
            log_test("Get Questions with Filters", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Get Questions with Filters", False, str(e))
    
    # Test answer submission
    if created_question_id and login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.post(
                f"{BASE_URL}/questions/{created_question_id}/answer?answer=Paris", 
                headers=headers
            )
            passed = response.status_code == 200 and response.json().get("correct") == True
            log_test("Submit Correct Answer", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Submit Correct Answer", False, str(e))
        
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.post(
                f"{BASE_URL}/questions/{created_question_id}/answer?answer=London", 
                headers=headers
            )
            passed = response.status_code == 200 and response.json().get("correct") == False
            log_test("Submit Incorrect Answer", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Submit Incorrect Answer", False, str(e))

def test_study_groups(login_results):
    # Test study group creation
    created_group_id = None
    
    if login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.post(f"{BASE_URL}/study-groups", json=TEST_STUDY_GROUP, headers=headers)
            passed = response.status_code == 200 and "id" in response.json()
            log_test("Create Study Group", passed, response.text if not passed else "")
            if passed:
                created_group_id = response.json()["id"]
        except Exception as e:
            log_test("Create Study Group", False, str(e))
    
    # Test study group listing
    if login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.get(f"{BASE_URL}/study-groups", headers=headers)
            passed = response.status_code == 200 and isinstance(response.json(), list)
            log_test("List Study Groups", passed, response.text if not passed else "")
        except Exception as e:
            log_test("List Study Groups", False, str(e))
    
    # Test study group joining
    if created_group_id and login_results.get("teacher") and "access_token" in login_results["teacher"]:
        try:
            headers = get_auth_header(login_results["teacher"]["access_token"])
            response = requests.post(f"{BASE_URL}/study-groups/{created_group_id}/join", headers=headers)
            passed = response.status_code == 200 and "message" in response.json()
            log_test("Join Study Group", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Join Study Group", False, str(e))

def test_quiz_arena(login_results):
    # Test quiz room creation
    created_room_code = None
    
    if login_results.get("teacher") and "access_token" in login_results["teacher"]:
        try:
            headers = get_auth_header(login_results["teacher"]["access_token"])
            response = requests.post(f"{BASE_URL}/quiz-rooms", json=TEST_QUIZ_ROOM, headers=headers)
            passed = response.status_code == 200 and "room_code" in response.json()
            log_test("Create Quiz Room", passed, response.text if not passed else "")
            if passed:
                created_room_code = response.json()["room_code"]
        except Exception as e:
            log_test("Create Quiz Room", False, str(e))
    
    # Test quiz room listing
    if login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.get(f"{BASE_URL}/quiz-rooms", headers=headers)
            passed = response.status_code == 200 and isinstance(response.json(), list)
            log_test("List Quiz Rooms", passed, response.text if not passed else "")
        except Exception as e:
            log_test("List Quiz Rooms", False, str(e))
    
    # Test quiz room joining
    if created_room_code and login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.post(f"{BASE_URL}/quiz-rooms/{created_room_code}/join", headers=headers)
            passed = response.status_code == 200 and "message" in response.json()
            log_test("Join Quiz Room", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Join Quiz Room", False, str(e))

def test_ai_tutor(login_results):
    if login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.post(
                f"{BASE_URL}/ai/chat?message=Can you explain the concept of photosynthesis?", 
                headers=headers
            )
            passed = response.status_code == 200 and "response" in response.json() and "session_id" in response.json()
            log_test("AI Tutor Chat", passed, response.text if not passed else "")
            
            # Test with session ID if first test passed
            if passed and "session_id" in response.json():
                session_id = response.json()["session_id"]
                response = requests.post(
                    f"{BASE_URL}/ai/chat?message=What are the key components needed for photosynthesis?&session_id={session_id}", 
                    headers=headers
                )
                passed = response.status_code == 200 and "response" in response.json()
                log_test("AI Tutor Chat with Session", passed, response.text if not passed else "")
        except Exception as e:
            log_test("AI Tutor Chat", False, str(e))

def test_analytics(login_results):
    if login_results.get("student") and "access_token" in login_results["student"]:
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
            passed = response.status_code == 200 and "user_stats" in response.json()
            log_test("Dashboard Analytics", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Dashboard Analytics", False, str(e))

def test_chat_system(login_results):
    # Create a room ID for testing
    room_id = str(uuid.uuid4())
    
    if login_results.get("student") and "access_token" in login_results["student"]:
        # Test sending a message
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.post(
                f"{BASE_URL}/chat/{room_id}/message?message=Hello, this is a test message!", 
                headers=headers
            )
            passed = response.status_code == 200 and "id" in response.json()
            log_test("Send Chat Message", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Send Chat Message", False, str(e))
        
        # Test retrieving messages
        try:
            headers = get_auth_header(login_results["student"]["access_token"])
            response = requests.get(f"{BASE_URL}/chat/{room_id}/messages", headers=headers)
            passed = response.status_code == 200 and isinstance(response.json(), list)
            log_test("Get Chat Messages", passed, response.text if not passed else "")
        except Exception as e:
            log_test("Get Chat Messages", False, str(e))

def test_adaptive_assessment(login_results):
    """Test the adaptive assessment functionality"""
    if not login_results.get("student") or "access_token" not in login_results["student"]:
        log_test("Adaptive Assessment - Start Session", False, "No student login available")
        return
    
    headers = get_auth_header(login_results["student"]["access_token"])
    session_id = None
    
    # 1. Start an adaptive assessment session
    try:
        assessment_config = {
            "subject": "Mathematics",
            "target_grade_level": "grade_8",
            "assessment_type": "diagnostic",
            "enable_think_aloud": True,
            "enable_ai_help_tracking": True,
            "max_questions": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/adaptive-assessment/start", 
            json=assessment_config,
            headers=headers
        )
        
        passed = (
            response.status_code == 200 and 
            "session_id" in response.json() and
            "initial_ability_estimate" in response.json()
        )
        
        log_test("Adaptive Assessment - Start Session", passed, response.text if not passed else "")
        
        if passed:
            session_id = response.json()["session_id"]
            print(f"  Created session: {session_id}")
            print(f"  Initial ability: {response.json()['initial_ability_estimate']}")
            print(f"  Estimated grade level: {response.json()['estimated_grade_level']}")
    except Exception as e:
        log_test("Adaptive Assessment - Start Session", False, str(e))
    
    if not session_id:
        log_test("Adaptive Assessment - Get Next Question", False, "No session ID available")
        return
    
    # 2. Get the first adaptive question
    question_id = None
    try:
        response = requests.get(
            f"{BASE_URL}/adaptive-assessment/{session_id}/next-question",
            headers=headers
        )
        
        passed = (
            response.status_code == 200 and
            "id" in response.json() and
            "question_text" in response.json() and
            "estimated_difficulty" in response.json()
        )
        
        log_test("Adaptive Assessment - Get Next Question", passed, response.text if not passed else "")
        
        if passed:
            question_id = response.json()["id"]
            print(f"  Question: {response.json()['question_text']}")
            print(f"  Difficulty: {response.json()['estimated_difficulty']}")
            print(f"  Current ability estimate: {response.json()['current_ability_estimate']}")
    except Exception as e:
        log_test("Adaptive Assessment - Get Next Question", False, str(e))
    
    if not question_id:
        log_test("Adaptive Assessment - Submit Answer", False, "No question ID available")
        return
    
    # 3. Submit an answer with think-aloud data
    try:
        # Create think-aloud data
        think_aloud_data = {
            "question_id": question_id,
            "reasoning": "I'm solving this by first understanding what the question is asking. I need to apply the formula for the area of a circle which is πr². Since the radius is given as 5 cm, I can calculate the area as π × 5² = π × 25 = 78.54 cm².",
            "strategy": "I'm using the formula for the area of a circle and substituting the given radius.",
            "confidence_level": 4,  # 1-5 scale
            "difficulty_perception": 2,  # 1-5 scale
            "connections_to_prior_knowledge": "This connects to my previous knowledge of geometry and the properties of circles."
        }
        
        # Submit answer
        answer_data = {
            "session_id": session_id,
            "question_id": question_id,
            "answer": "78.54",  # Assuming this is correct for testing
            "response_time_seconds": 25.5,
            "think_aloud_data": think_aloud_data,
            "ai_help_used": False
        }
        
        response = requests.post(
            f"{BASE_URL}/adaptive-assessment/submit-answer",
            json=answer_data,
            headers=headers
        )
        
        passed = (
            response.status_code == 200 and
            "correct" in response.json() and
            "points_earned" in response.json() and
            "new_ability_estimate" in response.json()
        )
        
        log_test("Adaptive Assessment - Submit Answer with Think-Aloud", passed, response.text if not passed else "")
        
        if passed:
            print(f"  Correct: {response.json()['correct']}")
            print(f"  Points earned: {response.json()['points_earned']}")
            print(f"  New ability estimate: {response.json()['new_ability_estimate']}")
            print(f"  Think-aloud quality score: {response.json()['think_aloud_quality_score']}")
    except Exception as e:
        log_test("Adaptive Assessment - Submit Answer with Think-Aloud", False, str(e))
    
    # 4. Get the next question (should adapt based on performance)
    second_question_id = None
    try:
        response = requests.get(
            f"{BASE_URL}/adaptive-assessment/{session_id}/next-question",
            headers=headers
        )
        
        passed = (
            response.status_code == 200 and
            "id" in response.json() and
            "question_text" in response.json() and
            "estimated_difficulty" in response.json()
        )
        
        # Check if difficulty adapted based on previous correct answer
        if passed and "estimated_difficulty" in response.json():
            # If previous answer was correct, difficulty should increase
            adaptation_correct = response.json()["estimated_difficulty"] > 0.5
            log_test("Adaptive Assessment - Question Difficulty Adaptation", adaptation_correct, 
                     "Question difficulty did not adapt as expected" if not adaptation_correct else "")
        
        log_test("Adaptive Assessment - Get Second Question", passed, response.text if not passed else "")
        
        if passed:
            second_question_id = response.json()["id"]
            print(f"  Second question: {response.json()['question_text']}")
            print(f"  New difficulty: {response.json()['estimated_difficulty']}")
    except Exception as e:
        log_test("Adaptive Assessment - Get Second Question", False, str(e))
    
    if not second_question_id:
        log_test("Adaptive Assessment - Submit Answer with AI Help", False, "No second question ID available")
        return
    
    # 5. Submit another answer with AI help tracking
    try:
        # Submit answer with AI help
        ai_help_details = {
            "type": "hint",
            "content": "The AI provided a hint about using the quadratic formula to solve this equation."
        }
        
        answer_data = {
            "session_id": session_id,
            "question_id": second_question_id,
            "answer": "x = 3",  # Assuming this is correct for testing
            "response_time_seconds": 45.2,
            "think_aloud_data": None,  # No think-aloud this time
            "ai_help_used": True,
            "ai_help_details": ai_help_details
        }
        
        response = requests.post(
            f"{BASE_URL}/adaptive-assessment/submit-answer",
            json=answer_data,
            headers=headers
        )
        
        passed = (
            response.status_code == 200 and
            "correct" in response.json() and
            "ai_help_impact" in response.json()
        )
        
        log_test("Adaptive Assessment - Submit Answer with AI Help", passed, response.text if not passed else "")
        
        if passed:
            print(f"  Correct: {response.json()['correct']}")
            print(f"  Points earned: {response.json()['points_earned']}")
            print(f"  AI help impact: {response.json()['ai_help_impact']}")
    except Exception as e:
        log_test("Adaptive Assessment - Submit Answer with AI Help", False, str(e))
    
    # 6. Get session analytics
    try:
        response = requests.get(
            f"{BASE_URL}/adaptive-assessment/{session_id}/analytics",
            headers=headers
        )
        
        passed = (
            response.status_code == 200 and
            "accuracy" in response.json() and
            "final_ability_estimate" in response.json() and
            "estimated_grade_level" in response.json() and
            "ai_help_percentage" in response.json() and
            "recommendations" in response.json()
        )
        
        log_test("Adaptive Assessment - Session Analytics", passed, response.text if not passed else "")
        
        if passed:
            print(f"  Accuracy: {response.json()['accuracy']}")
            print(f"  Final ability estimate: {response.json()['final_ability_estimate']}")
            print(f"  Estimated grade level: {response.json()['estimated_grade_level']}")
            print(f"  AI help percentage: {response.json()['ai_help_percentage']}")
            print(f"  Recommendations: {response.json()['recommendations']}")
    except Exception as e:
        log_test("Adaptive Assessment - Session Analytics", False, str(e))

def run_all_tests():
    print("Starting StarGuide API Tests...")
    print("=" * 50)
    
    # Test basic endpoints
    test_health_check()
    test_root_endpoint()
    
    # Test authentication
    users = test_user_registration()
    login_results = test_user_login(users)
    test_current_user(login_results)
    
    # Test learning engine
    test_learning_engine(login_results)
    
    # Test study groups
    test_study_groups(login_results)
    
    # Test quiz arena
    test_quiz_arena(login_results)
    
    # Test AI tutor
    test_ai_tutor(login_results)
    
    # Test analytics
    test_analytics(login_results)
    
    # Test chat system
    test_chat_system(login_results)
    
    # Test adaptive assessment
    test_adaptive_assessment(login_results)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Test Summary: {test_results['passed']} passed, {test_results['failed']} failed")
    print("=" * 50)
    
    return test_results

if __name__ == "__main__":
    run_all_tests()