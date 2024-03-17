# pip install geopandas
# sudo apt install python3-geopandas
import csv
import geopandas as gpd
import json
from os import path
from datetime import datetime
import requests
from urllib.parse import quote

csvFilename = '9igf-gac.csv'
prevHike = '';
stats = {
    'types': {},
    'errors': 0,
    'total': 0,
    'km': 0,
    'dplus': 0,
    'people': 0,
    'kmpp': 0
};

colors = {
    '2020': '#1766B5',
    '2021': '#504488',
    '2022': '#8FBE23',
    '2023': '#C03535',
    '2024': '#FF7800'
}
albumRoot = 'https://binnette.github.io/GacImg'

def parseFloat(s):
  try:
    return float(s)
  except ValueError:
    return 0.0

def dumpUmapByLayers(filename, layers, name, description):
    data = {
        "type": "umap",
        "uri": "",
        "properties": {
            "easing": True,
            "embedControl": True,
            "fullscreenControl": True,
            "searchControl": True,
            "datalayersControl": True,
            "zoomControl": True,
            "slideshow": {},
            "captionBar": False,
            "limitBounds": {},
            "tilelayer": {
                "tms": False,
                "name": "OSM CH",
                "maxZoom": 21,
                "minZoom": 1,
                "attribution": "© [[https://binnette.github.io/GAC/|Grenoble Adventure Club]] | [[https://osm.ch|osm.ch]] | © [[https://openstreetmap.org/copyright|OpenStreetMap]] contributors",
                "url_template": "https://{s}.tile.osm.ch/switzerland/{z}/{x}/{y}.png"
            },
            "licence": "",
            "name": name,
            "description": description,
            "displayPopupFooter": False,
            "miniMap": False,
            "moreControl": True,
            "scaleControl": True,
            "scrollWheelZoom": True,
            "zoom": 10
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                5.7403564453125,
                45.182036837015886
            ]
        },
        "layers": layers
    }

    filepath = path.join('umap', filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f'🟢 umap file created: {filename}')

#Date,Suffix,KM,Dplus,Top,People,Name,Type,Comment,EventLink,TrailShortLink,TrailFullLink,Trail1,Trail2
def parseFeatureFromCsvRow(row):
    global prevHike, stats

    date = row['Date']
    date_object = datetime.strptime(date, "%Y-%m-%d")
    year = date_object.year
    suffix = row['Suffix']
    km = row['KM']
    dplus = row['Dplus']
    top = row['Top']
    people = row['People']
    name = row['Name']
    type = row['Type']
    comment = row['Comment']
    eventLink = row['EventLink']
    trailShortLink = row['TrailShortLink']
    album = row['Album']
    havePhoto = False if row['HavePhoto'] == 'No' else True

    if type.lower() != 'cancelled':
        stats['total'] += 1
        stats['km'] += parseFloat(km)
        stats['dplus'] += parseFloat(dplus)
        stats['people'] += parseFloat(people)
        stats['kmpp'] += (parseFloat(km) * parseFloat(people))
    
    if type in stats['types']:
        stats['types'][type] += 1
    else:
        stats['types'][type] = 1

    if 'Hike' not in type:
        print(f'🔵 not a hike: {name}')
        return

    if len(suffix) > 0:
        gpx = f'{date}-{suffix}.gpx'
        img = f'{date}-{suffix}.jpg'
        curHike = f'{date}-{suffix}'
    else:
        gpx = f'{date}.gpx'
        img = f'{date}.jpg'
        curHike = f'{date}'

    if len(date) < 10:
        stats['errors'] += 1
        print(f'🔴 incorrect date format {curHike}')
        return

    if len(trailShortLink) < 1:
        stats['errors'] += 1
        print(f'🔴 missing trailShortLink for {curHike}')
        return
    
    if havePhoto and len(album) < 1:
        print(f'🟡 missing Album for {curHike}')

    if len(km) < 1:
        stats['errors'] += 1
        print(f'🔴 missing km for {curHike}')
        return

    if len(dplus) < 1:
        stats['errors'] += 1
        print(f'🔴 missing dplus for {curHike}')
        return

    if len(top) < 1:
        stats['errors'] += 1
        print(f'🔴 missing top for {curHike}')
        return

    if len(people) < 1:
        stats['errors'] += 1
        print(f'🔴 missing people for {curHike}')
        return

    if len(name) < 1:
        stats['errors'] += 1
        print(f'🔴 missing name for {curHike}')
        return

    if len(eventLink) < 1:
        stats['errors'] += 1
        print(f'🔴 missing eventLink for {curHike}')
        return

    if prevHike == curHike:
        stats['errors'] += 1
        print(f'🔴 hike with same date & suffix: {curHike}')
        return
    
    prevHike = curHike

    gpxPath = f'gpx/{gpx}'
    imgPath = f'img/{img}'

    if not path.exists(gpxPath):
        stats['errors'] += 1
        print(f'🔴 gpx not found: {gpxPath} -> {trailShortLink}')
        return

    if not path.exists(imgPath):
        stats['errors'] += 1
        print(f'🔴 img not found: {imgPath} -> {eventLink}')
        return

    # Create an empty GeoDataFrame
    track = gpd.read_file(gpxPath, layer='tracks').explode(index_parts=False)
    geojson = json.loads(track.to_json())
    
    if len(geojson['features']) > 1:
        stats['errors'] += 1
        print(f'🔴 geojson contains more than one feature for gpx {gpxPath}')
        return

    geometry = geojson['features'][0]['geometry']
    
    desc = f'{km} km - d+ {dplus}m - top {top}m\n'
    desc += '{{https://binnette.github.io/GAC/Stats/img/' + img + '}}\n'
    desc += f'GPX: {trailShortLink}\n'

    if len(album) < 1:
        desc += f'{date}: [[{eventLink}|Meetup]]'
    else:
        album = quote(album)
        albumUrl = f'{albumRoot}{year}/{album}'
        desc += f'{date}: [[{albumUrl}|Album]] - [[{eventLink}|Meetup]]'

        response = requests.get(albumUrl)
        if response.status_code != 200:
            stats['errors'] += 1
            print(f'🔴 Unreachable album url: {albumUrl}')

    return {
        "type": "Feature",
        "properties": {
            "name": name,
            "description": desc,
            "time": date
        },
        "geometry": geometry
    }

