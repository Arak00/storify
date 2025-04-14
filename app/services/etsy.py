import requests
import json
from urllib.parse import urlencode

class EtsyService:
    """Service for interacting with the Etsy API"""
    
    API_BASE_URL = 'https://api.etsy.com/v3'
    OAUTH_URL = 'https://www.etsy.com/oauth/connect'
    
    def __init__(self, api_key=None, api_secret=None, redirect_uri=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state):
        """Get the Etsy authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.api_key,
            'redirect_uri': self.redirect_uri,
            'scope': 'listings_r shops_r',
            'state': state
        }
        return f"{self.OAUTH_URL}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange the authorization code for an access token"""
        response = requests.post(
            f"{self.API_BASE_URL}/public/oauth/token",
            json={
                'grant_type': 'authorization_code',
                'client_id': self.api_key,
                'client_secret': self.api_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        return response.json()
    
    def get_user_info(self, access_token):
        """Get information about the authenticated user"""
        response = requests.get(
            f"{self.API_BASE_URL}/application/users/me",
            headers={
                'Authorization': f'Bearer {access_token}',
                'x-api-key': self.api_key
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
        
        return response.json()
    
    def get_shops(self, access_token):
        """Get shops owned by the user"""
        response = requests.get(
            f"{self.API_BASE_URL}/application/users/me/shops",
            headers={
                'Authorization': f'Bearer {access_token}',
                'x-api-key': self.api_key
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get shops: {response.text}")
        
        return response.json().get('results', [])
    
    def get_listings(self, shop_id, access_token, limit=25):
        """Get active listings for a shop"""
        response = requests.get(
            f"{self.API_BASE_URL}/application/shops/{shop_id}/listings/active",
            headers={
                'Authorization': f'Bearer {access_token}',
                'x-api-key': self.api_key
            },
            params={
                'limit': limit
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get listings: {response.text}")
        
        return response.json().get('results', [])
    
    def get_listing(self, listing_id, access_token):
        """Get a specific listing"""
        response = requests.get(
            f"{self.API_BASE_URL}/application/listings/{listing_id}",
            headers={
                'Authorization': f'Bearer {access_token}',
                'x-api-key': self.api_key
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get listing: {response.text}")
        
        return response.json()
    
    def get_listing_images(self, listing_id, access_token):
        """Get images for a listing"""
        response = requests.get(
            f"{self.API_BASE_URL}/application/listings/{listing_id}/images",
            headers={
                'Authorization': f'Bearer {access_token}',
                'x-api-key': self.api_key
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get listing images: {response.text}")
        
        return response.json().get('results', [])
    
    def refresh_token(self, refresh_token):
        """Refresh the access token"""
        response = requests.post(
            f"{self.API_BASE_URL}/public/oauth/token",
            json={
                'grant_type': 'refresh_token',
                'client_id': self.api_key,
                'client_secret': self.api_secret,
                'refresh_token': refresh_token
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        return response.json() 