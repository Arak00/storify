import requests
import json
from urllib.parse import urlencode

class InstagramService:
    """Service for interacting with the Instagram Graph API"""
    
    API_BASE_URL = 'https://api.instagram.com'
    GRAPH_BASE_URL = 'https://graph.instagram.com'
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state):
        """Get the Instagram authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state
        }
        return f"{self.API_BASE_URL}/oauth/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange the authorization code for an access token"""
        response = requests.post(
            f"{self.API_BASE_URL}/oauth/access_token",
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        # Convert short-lived token to long-lived token
        token_data = response.json()
        
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/access_token",
            params={
                'grant_type': 'ig_exchange_token',
                'client_secret': self.client_secret,
                'access_token': token_data['access_token']
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to exchange for long-lived token: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token):
        """Get information about the authenticated user"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/me",
            params={
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        return response.json()
    
    def get_posts(self, access_token, limit=25):
        """Get the user's media/posts"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/me/media",
            params={
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username',
                'access_token': access_token,
                'limit': limit
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get posts: {response.text}")
        
        return response.json().get('data', [])
    
    def get_post(self, media_id, access_token):
        """Get a specific post"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/{media_id}",
            params={
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username',
                'access_token': access_token
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get post: {response.text}")
        
        return response.json()
    
    def refresh_token(self, access_token):
        """Refresh a long-lived token (can be done within 60 days)"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/refresh_access_token",
            params={
                'grant_type': 'ig_refresh_token',
                'access_token': access_token
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        return response.json() 