def parseFeaturesFromCsvFile():
    features = []
    with open(csvFilename, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            feature = parseFeatureFromCsvRow(row)
            if feature is not None:
                 features.append(feature)

    return features

def getLayerFromFeatures(year, features):
    color = colors[year]
    return {
            "type": "FeatureCollection",
            "features": features, 
            "_umap_options": {
                "displayOnLoad": True,
                "browsable": True,
                "remoteData": {},
                "name": f'{year} hikes',
                "id": "",
                "opacity": "0.8",
                "color": color,
                "weight": "6"
            }
        }

def getLayersFromFeatures(features):
    layers = []
    toDump = []
    curYear = ''
    for f in features:
        year = f['properties']['time'][:4]
        if curYear == '':
            curYear = year
        if year != curYear:
            layers.append(getLayerFromFeatures(curYear, toDump))
            curYear = year
            toDump = []
        toDump.append(f)
    # dump last year
    layers.append(getLayerFromFeatures(curYear, toDump))
    return layers        

def generetateAllUmap():
    features = parseFeaturesFromCsvFile()
    if stats['errors'] > 0:
        print(f'🔴 CSV parsing done with {stats["errors"]} errors')
    else:
        print('🟢 CSV parsing done without error')

    print('Stats - event types :')
    for s in stats['types']:
        print(f' - {s} = {stats["types"][s]}')
    print(f' # Total (without canceled) = {stats["total"]}')

    print('Stats :')
    print(f' - km = {stats["km"]}')
    print(f' - dplus = {stats["dplus"]}')
    print(f' - people = {stats["people"]}')
    print(f' - kmpp = {stats["kmpp"]}')

    layers = getLayersFromFeatures(features);
    for l in layers:
        layerName = l['_umap_options']['name'].replace(' ', '_')
        year = layerName[:4]
        filename = f'grenoble_adventure_club_{layerName}.umap'
        name = f'Grenoble Adventure Club {year} hikes'
        description = f'All hikes done with the GAC in {year}'
        dumpUmapByLayers(filename, [l], name, description)

    filename = 'grenoble_adventure_club_all_hikes.umap'
    name = 'Grenoble Adventure Club all hikes'
    description = 'All hikes done with the GAC'
    dumpUmapByLayers(filename, layers, name, description)

if __name__ == "__main__":
    generetateAllUmap()
