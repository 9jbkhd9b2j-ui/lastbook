#!/usr/bin/env python3
"""Topic search beyond a-z: web/words.js run in Node, with and without Intl.Segmenter.

  python3 -B -m unittest app.tests.test_topic_search [-v]

Accented words stay whole and fold (niño finds nino), Chinese words of one or two characters count, typed symbols
never reach a RegExp, Turkish İ folds to i, and every English query in the list ranks exactly as it did before.
Needs Node on PATH; skipped without it. Never packaged."""
import json, re, shutil, subprocess, tempfile, unicodedata, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NODE = shutil.which('node')
WORDS = ROOT / 'web' / 'words.js'

# The stop words app.js passes in, read from app.js so the test follows it.
QSTOP = re.search(r"const QSTOP = new Set\('([^']*)'\.split", (ROOT / 'web' / 'app.js').read_text(encoding='utf-8')).group(1).split(' ')
TOPICS = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'content' / 'topics').glob('*.json'))]

# Everyday English questions. Each must give the same topics and choices as the old a-z matching.
ENGLISH = [
    'how do I purify water', 'boil water', 'is the tap water safe', 'bleach for drinking water', 'find water',
    'deep cut bleeding', 'broken leg', 'burn on my hand', 'cpr', 'choking', 'fever', 'dehydration', 'snake bite',
    'hypothermia', 'the power is out', 'generator', 'solar panel', 'car battery', 'earthquake', 'flood',
    'wildfire smoke', 'store food', 'cook without power', 'stay warm', 'shelter', 'toilet', 'radio',
    'grow vegetables', 'save seeds', 'first aid kit', "water's gone brown", "don't have power", "can't breathe",
    'how to start a fire', 'baby', 'medicine', 'keep food cold', 'clean water storage container',
]

CASES = {
    'stop': QSTOP,
    'fold': ['İstanbul', 'ISTANBUL', 'ılık', 'Straße', 'ΣΟΦΟΣ', 'ｗａｔｅｒ', 'niño', 'niño', 'Jalapeño', 'καφές'],
    'words': ['¿Cómo purifico el agua para el niño?', '怎么净化水', "How do I purify water's taste?", 'don’t have water',
              'ｗａｔｅｒ', 'c++ (water', '[a', '(', '\\', '*?+{', 'İstanbul', 'éclair', '𠀀水', ''],
    'match': [['chocolate éclair', 'eclair'], ['Chocolate Éclair', 'eclair'], ['煮沸 水', '水'], ['怎么净化水', '净化'],
              ['drink water', 'rink'], ['drink water', 'drin'], ['Rainwater', 'water'], ['Straße', 'strasse'],
              ['ΣΟΦΟΣ', 'σοφοσ'], ['İstanbul', 'istanbul'], ['72-hour kit', 'hour'], ['Water: purify, boil', 'purif']],
    'rank': ENGLISH,
    'topics': TOPICS,
}


def run(mode):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'cases.json'
        p.write_text(json.dumps(CASES, ensure_ascii=False), encoding='utf-8')
        r = subprocess.run([NODE, str(HERE / 'topic_search_test.mjs'), str(WORDS), str(p), mode],
                           capture_output=True, text=True, encoding='utf-8', timeout=60)
    if r.returncode:
        raise AssertionError(r.stderr[-1500:])
    return json.loads(r.stdout)


def ok(entry):
    if 'error' in entry:
        raise AssertionError(entry['error'])
    return entry['ok']


@unittest.skipUnless(NODE, 'needs node on PATH')
class TopicSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seg, cls.fb = run('segmenter'), run('fallback')

    def test_modes(self):
        self.assertTrue(self.seg['segmenter'])
        self.assertFalse(self.fb['segmenter'])

    def test_fold(self):
        for r in (self.seg, self.fb):
            self.assertEqual(r['fold'], ['istanbul', 'istanbul', 'ılık', 'strasse', 'σοφοσ', 'water', 'nino', 'nino', 'jalapeno', 'καφέσ'])   # Greek accents kept, as in FTS5; final ς -> σ

    def test_turkish_i_order(self):
        # Marks must be removed only after decomposing. An NFC "İ" is one character with no mark to remove,
        # so removing marks first and lower-casing after leaves "i" + U+0307, which no longer matches "istanbul".
        marks_first = ''.join(ch for ch in unicodedata.normalize('NFC', 'İ') if not unicodedata.combining(ch)).lower()
        self.assertEqual(marks_first, 'i̇')
        self.assertEqual(self.seg['fold'][0], 'istanbul')

    def test_query_words(self):
        w = [ok(e) for e in self.seg['words']]
        self.assertEqual(w[0], ['como', 'purifico', 'agua', 'para', 'nino'])   # accents stay whole, then fold
        self.assertEqual(w[1], ['怎么', '净化', '水'])                             # one- and two-character words count
        self.assertEqual(w[2], ['purify', 'water', 'taste'])                     # water's -> water, as before
        self.assertEqual(w[3], ['water'])                                         # curly apostrophe, stop words
        self.assertEqual(w[4], ['water'])                                         # full-width Latin
        self.assertEqual(w[5], ['water'])
        self.assertEqual(w[6:10], [[], [], [], []])                               # symbols: no words, no exception
        self.assertEqual(w[10], ['istanbul'])
        self.assertEqual(w[11], ['eclair'])
        self.assertTrue(w[12])                                                    # a character outside the BMP
        self.assertEqual(w[13], [])

    def test_query_words_fallback(self):
        w = [ok(e) for e in self.fb['words']]
        self.assertEqual(w[0], ['como', 'purifico', 'agua', 'para', 'nino'])
        self.assertEqual(w[1], ['怎么净化水'])                                     # no segmenter: the run stays one word
        self.assertEqual(w[2:6], [['purify', 'water', 'taste'], ['water'], ['water'], ['water']])
        self.assertEqual(w[6:10], [[], [], [], []])

    def test_match(self):
        expect = [True, True, True, True, False, True, False, True, True, True, True, True]
        for r in (self.seg, self.fb):
            self.assertEqual([ok(e) for e in r['match']], expect)

    def test_english_ranks_as_before(self):
        for r in (self.seg, self.fb):
            for case in r['rank']:
                with self.subTest(q=case['q'], segmenter=r['segmenter']):
                    self.assertEqual(ok(case['now']), case['before'])
        self.assertTrue(any(c['before'] for c in self.seg['rank']))              # the list does reach the guides


if __name__ == '__main__':
    unittest.main()
