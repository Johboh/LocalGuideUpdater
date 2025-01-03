import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Given a result.json file with result from fetch.py, upload data to top100localguides.com
# # the TOP100LOCALGUIDES_USERNAME and TOP100LOCALGUIDES_PASSWORD must be set in the the environment .env file.

INPUT = "result.json"
MAPPING = {
    "n_reviews": "review",
    "n_contreviews": "review",
    "n_ratings": "rating",
    "n_contratings": "rating",
    "n_photos": "photo",
    "n_contphotos": "photo",
    "n_contvideos": "video",
    "n_contcaptions": "photo_caption",
    "n_contanswers": "question",
    "n_contedits": "report_a_problem",
    "n_contrptinc": "mark_incorrect",
    "n_contplaces": "add_a_place",
    "n_controads": "add_missing_road",
    "n_contfacts": "moderation_vote",
    "n_contqna": "place_qa_answer",
    "n_points": "total"
}
BASE_URL = "https://top100localguides.com/"

load_dotenv()
USERNAME = os.getenv("TOP100LOCALGUIDES_USERNAME")
PASSWORD = os.getenv("TOP100LOCALGUIDES_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("TOP100LOCALGUIDES_USERNAME or TOP100LOCALGUIDES_PASSWORD environment variable is not set.")

# Read result and map into dict
data = {}
with open(INPUT, 'r') as file:
    data = json.load(file)

if data["total"] <= 0:
    print("Missing total points, result is wrong, will not continue. Exiting...")
    exit(1)

# Initialize a session
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
}

# Get CSRF Token
print("Getting CSRF token...")
token_response = session.get(BASE_URL, headers=headers)
soup = BeautifulSoup(token_response.text, 'html.parser')
token_input = soup.find('input', {'name': 'token'})

if not token_input:
    print("Unable to find CSRF token, exiting....")
    exit(1)
token_input = token_input.get('value')

# Data for login
login_data = {
    'username': USERNAME,
    'password': PASSWORD,
    'token': token_input,
}

# Perform login
print("Got token, logging in...")
login_response = session.post(BASE_URL + "authenticate.php", headers=headers, data=login_data)

if login_response.status_code == 200:
    # Get current field values
    print("Login successful, fetching current data...")
    current_response = session.get(BASE_URL + "12mapsdata.php", headers=headers)
    if current_response.status_code != 200:
        print("Failed to fetch current data, exiting...")
        exit(1)

    current_data = {}
    soup = BeautifulSoup(current_response.text, 'html.parser')
    form = soup.find('form')
    if form:
        inputs = form.find_all('input')
        for input_field in inputs:
            field_name = input_field.get('name')
            field_value = input_field.get('value')
            current_data[field_name] = field_value

    # Update current with result
    for key in current_data:
        if key in MAPPING:
            result_key = MAPPING[key]
            if result_key in data and data[result_key] > 0:
                current_data[key] = data[result_key]

    print("Will post the following: %s" % current_data)

    # Post new data
    post_response = session.post(BASE_URL + "12mapsdata.php", headers=headers, data=current_data)

    if post_response.status_code == 200:
        print("Data updated successfully")
    else:
        print("Failed to update data, exiting...")
        exit(1)
else:
    print("Login failed, exiting...")
    exit(1)
