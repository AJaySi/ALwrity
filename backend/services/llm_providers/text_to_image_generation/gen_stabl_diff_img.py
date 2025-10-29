# Ensure you sign up for an account to obtain an API key:
# https://platform.stability.ai/
# Your API key can be found here after account creation:
# https://platform.stability.ai/account/keys

import os
import requests
import base64
from PIL import Image
from io import BytesIO
import streamlit as st
from loguru import logger

# Import APIKeyManager
from ...onboarding.api_key_manager import APIKeyManager

def save_generated_image(data):
    """Save the generated image to a file."""
    # Implementation for saving image
    pass

def generate_stable_diffusion_image(prompt):
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    
    # Use APIKeyManager instead of direct environment variable access
    api_key_manager = APIKeyManager()
    api_key = api_key_manager.get_api_key("stability")
    
    if api_key is None:
        st.warning("Missing Stability API key. Please configure it in the onboarding process.")
        return None
    
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": prompt
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )
    
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    
    data = response.json()
    img_path = save_generated_image(data)

    for i, image in enumerate(data["artifacts"]):
        # Decode base64 image data
        img_data = base64.b64decode(image["base64"])
        # Open image using PIL
        img = Image.open(BytesIO(img_data))
        # Display the image
        img.show()

    return img_path
