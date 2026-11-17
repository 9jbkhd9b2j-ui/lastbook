#!/usr/bin/env python3
"""Tests for tools/build_places_region.py.

  python3 tools/test_build_places_region.py

Needs pyosmium (a build-time dependency already used by tools/build_coast.py). Builds from a tiny OSM file,
so it runs without any library or data folder.
"""
import sqlite3
import subprocess
import unittest
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

OSM = '''<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" version="1" lat="-33.8700" lon="151.2100">
    <tag k="place" v="city"/><tag k="name" v="Sydney"/><tag k="name:zh" v="悉尼"/>
  </node>
  <node id="2" version="1" lat="-33.8800" lon="151.2200">
    <tag k="amenity" v="hospital"/><tag k="name" v="St Vincent's Hospital"/><tag k="emergency" v="yes"/>
  </node>
  <node id="3" version="1" lat="-33.8900" lon="151.2300">
    <tag k="amenity" v="shelter"/><tag k="shelter_type" v="public_transport"/><tag k="name" v="Bus shelter"/>
  </node>
  <node id="4" version="1" lat="-33.9000" lon="151.2400">
    <tag k="amenity" v="pharmacy"/><tag k="name" v="Chemist Warehouse"/>
  </node>
  <node id="5" version="1" lat="-33.9100" lon="151.2500">
    <tag k="place" v="village"/><tag k="name" v="Nowhere"/><tag k="name:zh" v="诺威尔"/>
  </node>
  <node id="6" version="1" lat="-20.0000" lon="140.0000">
    <tag k="place" v="town"/><tag k="name" v="Outside"/><tag k="name:zh" v="外面"/>
  </node>
</osm>
'''


def build(osm, out, bbox=None):
    cmd = [sys.executable, str(HERE / 'build_places_region.py'), str(osm), '--region', 'Australia', '--out', str(out)]
    if bbox:
        cmd += [f'--bbox={bbox}']  # the '=' form keeps a leading minus from looking like an option
    subprocess.run(cmd, check=True, capture_output=True, text=True)


class BuildPlacesRegionTest(unittest.TestCase):
    def test_region(self):
      tmp = Path(tempfile.mkdtemp(prefix='lastbook-places-'))
      osm = tmp / 'sample.osm'
      osm.write_text(OSM, encoding='utf-8')
      out = tmp / 'geo'
      build(osm, out, bbox='-40,140,-25,155')

      pdb = sqlite3.connect(out / 'places.sqlite')
      places = pdb.execute('SELECT name,kind,detail,lat,lon,rank,source FROM place ORDER BY name').fetchall()
      assert [p[0] for p in places] == ['Nowhere', 'Sydney'], places  # Outside is outside the bbox
      sydney = next(p for p in places if p[0] == 'Sydney')
      assert sydney[1] == 'city' and sydney[5] == 1, sydney  # kind and rank as the place finder expects
      assert sydney[2].startswith('悉尼 · Australia (OpenStreetMap)'), sydney[2]
      assert abs(sydney[3] + 33.87) < 1e-6 and abs(sydney[4] - 151.21) < 1e-6, sydney

      # the place finder queries the FTS index with a prefix match; other-language names must be findable
      hit = pdb.execute('SELECT p.name FROM place_fts f JOIN place p ON p.id=f.rowid '
                        'WHERE place_fts MATCH ? ORDER BY p.rank', ('"悉尼"*',)).fetchall()
      assert [h[0] for h in hit] == ['Sydney'], hit
      hit = pdb.execute('SELECT p.name FROM place_fts f JOIN place p ON p.id=f.rowid WHERE place_fts MATCH ?',
                        ('"Nowh"*',)).fetchall()
      assert [h[0] for h in hit] == ['Nowhere'], hit
      pdb.close()

      ndb = sqlite3.connect(out / 'national.sqlite')
      poi = ndb.execute('SELECT cls,name,lon,lat FROM poi ORDER BY cls').fetchall()
      assert [p[0] for p in poi] == ['hospital', 'pharmacy'], poi  # a bus shelter is not a refuge
      assert poi[0][1] == "St Vincent's Hospital" and abs(poi[0][2] - 151.22) < 1e-6, poi[0]
      ndb.close()

      # a second run adds to the same files instead of replacing what is there
      build(osm, out)
      pdb = sqlite3.connect(out / 'places.sqlite')
      assert pdb.execute('SELECT count(*) FROM place').fetchone()[0] == 5, 'second run should add the rows it left out'
      pdb.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
