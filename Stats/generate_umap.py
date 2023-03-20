import csv
import geopandas as gpd
import json
from os import path
from gpx_converter import Converter

csvFilename = '9igf-gac.csv'

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
        }
    }

    data = template | opts

    with open(filename, 'w') as f:
        json.dump(data, f)

#Date,Suffix,KM,Dplus,Top,People,Name,Type,Comment,EventLink,TrailShortLink,TrailFullLink,Trail1,Trail2
def parseCsvFile():
    with open(csvFilename) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
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
                break

            if len(suffix) > 0:
                gpx = "{}-{}.gpx".format(date, suffix)
                img = "{}-{}.jpg".format(date, suffix)
            else:
                gpx = "{}.gpx".format(date)
                img = "{}.jpg".format(date)

            gpxPath = 'gpx/{}'.format(gpx)
            imgPath = 'img/{}'.format(img)

            if not path.exists(gpxPath):
                print('🔴 gpx not found: {}'.format(gpxPath))
                break

            if not path.exists(imgPath):
                print('🔴 img not found: {}'.format(imgPath))
                break

            # Create an empty GeoDataFrame
            gdf = gpd.GeoDataFrame(columns=['name', 'geometry'])
            track = gpd.read_file(gpxPath, layer='tracks')
            track = track.explode()
            geojson = track.to_json()
            print(geojson)

            track.plot("geometry", legend=True)

            desc = '{} km - d+ {}m - top {}m\n'.format(km, dplus, top)
            desc += '{{https://binnette.github.io/GAC/Stats/img/' + img + '}}\n'
            desc += 'GPX: {}\n'.format(trailShortLink)
            desc += 'Meetup {}: [[{}|{}]]'.format(date, eventLink, name)

            feature = {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "time": date,
                    "_umap_options": {
                        "color": "#6fde3c"
                    },
                    "description": desc,
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            5.875544,
                            45.109877,
                            1735.42
                        ],
                        [
                            5.875548,
                            45.109935,
                            1734.93
                        ]
                    ]
                }
            }
            

def main():
    parseCsvFile();

if __name__ == "__main__":
    main()
