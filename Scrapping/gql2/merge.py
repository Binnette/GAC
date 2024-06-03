import json
import os

# Initialize an empty dictionary for the merged data
merged_data = {"props": {"pageProps": {"__APOLLO_STATE__": {}}}}
count = 0

# Loop over the files
for i in range(11, 9, -1):
    filename = f"{i}.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            apollo_state = data.get("props", {}).get("pageProps", {}).get("__APOLLO_STATE__", {})
            for key, value in apollo_state.items():
                if key.startswith("Event:") and value.get("group", {}).get("__ref") == "Group:33873418":
                    # Only add the event to the merged data if it does not already exist
                    if key not in merged_data["props"]["pageProps"]["__APOLLO_STATE__"]:
                        merged_data["props"]["pageProps"]["__APOLLO_STATE__"][key] = value
                        count += 1

# Write the merged data to a new JSON file
with open('merged.json', 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=4)

print(f"Merged {count} events.")