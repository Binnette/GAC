# Import the json and os modules
import json
import os

# Define the folder name and the target id
folder = "gql2"
target_id = "33873418"
output = "data.json"

# Create an empty dictionary to store the global data
global_dict = {}

def get_events_from_data_data(data):
  # Get the group id from the data
  group_id = data["data"]["groupByUrlname"]["id"]

  # Check if the group id matches the target id
  if group_id == target_id:
    # Get the events list from the data
    events = data["data"]["groupByUrlname"]["events"]["edges"]

    # Loop through the events
    for event in events:
      # Get the event id and node from the event
      event_id = event["node"]["id"]
      node = event["node"]

      # Add the node to the global dictionary with the event id as the key
      global_dict[event_id] = node

def get_events_from_data_props(data):
  events = data["props"]["pageProps"]["__APOLLO_STATE__"]
  events = [events[key] for key in events if key.startswith("Event:") and events[key]["group"]["__ref"] == f"Group:{target_id}"]

  # Loop through the events
  for event in events:
    # Get the event id and node from the event
    event_id = event["id"]

    # Add the node to the global dictionary with the event id as the key
    global_dict[event_id] = event

# Loop through the files in the folder
for file in os.listdir(folder):
  # Check if the file is a json file
  if file.endswith(".json"):
    # Open the file and load the data
    with open(os.path.join(folder, file), "r") as f:
      data = json.load(f)

    if "data" in data:
      get_events_from_data_data(data)
    elif "props" in data:
      get_events_from_data_props(data)

# Convert the global dictionary values to a list
global_list = list(global_dict.values())

# Open a file for writing the output
with open(output, "w") as f:
  # Dump the global list to the file in JSON format
  json.dump(global_list, f, indent=2, ensure_ascii=False)

print(f'Dump {len(global_list)} events in {output}')