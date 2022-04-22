import os
import csv
import json

str_csv = 'Short-Term_Rental_Permit_Applications-2022_04_21.csv'

by_status = {}
by_type = {}

with open(str_csv, "r") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        s = row['Current Status'].lower().replace(" ", "_")
        t = row['Permit Type'].lower().replace(" ", "_")
        if t == "":
            t = "none"
        by_status[s] = by_status.get(s, []) + [row]
        by_type[t] = by_type.get(t, []) + [row]

def write_files(outdir, data):

    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    else:
        for i in os.listdir(outdir):
            os.remove(os.path.join(outdir, i))
    for k, v in data.items():
        print(k, len(v))
        if len(v) > 0:
            csv_path = os.path.join(outdir, k + ".csv")
            with open(csv_path, "w") as o:
                writer = csv.DictWriter(o, fieldnames=v[0].keys())
                writer.writeheader()
                writer.writerows(v)

            geojson_path = os.path.join(outdir, k + ".geojson")
            geojson = {"type": "FeatureCollection", "features": []}
            for i in v:
                i_copy = i.copy()
                try:
                    coords = i_copy.pop("Location")
                except KeyError:
                    continue
                c = coords.split(",")
                if len(c) == 2:
                    lat = c[0].lstrip("(")
                    lng = c[1].lstrip().rstrip(")")
                    feat = {
                        "type": "Feature",
                        "properties": i_copy,
                        "geometry": {"type": "Point", "coordinates": [lng, lat]},
                    }
                    geojson['features'].append(feat)
            with open(geojson_path, "w") as o:
                json.dump(geojson, o, indent=1)

write_files("status", by_status)
write_files("type", by_type)
