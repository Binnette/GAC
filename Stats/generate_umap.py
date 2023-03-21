import csv
import geopandas as gpd
import json
from os import path
from gpx_converter import Converter

csvFilename = '9igf-gac.csv'
gpxErr = 0
imgErr = 0

def dumpYear(year, features):
    sYear = str(year)
    opts = {
        "properties": {
            "name": "Grenoble Adventure Club " + sYear,
            "description": "All hikes dones with the GAC in " + sYear
        },
        "layers": [
            {
                "type": "FeatureCollection",
                "features": features,
                "_umap_options": {
                    "displayOnLoad": True,
                    "browsable": True,
                    "remoteData": {},
                    "name": sYear + " hikes",
                    "opacity": "0.8",
                    "color": "#0013e6",
                    "weight": "6"
                }
            }
        ]
    }
    
    filename = "gac-" + sYear + ".umap"
    dumpUmap(filename, opts)

def dumpUmap(filename, opts):

    template = {
        "type": "umap",
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
            "name": "",
            "description": "All hikes dones with the GAC in 2021",
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

    with open(filename, 'w') as f:
        json.dump(data, f)

#Date,Suffix,KM,Dplus,Top,People,Name,Type,Comment,EventLink,TrailShortLink,TrailFullLink,Trail1,Trail2
def parseFeatureFromCsvRow(row):
    global gpxErr
    global imgErr

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

    if 'Hike' not in type:
        print('🟡 not a hike: {}'.format(name))
        return

    if len(suffix) > 0:
        gpx = "{}-{}.gpx".format(date, suffix)
        img = "{}-{}.jpg".format(date, suffix)
    else:
        gpx = "{}.gpx".format(date)
        img = "{}.jpg".format(date)

    gpxPath = 'gpx/{}'.format(gpx)
    imgPath = 'img/{}'.format(img)

    if not path.exists(gpxPath):
        gpxErr += 1
        print('🔴 gpx not found: {}'.format(gpxPath))
        return

    if not path.exists(imgPath):
        imgErr += 1
        print('🔴 img not found: {}'.format(imgPath))
        return

    # Create an empty GeoDataFrame
    gdf = gpd.GeoDataFrame(columns=['name', 'geometry'])
    track = gpd.read_file(gpxPath, layer='tracks')
    track = track.explode(index_parts=False)
    geojsonStr = track.to_json()
    geojson = json.loads(geojsonStr)
    
    if len(geojson['features']) > 1:
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
            "time": date,
            "_umap_options": {
                "color": "#6fde3c"
            }
        },
        "geometry": geometry
    }

def parseLayerFromCsvFile():
    features = []
    with open(csvFilename) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            feature = parseFeatureFromCsvRow(row)
            if feature is not None:
                 features.append(feature)
    return {
        "type": "FeatureCollection",
        "features": features, 
        "_umap_options": {
            "displayOnLoad": True,
            "browsable": True,
            "remoteData": {},
            "name": "All hikes",
            "opacity": "0.8",
            "color": "#0013e6",
            "weight": "6"
        }
    }

def generetateAllHikesUmap():
    layer = parseLayerFromCsvFile();
    opts = {
         "layers": [layer]
    }
    dumpUmap('grenoble_adventure_club_all_hikes.umap', opts)
    print('🟢 Fichier umap prêt')
    print(' - gpxErr = {}'.format(gpxErr))
    print(' - imgErr = {}'.format(imgErr))
     

def main():
    generetateAllHikesUmap()

if __name__ == "__main__":
    main()
