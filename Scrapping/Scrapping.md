# Scrapping meetup

## Scrapping hike attendees

```js
var t = [];
document.querySelectorAll(".attendee-item h4").forEach(function(a){
  t.unshift(a.innerText);
});
t.join(";")
```
