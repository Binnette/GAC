import csv
import datetime
import json
import re

# Test the function with the given json file
json_file = "data.json"
csv_file = "../Stats/9igf-gac.csv"
albumRoot = 'https://binnette.github.io/GacImg'

def csv_to_array(csv_file):
  array = []
    
  #read csv file
  with open(csv_file, encoding='utf-8') as csvf: 
      #load csv file data using csv library's dictionary reader
      csvReader = csv.DictReader(csvf) 

      #convert each csv row into python dict
      for row in csvReader: 
          #add this python dict to json array
          array.append(row)

  return array

def merge_all_events_lists(list1, list2):
  # Create a dictionary with the id as the key and the item as the value for each list
  dict1 = {item["id"]: item for item in list1}
  dict2 = {item["id"]: item for item in list2}

  # Merge the two dictionaries by updating the values of dict1 with the values of dict2
  dict1.update(dict2)

  # Convert the dictionary values to a list
  return list(dict1.values())

def merge_events_lists(list1, list2):
  # Create a dictionary with the id as the key and the item as the value for each list
  dict1 = {item["id"]: item for item in list1}
  dict2 = {item["id"]: item for item in list2}

  # Loop through the keys of dict1
  for key in dict1:
    # Check if the key exists in dict2
    if key in dict2:
      # Update the value of dict1 with the value of dict2
      dict1[key].update(dict2[key])
    else:
      print(f'🔴 Event not found in CSV: {key} - {dict1[key]["title"]}')

  # Convert the dictionary values to a list
  return list(dict1.values())

def format_description(description):
  # Split the string by newline characters
  string_list = description.split("\n")

  starts = [
    "🗺️ Topo & GPX track:",
    "📲 Download GPX",
    "📏 Distance:",
    "⏱️ Time:",
    "📈 D+:",
    "Topo & GPX track:",
    "▶💡 Download GPX",
    "Distance:",
    "Time:",
    "D+:",
  ]

  # Create an empty list to store the formatted lines
  formatted_list = []

  # Loop through the string list
  for line in string_list:
    if re.match(r"\*\*.*\*\*", line):
      line = line.replace("**", "")

    if re.match(r"^=+$", line):
      line = "---------------"
    elif re.match(r"^[\s=]+$", line):
      line = ""
    elif re.match(r"^=.*", line):
      line = line.lstrip("=")
      line = line.rstrip("=")
      # Add "##" at the start of the line
      line = "## " + line
    elif any(line.startswith(x) for x in starts):
      line = "* " + line

    # Append the formatted line to the list
    formatted_list.append(line)

  # Join the list with newline characters
  formatted_string = "\n".join(formatted_list)

  # Return the formatted string
  return formatted_string

