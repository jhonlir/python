from fastapi import HTTPException
import requests
import json

class FacebookClient:
    def __init__(self):
        self.app_id = '1365696864293776'
        self.app_secret = '7061b18b00e311445d780721c3977488'

    def get_access_token(self):
        try:
            token_response = requests.post(
                'https://graph.facebook.com/oauth/access_token',
                data={
                    'client_id': self.app_id,
                    'client_secret': self.app_secret,
                    'grant_type': 'client_credentials'
                }
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            return token_data.get('access_token')
        except requests.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error getting access token: {e}")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding access token response: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error getting access token: {e}")

    def get_video_embed_html(self, video_id):
        access_token = self.get_access_token()
        try:
            video_response = requests.get(
                f'https://graph.facebook.com/v21.0/{video_id}',
                params={'access_token': access_token, 'fields': 'embed_html'}
            )
            video_response.raise_for_status()
            video_data = video_response.json()
            if 'embed_html' in video_data:
                return video_data['embed_html']
            else:
                raise HTTPException(status_code=400, detail=f"No embed HTML found for video {video_id}: {video_data}")
        except requests.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error getting video embed HTML: {e}")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding video response: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error getting video embed HTML: {e}")