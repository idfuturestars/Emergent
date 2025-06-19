#!/usr/bin/env python3
"""
Debug script for IDFS StarGuide API endpoints
This script specifically tests the Study Groups and Assessments endpoints that are returning 500 errors.
"""

import requests
import json
import os
import random
import string
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint

# Load environment variables from frontend/.env to get the backend URL
frontend_env_path = Path('/app/frontend/.env')
load_dotenv(frontend_env_path)

# Backend API URL
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")

API_URL = f"{BACKEND_URL}/api"
print(f"Using backend API URL: {API_URL}")

# Test user credentials
TEST_USER = {
    'username': f"debug_user_{random.randint(1000, 9999)}",
    'email': f"debug_user_{random.randint(1000, 9999)}@test.com",
    'password': ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
    'role': 'student',
    'token': None,
    'id': None
}

def setup_test_user():
    """Register and login test user"""
    print("\n=== Setting up test user ===")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                'username': TEST_USER['username'],
                'email': TEST_USER['email'],
                'password': TEST_USER['password'],
                'role': TEST_USER['role'],
                'full_name': "Debug User"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            TEST_USER['token'] = data['token']
            TEST_USER['id'] = data['user']['id']
            print(f"Successfully registered test user with ID: {TEST_USER['id']}")
        elif response.status_code == 400 and "User already exists" in response.text:
            # User exists, try logging in
            login_response = requests.post(
                f"{API_URL}/auth/login",
                json={
                    'email': TEST_USER['email'],
                    'password': TEST_USER['password']
                }
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                TEST_USER['token'] = data['token']
                TEST_USER['id'] = data['user']['id']
                print(f"Successfully logged in existing test user with ID: {TEST_USER['id']}")
            else:
                print(f"Failed to login existing test user: {login_response.text}")
        else:
            print(f"Failed to register test user: {response.text}")
    except Exception as e:
        print(f"Error setting up test user: {str(e)}")
    
    return TEST_USER['token'] is not None

def debug_study_groups_endpoint():
    """Debug the study groups endpoint"""
    print("\n=== Debugging Study Groups Endpoint ===")
    
    if not TEST_USER['token']:
        print("No test user token available")
        return False
    
    # First, try to create a study group
    print("Creating a test study group...")
    group_data = {
        'name': 'Debug Study Group',
        'description': 'A test study group for debugging',
        'subject': 'Computer Science',
        'max_members': 5,
        'is_public': True
    }
    
    try:
        create_response = requests.post(
            f"{API_URL}/groups",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"},
            json=group_data
        )
        
        if create_response.status_code == 200:
            print("✅ Successfully created study group")
            group = create_response.json().get('group')
            print(f"Group ID: {group['id']}")
        else:
            print(f"❌ Failed to create study group: {create_response.status_code}")
            print(f"Response: {create_response.text}")
    except Exception as e:
        print(f"❌ Exception creating study group: {str(e)}")
    
    # Now try to get study groups
    print("\nGetting study groups...")
    try:
        get_response = requests.get(
            f"{API_URL}/groups",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"}
        )
        
        if get_response.status_code == 200:
            data = get_response.json()
            print(f"✅ Successfully retrieved {len(data.get('groups', []))} study groups")
            if data.get('groups'):
                print("First group details:")
                pprint(data['groups'][0])
        else:
            print(f"❌ Failed to get study groups: {get_response.status_code}")
            print(f"Response: {get_response.text}")
    except Exception as e:
        print(f"❌ Exception getting study groups: {str(e)}")
    
    return True

def debug_assessments_endpoint():
    """Debug the assessments endpoint"""
    print("\n=== Debugging Assessments Endpoint ===")
    
    if not TEST_USER['token']:
        print("No test user token available")
        return False
    
    # First, create a question to use in the assessment
    print("Creating a test question...")
    question_data = {
        'content': 'What is the capital of France?',
        'question_type': 'multiple_choice',
        'subject': 'Geography',
        'difficulty': 'easy',
        'options': ['Paris', 'London', 'Berlin', 'Madrid'],
        'correct_answer': 'Paris',
        'explanation': 'Paris is the capital and most populous city of France.',
        'tags': ['geography', 'capitals', 'europe']
    }
    
    question_id = None
    try:
        question_response = requests.post(
            f"{API_URL}/questions",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"},
            json=question_data
        )
        
        if question_response.status_code == 200:
            data = question_response.json()
            question_id = data['question']['id']
            print(f"✅ Successfully created question with ID: {question_id}")
        else:
            print(f"❌ Failed to create question: {question_response.status_code}")
            print(f"Response: {question_response.text}")
    except Exception as e:
        print(f"❌ Exception creating question: {str(e)}")
    
    # Create an assessment if we have a question
    if question_id:
        print("\nCreating a test assessment...")
        assessment_data = {
            'title': 'Debug Assessment',
            'description': 'A test assessment for debugging',
            'question_ids': [question_id],
            'time_limit': 30,
            'subject': 'Geography',
            'difficulty': 'easy'
        }
        
        try:
            assessment_response = requests.post(
                f"{API_URL}/assessments",
                headers={'Authorization': f"Bearer {TEST_USER['token']}"},
                json=assessment_data
            )
            
            if assessment_response.status_code == 200:
                print("✅ Successfully created assessment")
                assessment = assessment_response.json().get('assessment')
                print(f"Assessment ID: {assessment['id']}")
            else:
                print(f"❌ Failed to create assessment: {assessment_response.status_code}")
                print(f"Response: {assessment_response.text}")
        except Exception as e:
            print(f"❌ Exception creating assessment: {str(e)}")
    
    # Now try to get assessments
    print("\nGetting assessments...")
    try:
        get_response = requests.get(
            f"{API_URL}/assessments",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"}
        )
        
        if get_response.status_code == 200:
            data = get_response.json()
            print(f"✅ Successfully retrieved {len(data.get('assessments', []))} assessments")
            if data.get('assessments'):
                print("First assessment details:")
                pprint(data['assessments'][0])
        else:
            print(f"❌ Failed to get assessments: {get_response.status_code}")
            print(f"Response: {get_response.text}")
    except Exception as e:
        print(f"❌ Exception getting assessments: {str(e)}")
    
    return True

def check_mongodb_collections():
    """Check if the MongoDB collections exist and have data"""
    print("\n=== Checking MongoDB Collections ===")
    
    # We'll use the backend API to check if collections exist
    # by trying to get data from them
    
    if not TEST_USER['token']:
        print("No test user token available")
        return False
    
    collections_to_check = [
        {"name": "study_groups", "endpoint": "/groups"},
        {"name": "assessments", "endpoint": "/assessments"},
        {"name": "questions", "endpoint": "/questions"},
        {"name": "users", "endpoint": "/auth/me"}
    ]
    
    for collection in collections_to_check:
        try:
            response = requests.get(
                f"{API_URL}{collection['endpoint']}",
                headers={'Authorization': f"Bearer {TEST_USER['token']}"}
            )
            
            if response.status_code == 200:
                print(f"✅ Collection '{collection['name']}' exists and is accessible")
            else:
                print(f"❌ Collection '{collection['name']}' may have issues: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Exception checking collection '{collection['name']}': {str(e)}")
    
    return True

if __name__ == "__main__":
    print(f"{'='*80}")
    print(f"IDFS StarGuide API Endpoint Debugger")
    print(f"{'='*80}")
    
    # Setup test user
    if not setup_test_user():
        print("❌ Failed to set up test user. Cannot proceed with debugging.")
        exit(1)
    
    # Check MongoDB collections
    check_mongodb_collections()
    
    # Debug study groups endpoint
    debug_study_groups_endpoint()
    
    # Debug assessments endpoint
    debug_assessments_endpoint()
    
    print(f"\n{'='*80}")
    print("Debugging complete")
    print(f"{'='*80}")