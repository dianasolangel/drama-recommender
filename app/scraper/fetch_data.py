import requests

BASE_URL = "https://kuryana.tbdh.app"

def get_user_list(username):
    url = f"{BASE_URL}/dramalist/{username}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_drama_metadata(slug):
    url = f"{BASE_URL}/id/{slug}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
