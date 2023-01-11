var sep = ";"; var t = [];
document.querySelectorAll(".eventList .eventCard").forEach(function(e) {
    var a = e.querySelector("a");
    var url = 'https://www.meetup.com/fr-FR' + a.getAttribute('href');
    var name = a.innerText;
    var datetime = e.querySelector("time").getAttribute("datetime");
    var time = new Date(parseInt(datetime));
    var formated = time.toISOString().substring(0, 10);
    var line = formated + sep + name + sep + url;
    t.push(line);
});
t.join("\n");
