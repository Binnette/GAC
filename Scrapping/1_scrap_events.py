"""
This script scrapes past event data from the Grenoble Adventure Club Meetup page.
It uses Selenium and BeautifulSoup to extract event data and saves it to a JSON file.
"""

import json
from bs4 import BeautifulSoup
from utils import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants
PAST_EVENTS_URL = "https://www.meetup.com/grenoble-adventure-club-english-french/events/?type=past"
GEOJSON_FILE = 'scrap_data.json'

# Open the URL
driver = get_driver()
driver.get(PAST_EVENTS_URL)

# Function to capture JSON network requests
def capture_json_requests(driver):
    logs = driver.get_log('performance')
    json_requests = []
    for entry in logs:
        try:
            log = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in log['method'] and 'params' in log and 'response' in log['params'] and 'json' in log['params']['response']['mimeType']:
                request_id = log['params']['requestId']
                response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                body = json.loads(response['body'])
                json_requests.append(body)
        except Exception as e:
            print(f"Error capturing network request: {e}")
    return json_requests

# Initialize variables
previous_max = -1
same_max_count = 0
json_requests_array = []

# Wait until at least one div with id like "ep-x" is present
# Wait until the elements are present
wait = WebDriverWait(driver, 2)
max_value = 0

# Main loop
while same_max_count < 3:
    try:
        wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//div[starts-with(@id, 'ep-{max_value+1}')]")))
    except:
        print(f"ep-{max_value+1} not found")

    # Get all divs with ids like "ep-x"
    divs = driver.find_elements(By.XPATH, "//div[starts-with(@id, 'ep-')]")
    
    # Find the maximum "ep-x" value
    max_value = max([int(div.get_attribute("id").split('-')[1]) for div in divs])

    # Scroll to the maximum "ep-x" div
    max_div = driver.find_element(By.ID, f"ep-{max_value}")
    actions = ActionChains(driver)
    actions.move_to_element(max_div).perform()

    # Scroll down a bit to load more content
    driver.execute_script("window.scrollBy(0, 1000);")

    # Check if the maximum value is the same as the previous iteration
    if max_value == previous_max:
        same_max_count += 1
        print(f"Max value {max_value} same {same_max_count} times")
    else:
        same_max_count = 0
        print(f"Max value {max_value} updated")

    # Update the previous maximum value
    previous_max = max_value
    
# Capture JSON network requests and append to json_requests_array
json_requests = capture_json_requests(driver)
json_requests_array.extend(json_requests)

# Use BeautifulSoup to extract JSON from <script id="__NEXT_DATA__">
soup = BeautifulSoup(driver.page_source, 'html.parser')
script_tag = soup.find('script', id='__NEXT_DATA__')
if script_tag:
    next_data = json.loads(script_tag.string)
    apollo_state = next_data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})

    next_event_count = 0
    # Extract properties starting with "Event:"
    for key, value in apollo_state.items():
        if key.startswith("Event:"):
            next_event_count += 1
            json_requests_array.append(value)

print(f'Found {next_event_count} events')

# Write the JSON requests to the output file
with open(GEOJSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(json_requests_array, f, ensure_ascii=False, indent=2)

# Close the driver
driver.quit()

print(f'{len(json_requests_array)} JSON objects dumped to {GEOJSON_FILE}')
