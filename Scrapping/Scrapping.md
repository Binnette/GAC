# Scrapping meetup

## Scrapping hikes

```js
// Use the built-in JSON.stringify method to convert __NEXT_DATA__ to a string
var dataString = JSON.stringify(__NEXT_DATA__, null, 2);
// Create a Blob object from the data string with the type "application/json"
var dataBlob = new Blob([dataString], {type: "application/json"});
// Create a URL for the Blob object using the URL.createObjectURL method
var dataURL = URL.createObjectURL(dataBlob);
// Create an anchor element with the download attribute set to "data.json"
var dataLink = document.createElement("a");
dataLink.download = "data.json";
// Set the href attribute of the anchor element to the data URL
dataLink.href = dataURL;
// Append the anchor element to the document body
document.body.appendChild(dataLink);
// Simulate a click on the anchor element to trigger the download
dataLink.click();
// Remove the anchor element from the document body
document.body.removeChild(dataLink);
// Revoke the data URL using the URL.revokeObjectURL method
URL.revokeObjectURL(dataURL);
```

## Telegram screenshot

```js
document.querySelector("[data-testid=organizer-panel-button]").parentNode.parentNode.parentNode.remove(); // Organizer tools
document.querySelectorAll("[data-event-label=event-group]").forEach(e => e.parentNode.parentNode.remove()); // GAC
document.querySelector("[data-event-label=event-map]").parentNode.remove(); // Map
document.querySelector("[data-testid=add-to-calendar]").remove(); // Calendar
document.querySelector("[data-event-label=action-bar]").remove(); // action-bar
```

## Scrapping photos

```js
var commands = [];
var submainText = document.querySelectorAll("#submain .items-start")[0].textContent;
var match = submainText.match(/(\d+) Photo/);
var nbPhotos = parseInt(match[1]);
var titleText = document.querySelectorAll("#submain h1")[0].textContent;
var match = titleText.match(/(\w{3} \d{1,2}, \d{4})/);
var title = titleText.replace(/\s+\(\w{3} \d{1,2}, \d{4}\)/, '')
//title = title.replaceAll(/[<>"\/\\|?*]/g, '_');
title = title.replaceAll(/'/g, '’')
title = title.replaceAll(/\//g, ' ')
var date;
if (match) {
  date = new Date(match[1] + " 14:00");
} else {
  fields = submainText.split('· ');
  date = new Date(fields[fields.length-1] + " 14:00");
}
var formattedDate = date.toISOString().slice(0, 10);
var folder = `${formattedDate} ${title}`;
document.querySelectorAll("ul a img").forEach(function(imgElement){
  var src = imgElement.getAttribute("src");
  var url = src.replace("/event_", "/highres_").replace(".webp?", ".jpeg?");
  var match = url.match(/\/highres_([0-9]+)\.jpeg/);
  var fileName = match ? `${match[1]}.jpg` : '';
  var wgetCommand = `wget -nv ${url} -O "${fileName}" 2>&1`;
  commands.push(wgetCommand);
});
if (commands.length != nbPhotos) {
  console.error(`nbPhotos=${nbPhotos};commands=${commands.length}`);
}
var resultCommands = [];
resultCommands.push(`\nmkdir '${folder}'`);
resultCommands.push(`cd '${folder}'`);
resultCommands = resultCommands.concat(commands);
resultCommands.push(`num_files=$(ls . | wc -l)`)
resultCommands.push(`cd ..`)
resultCommands.push(`if [ $num_files -ne '${nbPhotos}' ]; then`);
resultCommands.push(`  echo "🔴 Incorrect number of pictures $num_files / ${nbPhotos}"`);
resultCommands.push(`else`);
resultCommands.push(`  echo "🟢 Correct number of pictures $num_files / ${nbPhotos}"`);
resultCommands.push(`fi`);
resultCommands.push(`# Script end\n`);
resultCommands.join("\n");
```

```bash
# rename pictures
date="2023-01-14"
ext="jpg"

for p in *.jpeg; do
  p="${p/.\//}"
  np="${p/highres/$date}"
  np="${np/jpeg/$ext}"
  mv $p $np
  echo $np
done
```

## Scrap hikes for CSV

```js
var events = [];
document.querySelectorAll("ul.w-full > li").forEach(eventElement => {
  var strDateTime = eventElement.querySelector("time").textContent;
  var iso = strDateTime.replace(/,|Sun|AM/g, "").trim() + "Z";
  var date = new Date(iso);
  var dateString = `${date.toISOString().slice(0, 10)}`;
  var km = "", dplus = "", people = "";
  var attendeesSection = eventElement.querySelector(".items-center span.hidden");
  if (attendeesSection) {
    people = Number(attendeesSection.innerText.split(" ")[0]);
  }
  var titleElement = eventElement.querySelector(".ds-font-title-3");
  var title = titleElement.innerText.replaceAll('"', "'");
  var type = '';
  if (title.includes('🎿')){
    type = 'Ski';
  } else if (title.includes('🧗')){
    type = 'Via';
  } else if (title.includes('🥾') || title.toLowerCase().includes('hike')) {
    type = 'Hike';
  }
  var url = eventElement.querySelector("a").href.trim("/");
  if (url.endsWith("/")) url = url.slice(0, -1);
  parts = url.split("/");
  var id = parts[parts.length - 1];
  var trails = [];
  eventElement.querySelectorAll("a[href*='https://s.42l.fr']").forEach(trailElement => {
    trails.push(trailElement.href);
  });
  var distanceMatch = eventElement.textContent.match(/Distance: ([0-9.]+)km/);
  km = distanceMatch ? parseFloat(distanceMatch[1]) : '';
  var dplusMatch = eventElement.textContent.match(/D\+: ([0-9]+)m/);
  dplus = dplusMatch ? parseFloat(dplusMatch[1]) : '';
  var albumTitle = title.replaceAll(":", " ").replaceAll("  ", " ").replaceAll(" ", "-").trim();
  var album = `${dateString}-${albumTitle}.html`;
  events.unshift([`'${dateString}`, "", km, dplus, "", people, `"${title}"`, type, "", id, url, trails.join(";"), "", "", "", `"${album}"`, ""].join(","));
});
var headers = ["Date", "Suffix", "KM", "Dplus", "Top", "People", "Name", "Type", "Comment", "id", "EventLink", "TrailShortLink", "TrailFullLink", "Trail1", "Trail2", "Album", "HavePhoto"];

events.unshift(headers.join(","));
events.push(headers.join(","));
events.join('\n');
```