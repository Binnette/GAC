# Scrapping meetup

## Scrapping hike attendees

```js
var t = [];
document.querySelectorAll(".attendee-item h4").forEach(function(a){
  t.unshift(a.innerText);
});
t.join(";")
```

## Scrapping hikes

```js
var t=[]; document.querySelectorAll(".eventList-list .eventCard").forEach(e => {
  var date = Number(e.querySelector("time").getAttribute("datetime"));
  var date = new Date(date);
  var date = "'" + date.toISOString().slice(0, 10);
  var suffix = "", km = "", dplus = "", ele = "",  comment = "", attendees = "";
  var section = e.querySelector(".avatarRow--attendingCount");
  if (section) {
    attendees = Number(section.innerText.split(" ")[0]);
  }
  var title = e.querySelector(".eventCardHead--title").innerText.replaceAll('"', "'");
  var type = ''
  if (title.includes('🥾') || title.toLowerCase().includes('hike')) {
    type = 'Hike'
  }
  var url = e.querySelector("a").href;
  var trails = [];
  e.querySelectorAll("a[href*='https://s.42l.fr']").forEach(a => { trails.push(a.href); });
  t.unshift([date, suffix, km, dplus, ele, attendees, '"' + title + '"', type, comment, url, trails.join(",")].join(";"));
});
var headers = ["date", "suffix", "km", "dplus", "ele", "attendees", "title", "type", "comment", "url", "trails"];
t.unshift(headers.join(";"));
t.push(headers.join(";"));
t.join('\n');
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
```