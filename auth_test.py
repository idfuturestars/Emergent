#!/usr/bin/env python3
"""
IDFS StarGuide Authentication Test Suite
This script specifically tests the authentication system of the IDFS StarGuide application.
"""

import requests
import json
import unittest
import random
import string
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from frontend/.env to get the backend URL
frontend_env_path = Path('/app/frontend/.env')
load_dotenv(frontend_env_path)

# Backend API URL
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")

API_URL = f"{BACKEND_URL}/api"
print(f"Using backend API URL: {API_URL}")

# Generate random credentials for testing
TEST_USER = {
    'username': f"testuser_{random.randint(1000, 9999)}",
    'email': f"testuser_{random.randint(1000, 9999)}@example.com",
    'password': ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
    'role': 'student',
    'token': None,
    'id': None
}

class AuthenticationTest(unittest.TestCase):
    """Test authentication endpoints"""
    
    def test_01_register_user(self):
        """Test user registration with valid data"""
        print("\n=== Testing User Registration ===")
        
        # Registration data
        register_data = {
            'username': TEST_USER['username'],
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'role': TEST_USER['role'],
            'full_name': "Test User"
        }
        
        print(f"Registering user: {register_data['username']} with email: {register_data['email']}")
        
        # Make registration request
        response = requests.post(
            f"{API_URL}/auth/register",
            json=register_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Registration failed with status {response.status_code}: {response.text}")
        
        # Parse response
        data = response.json()
        self.assertIn('token', data, "No token returned in registration response")
        self.assertIn('user', data, "No user data returned in registration response")
        self.assertEqual(data['user']['email'], register_data['email'], "Email mismatch in response")
        
        # Store token and user ID for subsequent tests
        TEST_USER['token'] = data['token']
        TEST_USER['id'] = data['user']['id']
        
        print(f"Successfully registered user with ID: {TEST_USER['id']}")
        
        # Verify user is stored in database by retrieving user info
        me_response = requests.get(
            f"{API_URL}/auth/me",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"}
        )
        
        self.assertEqual(me_response.status_code, 200, "Failed to retrieve user info after registration")
        user_data = me_response.json()
        self.assertEqual(user_data['email'], register_data['email'], "Email mismatch in user data")
        
        print("Successfully verified user is stored in database")
    
    def test_02_login_user(self):
        """Test user login with valid credentials"""
        print("\n=== Testing User Login ===")
        
        # Login data
        login_data = {
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        }
        
        print(f"Logging in with email: {login_data['email']}")
        
        # Make login request
        response = requests.post(
            f"{API_URL}/auth/login",
            json=login_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Login failed with status {response.status_code}: {response.text}")
        
        # Parse response
        data = response.json()
        self.assertIn('token', data, "No token returned in login response")
        self.assertIn('user', data, "No user data returned in login response")
        self.assertEqual(data['user']['email'], login_data['email'], "Email mismatch in response")
        
        # Update token for subsequent tests
        TEST_USER['token'] = data['token']
        
        print("Successfully logged in and received valid JWT token")
        
        # Verify token contains user information
        import jwt
        try:
            # We don't have the secret key, but we can decode without verification
            # just to check the structure
            decoded = jwt.decode(data['token'], options={"verify_signature": False})
            self.assertIn('user_id', decoded, "Token does not contain user_id")
            self.assertIn('email', decoded, "Token does not contain email")
            self.assertIn('role', decoded, "Token does not contain role")
            self.assertEqual(decoded['email'], login_data['email'], "Email mismatch in token")
            print("Successfully verified JWT token contains user information")
        except Exception as e:
            self.fail(f"Failed to decode JWT token: {str(e)}")
    
    def test_03_protected_route(self):
        """Test accessing a protected route with valid JWT token"""
        print("\n=== Testing Protected Route Access ===")
        
        if not TEST_USER['token']:
            self.skipTest("No token available, skipping protected route test")
        
        print("Accessing protected route /api/auth/me")
        
        # Make request to protected route
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Protected route access failed with status {response.status_code}: {response.text}")
        
        # Parse response
        data = response.json()
        self.assertEqual(data['email'], TEST_USER['email'], "Email mismatch in protected route response")
        self.assertEqual(data['role'], TEST_USER['role'], "Role mismatch in protected route response")
        
        print("Successfully accessed protected route with valid token")
    
    def test_04_login_incorrect_password(self):
        """Test login with incorrect password (should return 401)"""
        print("\n=== Testing Login with Incorrect Password ===")
        
        # Login data with incorrect password
        login_data = {
            'email': TEST_USER['email'],
            'password': TEST_USER['password'] + '_wrong'
        }
        
        print(f"Attempting login with incorrect password for email: {login_data['email']}")
        
        # Make login request
        response = requests.post(
            f"{API_URL}/auth/login",
            json=login_data
        )
        
        # Check response - should be 401 Unauthorized
        self.assertEqual(response.status_code, 401, f"Expected 401 status code, got {response.status_code}: {response.text}")
        
        print("Successfully verified login fails with incorrect password")
    
    def test_05_login_nonexistent_email(self):
        """Test login with non-existent email (should return 401)"""
        print("\n=== Testing Login with Non-existent Email ===")
        
        # Login data with non-existent email
        login_data = {
            'email': f"nonexistent_{random.randint(1000, 9999)}@example.com",
            'password': TEST_USER['password']
        }
        
        print(f"Attempting login with non-existent email: {login_data['email']}")
        
        # Make login request
        response = requests.post(
            f"{API_URL}/auth/login",
            json=login_data
        )
        
        # Check response - should be 401 Unauthorized
        self.assertEqual(response.status_code, 401, f"Expected 401 status code, got {response.status_code}: {response.text}")
        
        print("Successfully verified login fails with non-existent email")
    
    def test_06_protected_route_without_token(self):
        """Test accessing protected route without token (should return 401)"""
        print("\n=== Testing Protected Route Access Without Token ===")
        
        print("Attempting to access protected route without token")
        
        # Make request to protected route without token
        response = requests.get(f"{API_URL}/auth/me")
        
        # Check response - should be 401 Unauthorized
        self.assertEqual(response.status_code, 401, f"Expected 401 status code, got {response.status_code}: {response.text}")
        
        print("Successfully verified protected route access fails without token")
    
    def test_07_logout_user(self):
        """Test user logout"""
        print("\n=== Testing User Logout ===")
        
        if not TEST_USER['token']:
            self.skipTest("No token available, skipping logout test")
        
        print("Logging out user")
        
        # Make logout request
        response = requests.post(
            f"{API_URL}/auth/logout",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Logout failed with status {response.status_code}: {response.text}")
        
        print("Successfully logged out user")
        
        # Verify user's online status is updated by checking user info
        # Note: We can still use the token to access protected routes after logout
        # as the token is still valid, but the user's online status should be updated
        me_response = requests.get(
            f"{API_URL}/auth/me",
            headers={'Authorization': f"Bearer {TEST_USER['token']}"}
        )
        
        self.assertEqual(me_response.status_code, 200, "Failed to retrieve user info after logout")
        
        print("Successfully verified user can still access protected routes after logout (token still valid)")


if __name__ == "__main__":
    print(f"{'='*80}")
    print(f"IDFS StarGuide Authentication Test Suite")
    print(f"{'='*80}")
    
    unittest.main(verbosity=2)