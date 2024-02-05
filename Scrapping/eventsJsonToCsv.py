# Import the json and csv modules
import json
import csv
import re
import requests

# Open the data.json file and load it as a python dictionary
with open("data.json") as f:
  data = json.load(f)

# Get the events from the data dictionary
events = data["props"]["pageProps"]["__APOLLO_STATE__"]

# Filter the events that start with "Event:" and have the group reference "Group:33873418"
filtered_events = [events[key] for key in events if key.startswith("Event:") and events[key]["group"]["__ref"] == "Group:33873418"]

# Define the csv headers
headers = ["Date", "Suffix", "KM", "Dplus", "Top", "People", "Name", "Type", "Comment", "EventLink", "TrailShortLink", "TrailFullLink", "Trail1", "Trail2", "Album"]

# Define a function that takes an URL as a parameter
def get_redirected_url(url):
  # Use the requests.get method to make a GET request to the URL
  # Use the allow_redirects parameter to enable automatic redirection
  response = requests.get(url, allow_redirects=True)
  # Use the url attribute of the response object to get the final URL after redirection
  redirected_url = response.url
  # Return the redirected URL
  return redirected_url

def get_redirected_urls(urls):
  # Create an empty set for storing the redirected urls
  redirected_urls = set()

  # Loop through each url in the urls set
  for url in urls:
    # Use the get_redirected_url function to get the redirected url for each url
    redirected_url = get_redirected_url(url)
    # Add the redirected url to the redirected_urls set
    redirected_urls.add(redirected_url)
  
  return redirected_urls

# Define a function to format the date
def format_date(date):
  # Split the date by "T" and take the first part
  return date.split("T")[0]

# Define a function to remove emojis from a string
def remove_emoji(string):
  # Use a regular expression to match and replace emojis with an empty string
  import re
  emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE)
  return emoji_pattern.sub(r'', string)

# Define a function to replace letters with accent by letters without accent
def remove_accents(string):
  # Use a dictionary to map the letters with accent to the letters without accent
  accent_map = {
    "á": "a",
    "é": "e",
    "í": "i",
    "ó": "o",
    "ú": "u",
    "à": "a",
    "è": "e",
    "ì": "i",
    "ò": "o",
    "ù": "u",
    "â": "a",
    "ê": "e",
    "î": "i",
    "ô": "o",
    "û": "u",
    "ä": "a",
    "ë": "e",
    "ï": "i",
    "ö": "o",
    "ü": "u",
    "ç": "c",
    "ñ": "n"
  }
  # Replace each letter with accent by its corresponding letter without accent
  for letter in accent_map:
    string = string.replace(letter, accent_map[letter])
  return string

# Define a function to check if a string contains another string ignoring case
def contains_ignore_case(string, substring):
  # Convert both strings to lower case and use the in operator
  return substring.lower() in string.lower()

# Define a function to map an event to a csv row
def map_event_to_csv_row(event):
  # Get event full description
  description = event["description"]
  # Initialize an empty dictionary for the csv row
  csv_row = {}

  # Map the date using the format_date function
  csv_row["Date"] = format_date(event["dateTime"])

  # Default to empty
  csv_row["Suffix"] = ''

  # Get event distance if any
  # Use the re.search method to find the first match of the pattern in the description
  distanceMatch = re.search(r"Distance: ([0-9.]+)km", description)
  # Use the group method to get the matched substring, or use an empty string if no match is found
  csv_row["KM"] = float(distanceMatch.group(1)) if distanceMatch else ''

  # Get D+ elevation if any
  # Use the re.search method to find the first match of the pattern in the description
  dplusMatch = re.search(r"D\+: ([0-9]+)m", description)
  # Use the group method to get the matched substring, or use an empty string if no match is found
  csv_row["Dplus"] = int(dplusMatch.group(1)) if dplusMatch else ''

  # default
  csv_row["Top"] = ''

  # Map the people using the going totalCount
  csv_row["People"] = event["going"]["totalCount"]

  # Map the name using the title
  csv_row["Name"] = event["title"].strip()

  # Map the type using the title and the contains_ignore_case function
  if contains_ignore_case(event["title"], "hike") or contains_ignore_case(event["title"], "🥾"):
    csv_row["Type"] = "Hike"
  elif contains_ignore_case(event["title"], "ski") or contains_ignore_case(event["title"], "⛷️"):
    csv_row["Type"] = "Ski"
  elif contains_ignore_case(event["title"], "via") and contains_ignore_case(event["title"], "ferrata"):
    csv_row["Type"] = "Via"
  else:
    csv_row["Type"] = ""

  # Default to empty
  csv_row["Comment"] = ''

  # Map the event link using the eventUrl
  csv_row["EventLink"] = event["eventUrl"]

  # Use the re.findall method to find all the urls that start with 'https://s.42l.fr' in the description
  # Use the \S+? pattern to match any non-whitespace characters after the url, but as few as possible
  # Use the (?<!\]) negative lookbehind to exclude the urls that are enclosed in brackets
  # Use the (?=\)|\s|$) positive lookahead to match the urls that are followed by a parenthesis, a whitespace, or the end of the string
  urls = re.findall(r"(?<!\[)https://s\.42l\.fr\S+?(?=\)|\s|$)", description)

  # Use the set function to remove any duplicate urls from the list
  urls = set(urls)

  # Use the join method to join all the urls with a space
  csv_row["TrailShortLink"] = ' '.join(urls)

  # Default to empty
  redirected_urls = get_redirected_urls(urls)
  csv_row["TrailFullLink"] = ' '.join(redirected_urls)

  # Default to empty
  csv_row["Trail1"] = ''

  # Default to empty
  csv_row["Trail2"] = ''

  # Map the album using the format_date function, the title and the remove_accents function
  csv_row["Album"] = format_date(event["dateTime"]) + "-" + remove_accents(event["title"].strip()).replace(" ", "-") + ".html"

  # Return the csv row
  return csv_row

# Create a list of csv rows by mapping each filtered event to a csv row
csv_rows = [map_event_to_csv_row(event) for event in filtered_events]

# Open the events.csv file in write mode
with open("events.csv", "w") as f:
  # Create a csv writer object
  writer = csv.writer(f, delimiter=";")
  # Write the headers to the csv file
  writer.writerow(headers)
  # Write each csv row to the csv file
  for row in reversed(csv_rows):
    writer.writerow([row[header] for header in headers])
