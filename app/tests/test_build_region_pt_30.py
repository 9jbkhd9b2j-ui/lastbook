#!/usr/bin/env python3
"""Offline Madeira builder regressions: python3 -B -m unittest app.tests.test_build_region_pt_30."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tools.build_region_pt_30 as builder
from tools.build_region_pt_30 import REGION, normalize_pt


def write_tree(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


class NormalisationTests(unittest.TestCase):
    def test_spellings_people_type_meet_in_one_key(self):
        """Case, accents, the abbreviated street type and name abbreviations share the one stored key."""
        for typed, stored in (
                ('R DE SANTA MARIA', 'rua de santa maria'),
                ('Rua de Santa Maria', 'rua de santa maria'),
                ('r de santa maria', 'rua de santa maria'),
                ('CAM S JOSE', 'caminho sao jose'),
                ('Caminho São José', 'caminho sao jose'),
                ('ER 222', 'estrada regional 222'),
        ):
            with self.subTest(text=typed):
                self.assertEqual(normalize_pt(typed), stored)


class RebuildRecoveryTests(unittest.TestCase):
    """A build stages into data.new/ and replaces data/ only after check passes, so a failure anywhere
    leaves the last good output and its report untouched — the recovery the #420 review asked for."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        for name, value in (('BASE', self.base), ('SOURCE', self.base / 'source')):
            patcher = mock.patch.object(builder, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        source = self.base / 'source'
        source.mkdir()
        (source / 'fetched.json').write_text(json.dumps({'fetched': '', 'files': {}}), encoding='utf-8')
        self.data = self.base / 'data'
        self.old = {'build.json': json.dumps({'region': REGION, 'built': 'earlier', 'outputs': {}}),
                    'map-set.json': json.dumps({'name': REGION, 'files': {}}),
                    'derived/geo/national.sqlite': 'old map'}
        write_tree(self.data, self.old)
        for step in ('cut_map', 'build_addresses', 'build_places'):
            patcher = mock.patch.object(builder, step, lambda *args: {})
            patcher.start()
            self.addCleanup(patcher.stop)

    def files(self, root):
        return {p.relative_to(root).as_posix(): p.read_text(encoding='utf-8', errors='replace')
                for p in sorted(root.rglob('*')) if p.is_file()}

    def new_map(self, fetched, geo):
        (geo / 'national.sqlite').write_text('new map', encoding='utf-8')
        return {}

    def test_a_step_that_fails_leaves_the_previous_output(self):
        def broken(fetched, geo):
            (geo / 'national.sqlite').write_text('half a map', encoding='utf-8')
            raise RuntimeError('injected failure')
        with mock.patch.object(builder, 'build_map', broken), self.assertRaises(RuntimeError):
            builder.build()
        self.assertEqual(self.files(self.data), self.old)

    def test_a_build_that_fails_its_checks_leaves_the_previous_output(self):
        with mock.patch.object(builder, 'build_map', self.new_map), \
                mock.patch.object(builder, 'check', lambda root=None: ['injected check failure']), \
                self.assertRaises(SystemExit):
            builder.build()
        self.assertEqual(self.files(self.data), self.old)
        self.assertEqual(self.files(self.base / 'data.new')['derived/geo/national.sqlite'], 'new map')   # kept to look at

    def test_a_stop_between_the_final_renames_is_repaired_by_the_next_build(self):
        self.data.rename(self.base / 'data.old')
        with mock.patch.object(builder, 'build_map', self.new_map), \
                mock.patch.object(builder, 'check', lambda root=None: ['injected check failure']), \
                self.assertRaises(SystemExit):
            builder.build()
        self.assertEqual(self.files(self.data), self.old)

    def test_a_build_that_passes_replaces_the_previous_output(self):
        checked = []

        def check_records(root=None):
            checked.append(root)
            return []
        with mock.patch.object(builder, 'build_map', self.new_map), \
                mock.patch.object(builder, 'check', check_records):
            builder.build()
        self.assertEqual(checked, [self.base / 'data.new'])           # checked before it was put in place
        new = self.files(self.data)
        self.assertEqual(new['derived/geo/national.sqlite'], 'new map')
        self.assertEqual(json.loads(new['build.json'])['outputs'].keys(), {'derived/geo/national.sqlite', 'map-set.json'})
        self.assertFalse((self.base / 'data.new').exists() or (self.base / 'data.old').exists())


if __name__ == '__main__':
    unittest.main()
