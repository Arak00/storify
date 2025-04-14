import requests
import json
from urllib.parse import urlencode

class TikTokService:
    """Service for interacting with the TikTok API"""
    
    API_BASE_URL = 'https://open-api.tiktok.com'
    GRAPH_BASE_URL = 'https://open-api.tiktok.com/api/v2'
    
    def __init__(self, client_key=None, client_secret=None, redirect_uri=None):
        self.client_key = client_key
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state):
        """Get the TikTok authorization URL"""
        params = {
            'client_key': self.client_key,
            'response_type': 'code',
            'scope': 'user.info.basic,video.list',
            'redirect_uri': self.redirect_uri,
            'state': state
        }
        return f"{self.API_BASE_URL}/platform/oauth/connect?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange the authorization code for an access token"""
        response = requests.post(
            f"{self.API_BASE_URL}/oauth/access_token",
            data={
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token):
        """Get information about the authenticated user"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/user/info",
            headers={
                'Authorization': f'Bearer {access_token}'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        return response.json().get('data', {})
    
    def get_videos(self, access_token, limit=20):
        """Get the user's videos"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/video/list",
            headers={
                'Authorization': f'Bearer {access_token}'
            },
            params={
                'fields': 'id,title,cover_image_url,share_url,video_description,duration,height,width,create_time',
                'max_count': limit
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get videos: {response.text}")
        
        return response.json().get('data', {}).get('videos', [])
    
    def get_video(self, video_id, access_token):
        """Get a specific video"""
        response = requests.get(
            f"{self.GRAPH_BASE_URL}/video/query",
            headers={
                'Authorization': f'Bearer {access_token}'
            },
            params={
                'fields': 'id,title,cover_image_url,share_url,video_description,duration,height,width,create_time',
                'video_id': video_id
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get video: {response.text}")
        
        return response.json().get('data', {})
    
    def refresh_token(self, refresh_token):
        """Refresh the access token"""
        response = requests.post(
            f"{self.API_BASE_URL}/oauth/refresh_token",
            data={
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        return response.json() 