# Define a function that takes a json file as an argument
def createMarkdownFileForEvent(event):
  # Get the event details from the data
  title = event["title"].strip()
  title_without_colon = title.replace(":)", "😊").replace('"', "")
  title_without_colon = re.sub(r"\s*:\s*", " - ", title_without_colon)
  event_url = event["eventUrl"]
  description = format_description(event["description"])
  start = event["dateTime"]
  end = event["endTime"]
  create = event["createdTime"]
  going = event["going"]["totalCount"]

  if "Suffix" not in event or "KM" not in event:
    print(f'🔴 Hike not found in CSV file: {start} - {title}')
    return

  suffix = event["Suffix"]
  km = event["KM"]
  dplus = event["Dplus"]
  top = event["Top"]
  people = event["People"]
  type = event["Type"]
  comment = event["Comment"]
  trailShortLink = event["TrailShortLink"]
  trailFullLink = event["TrailFullLink"]
  album = event["Album"]

  # Convert the date and time strings to datetime objects
  start = datetime.datetime.fromisoformat(start)
  end = datetime.datetime.fromisoformat(end)
  create = datetime.datetime.fromisoformat(create)

  # Format the date and time strings for the markdown file
  date_str = start.strftime("%Y-%m-%d")
  year = start.strftime("%Y")
  start_str = start.strftime("%Y-%m-%d %H:%M")
  end_str = end.strftime("%Y-%m-%d %H:%M")
  duration = end - start
  duration_str = str(duration)
  planned = start - create
  planned_str = str(planned)
  albumUrl = f'{albumRoot}{year}/{album}'

  date_str_with_suffix = date_str
  if len(suffix) > 1:
    date_str_with_suffix = f'{date_str}-{suffix}'

  if f'{people}' != f'{going}':
    print(f'🟡 Warning csv.people={people} json.going={going} for hike: {date_str} - {title}')

  # Create the markdown file name
  md_file = f"../Stats/events/{date_str_with_suffix}.md"

  # Write the markdown content to the file
  with open(md_file, "w", encoding='utf-8') as f:
    f.write(f"---\n")
    f.write(f"layout: default\n")
    f.write(f"title: {title_without_colon}\n")
    f.write(f"---\n\n")
    f.write(f"# {title}\n\n")
    f.write(f"![{date_str_with_suffix}](../img/orig/{date_str_with_suffix}.jpg)\n\n")
    f.write(f"{description}\n\n")
    f.write(f"## Stats\n\n")
    f.write(f"- Start time: {start_str}\n")
    f.write(f"- End time: {end_str}\n")
    f.write(f"- Duration: {duration_str}\n")
    f.write(f"- Time to event: {planned_str}\n")
    f.write(f"- Attendees: {going}\n")
    f.write(f"- KM: {km}\n")
    f.write(f"- D+: {dplus}\n")
    f.write(f"- Top: {top}\n")
    f.write(f"- Type: {type}\n")
    f.write(f"- Comment: {comment}\n\n")
    f.write(f"## Links\n\n")
    f.write(f"- [Trail short link]({trailShortLink})\n")
    f.write(f"- [Trail full link]({trailFullLink})\n")
    f.write(f"- [Album]({albumUrl})\n")
    f.write(f"- [Meetup event]({event_url})\n")

    #print(f"Markdown file created: {md_file}")
    return {
      "file": f"{date_str_with_suffix}.md",
      "date": start,
      "date_str": date_str,
      "title": title
    }
  
# Define a function that takes a string list as an argument
def create_events_index(events):

  # Create an empty dictionary to store the markdown files by year
  md_dict = {}

  # Loop through the string list
  for e in events:
    s = e["file"]
    # Extract the year from the string
    year = s[:4]

    # Check if the year is already in the dictionary
    if year in md_dict:
      # Append the string to the existing list of markdown files
      md_dict[year].append(e)
    else:
      # Create a new list of markdown files for the year
      md_dict[year] = [e]

  # Create the markdown file name
  md_file = "../Stats/events/index.md"

  # Write the markdown content to the file
  with open(md_file, "w", encoding='utf-8') as f:
    f.write(f"---\n")
    f.write(f"layout: default\n")
    f.write(f"title: Events index\n")
    f.write(f"---\n\n")

    # Loop through the dictionary keys sorted by year
    for year in sorted(md_dict.keys()):
      # Write the year as a heading
      f.write(f"# {year}\n\n")

      # Loop through the markdown files for the year
      for e in md_dict[year]:
        # Write the markdown file as a list item
        f.write(f"1. [{e['date_str']} - {e['title']}]({e['file']})\n")

      # Write a blank line after each year
      f.write(f"\n")

  print(f"Index created!")

# Read CSV file
csv_events = csv_to_array(csv_file)

# Open the json file and load the data
with open(json_file, "r", encoding='utf-8') as f:
    data = json.load(f)

# Get the events from the data dictionary
#events = data["props"]["pageProps"]["__APOLLO_STATE__"]
events = data

# Filter the events that start with "Event:" and have the group reference "Group:33873418"
#filtered_events = [events[key] for key in events if key.startswith("Event:") and events[key]["group"]["__ref"] == "Group:33873418"]

merged_events = merge_events_lists(events, csv_events)

# Create a list of csv rows by mapping each filtered event to a csv row
markdown_files = [createMarkdownFileForEvent(event) for event in merged_events]

# create a new list without None values
markdown_files = [e for e in markdown_files if e is not None]

# Sort the list by data in ascending order using a lambda function
markdown_files.sort(key=lambda e: e['date'])

# Create index.md
create_events_index(markdown_files)

print(f"Processing done!")
