import os
import gpxpy
from gpxpy.gpx import GPX

def merge_gpx_files(directory, output_file):
    gpx_files = [f for f in os.listdir(directory) if f.endswith('.gpx')]
    gpx = GPX()

    for gpx_file in gpx_files:
        with open(os.path.join(directory, gpx_file), 'r') as f:
            gpx_data = gpxpy.parse(f)
            for track in gpx_data.tracks:
                gpx.tracks.append(track)

    with open(output_file, 'w') as f:
        f.write(gpx.to_xml())

    print(f'Merged {len(gpx_files)} gpx in file: {output_file}')

# Usage
merge_gpx_files('gpx', 'merged.gpx')
