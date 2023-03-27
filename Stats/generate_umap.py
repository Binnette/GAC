import csv
import geopandas as gpd
import json
from os import path
from gpx_converter import Converter

csvFilename = '9igf-gac.csv'
errors = 0
prevHike = ''
colors = {
    '2020': '#1766B5',
    '2021': '#504488',
    '2022': '#8FBE23',
    '2023': '#C03535'
}
stats = {}
total = 0

def dumpUmapByLayers(filename, layers, name, description):
    opts = {
        "layers": layers
    }

    template = {
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
        "layers": []
    }

    data = template | opts

    filepath = path.join('umap', filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print('🟢 umap file created {}'.format(filename))

#Date,Suffix,KM,Dplus,Top,People,Name,Type,Comment,EventLink,TrailShortLink,TrailFullLink,Trail1,Trail2
def parseFeatureFromCsvRow(row):
    global errors, prevHike, curYear, stats, total

    date = row['Date']
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

    if type.lower() != 'Cancelled':
        total += 1
    
    if type in stats:
        stats[type] += 1
    else:
        stats[type] = 1

    if 'Hike' not in type:
        print('🟡 not a hike: {}'.format(name))
        return

    if len(suffix) > 0:
        gpx = "{}-{}.gpx".format(date, suffix)
        img = "{}-{}.jpg".format(date, suffix)
        curHike = "{}-{}".format(date, suffix)
    else:
        gpx = "{}.gpx".format(date)
        img = "{}.jpg".format(date)
        curHike = "{}".format(date)

    if len(date) < 10:
        errors += 1
        print('🔴 incorrect date format {}'.format(curHike))
        return

    if len(trailShortLink) < 1:
        errors += 1
        print('🔴 missing trailShortLink for {}'.format(curHike))
        return

    if len(km) < 1:
        errors += 1
        print('🔴 missing km for {}'.format(curHike))
        return

    if len(dplus) < 1:
        errors += 1
        print('🔴 missing dplus for {}'.format(curHike))
        return

    if len(top) < 1:
        errors += 1
        print('🔴 missing top for {}'.format(curHike))
        return

    if len(people) < 1:
        errors += 1
        print('🔴 missing people for {}'.format(curHike))
        return

    if len(name) < 1:
        errors += 1
        print('🔴 missing name for {}'.format(curHike))
        return

    if len(eventLink) < 1:
        errors += 1
        print('🔴 missing eventLink for {}'.format(curHike))
        return

    if prevHike == curHike:
        errors += 1
        print('🔴 hike with same date & suffix: {}'.format(curHike))
        return
    
    prevHike = curHike

    gpxPath = 'gpx/{}'.format(gpx)
    imgPath = 'img/{}'.format(img)

    if not path.exists(gpxPath):
        errors += 1
        print('🔴 gpx not found: {} -> {}'.format(gpxPath, trailShortLink))
        return

    if not path.exists(imgPath):
        errors += 1
        print('🔴 img not found: {} -> {}'.format(imgPath, eventLink))
        return

    # Create an empty GeoDataFrame
    gdf = gpd.GeoDataFrame(columns=['name', 'geometry'])
    track = gpd.read_file(gpxPath, layer='tracks')
    track = track.explode(index_parts=False)
    geojsonStr = track.to_json()
    geojson = json.loads(geojsonStr)
    
    if len(geojson['features']) > 1:
        errors += 1
        print('🔴 geojson contains more than one feature for gpx {}'.format(gpxPath))
        return

    geometry = geojson['features'][0]['geometry']
    
    desc = '{} km - d+ {}m - top {}m\n'.format(km, dplus, top)
    desc += '{{https://binnette.github.io/GAC/Stats/img/' + img + '}}\n'
    desc += 'GPX: {}\n'.format(trailShortLink)
    desc += 'Meetup {}: [[{}|{}]]'.format(date, eventLink, name)

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
    with open(csvFilename) as f:
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
                "name": "{} hikes".format(year),
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
    if errors > 0:
        print('🔴 CSV parsing done with {} errors'.format(errors))
    else:
        print('🟢 CSV parsing done without error')

    print("Stats :")
    for s in stats:
        print(" - {} = {}".format(s, stats[s]))
    print(" # Total = {}".format(total))

    layers = getLayersFromFeatures(features);
    for l in layers:
        layerName = l['_umap_options']['name']
        year = layerName[:4]
        filename = layerName.replace(' ', '_')
        filename = 'grenoble_adventure_club_{}.umap'.format(filename)
        name = 'Grenoble Adventure Club {} hikes'.format(year)
        description = 'All hikes done with the GAC in {}'.format(year)
        dumpUmapByLayers(filename, [l], name, description)

    filename = 'grenoble_adventure_club_all_hikes.umap'
    name = 'Grenoble Adventure Club all hikes'
    description = 'All hikes done with the GAC'
    dumpUmapByLayers(filename, layers, name, description)

def main():
    generetateAllUmap()

if __name__ == "__main__":
    main()
