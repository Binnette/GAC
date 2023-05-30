# Scrapping meetup

## Scrapping hikes

```js
var events = [];
document.querySelectorAll(".eventList-list .eventCard").forEach(eventElement => {
  var timestamp = Number(eventElement.querySelector("time").getAttribute("datetime"));
  var date = new Date(timestamp);
  var dateString = `'${date.toISOString().slice(0, 10)}`;
  var suffix = "", km = "", dplus = "", ele = "", comment = "", attendees = "";
  var attendeesSection = eventElement.querySelector(".avatarRow--attendingCount");
  if (attendeesSection) {
    attendees = Number(attendeesSection.innerText.split(" ")[0]);
  }
  var titleElement = eventElement.querySelector(".eventCardHead--title");
  var title = titleElement.innerText.replaceAll('"', "'");
  var type = '';
  if (title.includes('🎿')){
    type = 'Ski';
  }
  if (title.includes('🥾') || title.toLowerCase().includes('hike')) {
    type = 'Hike';
  }
  var url = eventElement.querySelector("a").href;
  var trails = [];
  eventElement.querySelectorAll("a[href*='https://s.42l.fr']").forEach(trailElement => {
    trails.push(trailElement.href);
  });
  var distanceMatch = eventElement.textContent.match(/Distance: ([0-9.]+)km/);
  km = distanceMatch ? parseFloat(distanceMatch[1]) : '';
  var dplusMatch = eventElement.textContent.match(/D\+: ([0-9]+)m/);
  dplus = dplusMatch ? parseFloat(dplusMatch[1]) : '';
  events.unshift([dateString, suffix, km, dplus, ele, attendees, `"${title}"`, type, comment, url, trails.join(",")].join(";"));
});
var headers = ["date", "suffix", "km", "dplus", "ele", "attendees", "title", "type", "comment", "url", "trails"];
events.unshift(headers.join(";"));
events.push(headers.join(";"));
events.join('\n');
```

## Telegram screenshot

```js
document.querySelector("[data-testid=organizer-panel-button]").parentNode.parentNode.parentNode.remove();
document.querySelectorAll("[data-event-label=event-group]").forEach(e => console.log(e.parentNode.parentNode.remove()));
document.querySelector("[data-event-label=event-map]").parentNode.remove();
document.querySelector("[data-event-label=event-chat]").parentNode.parentNode.remove();
document.querySelector("[data-testid=add-to-calendar]").remove();
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
resultCommands.push(`  echo "🔴 Incorrect number of pictures ${nbPhotos}"`);
resultCommands.push(`else`);
resultCommands.push(`  echo "🟢 Correct number of pictures ${nbPhotos}"`);
resultCommands.push(`fi\n`);
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
