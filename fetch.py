import os
import re
import json
import requests
from dotenv import load_dotenv

# Fetches total points and number of videos, photos, reviews etc etc for a Google Maps Local Guide user.
# the LOCAL_GUIDE_USER_ID must be set in the the environment .env file.
# LOCAL_GUIDE_USER_ID is the ID/number as part of the profile link one get when sharing (public) the Google Maps profile.
# Write the result to "result.json" as json.

OUTPUT = "result.json"
CONTRIBUTIONS_KEY = ["review", "rating", "photo", "video", "photo_caption", "question", "report_a_problem", "mark_incorrect", "add_a_place", "add_missing_road", "moderation_vote", "place_qa_answer"]

def fetch_website_source():
    try:
        load_dotenv()
        user_id = os.getenv("LOCAL_GUIDE_USER_ID")
        if not user_id:
            raise ValueError("LOCAL_GUIDE_USER_ID environment variable is not set.")

        base_url = "https://www.google.com/maps/contrib/"
        full_url = f"{base_url}{user_id}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        # Set a cookie to accept the Google consent screen
        cookies = {
            "CONSENT": "PENDING+987",
            "SOCS": "CAESHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmRlIAEaBgiAo_CmBg"
        }

        print("Fetching stats...")
        response = requests.get(full_url, headers=headers, cookies=cookies)
        response.raise_for_status()

        website_source = response.text
        return website_source
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"An error occurred: {e}")
        return None

def parse(content: str, keys: list) -> dict:
    individual_pattern = rf'({"|".join(re.escape(name) for name in keys)})\.png\\",(\d+),'
    result = {match[0]: int(match[1]) for match in re.findall(individual_pattern, content)}

    total_points_pattern = r"place_qa_answer.*?\]\],\[(\d+),"
    match = re.search(total_points_pattern, content)
    if match:
        total = int(match.group(1))
        result["total"] = total

    return result

source_code = fetch_website_source()

if source_code:
    result = parse(content = source_code, keys = CONTRIBUTIONS_KEY)
    print("Fetched stats sucessfully: %s" % result)
    with open(OUTPUT, 'w') as f:
        json.dump(result, f, indent=4)
else:
    print("Failed to fetch website source, exiting...")
    exit(1)
