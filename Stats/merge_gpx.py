import os
import gpxpy
from gpxpy.gpx import GPX
import re

def merge_gpx_files(directory, output_file):
    gpx_files = [f for f in os.listdir(directory) if f.endswith('.gpx')]
    gpx = GPX()

    for gpx_file in gpx_files:
        with open(os.path.join(directory, gpx_file), 'r') as f:
            gpx_data = gpxpy.parse(f)
            for track in gpx_data.tracks:
                for segment in track.segments:
                    # Keep only even-indexed points (0-based index)
                    segment.points = [point for i, point in enumerate(segment.points) if i % 2 == 0]
                    for point in segment.points:
                        point.elevation = None  # This removes the <ele> tag
                        point.time = None  # This removes the <time> tag
                gpx.tracks.append(track)

    # Generate the XML without pretty printing
    xml_str = gpx.to_xml(prettyprint=False)

    # Use regex to replace empty trkpt tags with self-closing ones
    xml_str = re.sub(r'<trkpt lat="([0-9.-]+)" lon="([0-9.-]+)">\s*</trkpt>', r'<trkpt lat="\1" lon="\2"/>', xml_str)

    with open(output_file, 'w') as f:
        f.write(xml_str)

    print(f'Merged {len(gpx_files)} gpx files into: {output_file}')

# Usage
merge_gpx_files('gpx', 'merged.gpx')
