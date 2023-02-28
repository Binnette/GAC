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
  var km = "", dplus = "", ele = "",  comment = "", attendees = "";
  var section = e.querySelector(".avatarRow--attendingCount");
  if (section) {
    attendees = Number(section.innerText.split(" ")[0]);
  }
  var title = e.querySelector(".eventCardHead--title").innerText.replaceAll('"', "'");
  var url = e.querySelector("a").href;
  var trails = [];
  e.querySelectorAll("a[href*='https://s.42l.fr']").forEach(a => { trails.push(a.href); });
  t.unshift([date, km, dplus, ele, attendees, '"' + title + '"', comment, url, trails.join(",")].join(";"));
});
t.unshift(["date", "km", "dplus", "ele", "attendees", "title", "comment", "url", "trails"].join(";"));
t.push(["date", "km", "dplus", "ele", "attendees", "title", "comment", "url", "trails"].join(";"));
t.join('\n');
```