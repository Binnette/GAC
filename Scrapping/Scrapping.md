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
var t=[];
document.querySelectorAll("ul a img").forEach(function(e){
  var s = e.getAttribute("src").replace("/event_", "/highres_").replace(".webp?", ".jpeg?");
  t.push(s);
});
t.join("\n");
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
