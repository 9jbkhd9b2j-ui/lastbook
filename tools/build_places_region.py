#!/usr/bin/env python3
"""Build the place finder and the help points from an OpenStreetMap extract for any region.

The map set shipped with Lastbook is Southern California, built from the US government gazetteers and one
Geofabrik extract. This tool does the same job from a single .osm.pbf for any region: towns, villages,
islands and named places go into `places.sqlite` (with the FTS index the place finder reads), and hospitals,
clinics, pharmacies, police, fire stations, drinking water, shelters, camp sites, fuel and supermarkets go
into the `poi` table of `national.sqlite`, which the map draws and the assistant can cite.

Names in other languages (`name:zh`, `name:ru`, …) are kept in the place's `detail` column, which is
indexed too, so a person can search in their own language. A place with a Chinese name gets it in front
of the detail: `悉尼 · Australia (OpenStreetMap)`.

  python3 tools/build_places_region.py australia-latest.osm.pbf --region Australia
  python3 tools/build_places_region.py new-zealand-latest.osm.pbf --region 'New Zealand' --bbox 166,-48,179,-34

Reads the .pbf, never writes it. Writes (or adds to) derived/geo/places.sqlite and derived/geo/national.sqlite,
so it can be run for several regions in a row. `--fresh` deletes the two files first.
"""
import argparse
import sqlite3
import sys
from pathlib import Path

import osmium

HERE = Path(__file__).resolve().parents[1]

PLACE = {'city': 1, 'town': 2, 'village': 3, 'hamlet': 4, 'suburb': 5, 'quarter': 5, 'neighbourhood': 5,
         'locality': 4, 'isolated_dwelling': 5, 'farm': 5, 'island': 4, 'islet': 5, 'archipelago': 4}
AMENITY = {'hospital', 'clinic', 'doctors', 'pharmacy', 'police', 'fire_station', 'drinking_water',
           'shelter', 'toilets', 'fuel', 'ranger_station', 'community_centre', 'social_facility'}
SHOP = {'supermarket', 'convenience', 'hardware', 'doityourself'}
ZH = ('name:zh', 'name:zh-Hans', 'name:zh-Hant')


def local_name(tags):
    """The first name in another language, Chinese first: it goes in front of the detail line."""
    for key in ZH + ('name:en', 'name:ru', 'name:es', 'name:fr', 'name:ar'):
        v = tags.get(key)
        if v:
            return v
    return ''


def poi_class(tags):
    a = tags.get('amenity')
    if a in AMENITY:
        # amenity=shelter is a bus shelter in much of the world; keep only real refuges and weather shelters
        if a == 'shelter' and tags.get('shelter_type') not in (None, 'weather_shelter', 'basic_hut'):
            return None
        return a
    if tags.get('emergency') in ('ambulance_station', 'water_tank'):
        return 'fire_station' if tags.get('emergency') == 'ambulance_station' else 'drinking_water'
    s = tags.get('shop')
    if s in SHOP:
        return 'supermarket' if s in ('supermarket', 'convenience') else s
    if tags.get('tourism') in ('alpine_hut', 'wilderness_hut', 'camp_site'):
        return 'camp_site' if tags.get('tourism') == 'camp_site' else 'shelter'
    return None


class Extract(osmium.SimpleHandler):
    def __init__(self, region, bbox):
        super().__init__()
        self.region = region
        self.bbox = bbox  # (min_lat, min_lon, max_lat, max_lon) or None
        self.places, self.pois = [], []

    def inside(self, lat, lon):
        if not self.bbox:
            return True
        a, b, c, d = self.bbox
        return a <= lat <= c and b <= lon <= d

    def node(self, n):
        t = n.tags
        if not t:
            return
        name = t.get('name') or local_name(t)
        if not name or not self.inside(n.location.lat, n.location.lon):
            return
        local = local_name(t)
        detail = (local + ' · ' if local and local != name else '') + f'{self.region} (OpenStreetMap)'
        rank = PLACE.get(t.get('place'))
        if rank:
            self.places.append((name, t.get('place'), detail, n.location.lat, n.location.lon, rank, 'OpenStreetMap'))
            return
        cls = poi_class(t)
        if cls:
            self.pois.append((cls, name, n.location.lon, n.location.lat))

    def area(self, a):
        t = a.tags
        if not t:
            return
        cls = poi_class(t)
        name = t.get('name') or local_name(t)
        if not (cls and name):
            return
        try:
            c = a.geometry().centroid()
        except Exception:
            return
        if self.inside(c.lat, c.lon):
            self.pois.append((cls, name, c.lon, c.lat))


def open_dbs(out, fresh):
    out.mkdir(parents=True, exist_ok=True)
    places, national = out / 'places.sqlite', out / 'national.sqlite'
    if fresh:
        for f in (places, national):
            f.unlink(missing_ok=True)
    pdb = sqlite3.connect(places)
    pdb.executescript('''CREATE TABLE IF NOT EXISTS place(id INTEGER PRIMARY KEY, name TEXT, kind TEXT, detail TEXT,
        lat REAL, lon REAL, rank INTEGER, source TEXT);
      CREATE VIRTUAL TABLE IF NOT EXISTS place_fts USING fts5(name, detail, content='place', content_rowid='id',
        tokenize='unicode61');''')
    ndb = sqlite3.connect(national)
    ndb.executescript('CREATE TABLE IF NOT EXISTS poi(id INTEGER PRIMARY KEY, cls TEXT, name TEXT, lon REAL, lat REAL);')
    return pdb, ndb


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('pbf', help='.osm.pbf for the region (Geofabrik, BBBike, …)')
    ap.add_argument('--region', required=True, help='plain name for the detail line, e.g. Australia')
    ap.add_argument('--out', default=str(HERE / 'derived' / 'geo'), help='directory holding places.sqlite')
    ap.add_argument('--bbox', help='min_lat,min_lon,max_lat,max_lon to keep only part of the extract; '
                                'write --bbox=-40,140,-25,155 when a number is negative')
    ap.add_argument('--fresh', action='store_true', help='delete places.sqlite and national.sqlite first')
    a = ap.parse_args()

    bbox = None
    if a.bbox:
        try:
            bbox = tuple(float(x) for x in a.bbox.split(','))
            if len(bbox) != 4:
                raise ValueError
        except ValueError:
            sys.exit('--bbox needs four numbers: min_lat,min_lon,max_lat,max_lon')

    h = Extract(a.region, bbox)
    h.apply_file(a.pbf, locations=True)
    pdb, ndb = open_dbs(Path(a.out), a.fresh)
    ins = 'INSERT INTO place(name,kind,detail,lat,lon,rank,source) VALUES (?,?,?,?,?,?,?)'
    pdb.executemany(ins, h.places)
    pdb.execute("INSERT INTO place_fts(place_fts) VALUES ('rebuild')")
    pdb.commit()
    ndb.executemany('INSERT INTO poi(cls,name,lon,lat) VALUES (?,?,?,?)', h.pois)
    ndb.commit()
    print(f"places {len(h.places)}  poi {len(h.pois)}  → {Path(a.out) / 'places.sqlite'}")


if __name__ == '__main__':
    main()
