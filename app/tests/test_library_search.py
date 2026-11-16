#!/usr/bin/env python3
"""The library's full-text search in scripts whose words carry combining marks: Hindi, Thai, vowelled Arabic, pointed
Hebrew. No real library, no server, no port: small made-up indexes in a temporary folder.

  python3 -B -m unittest app.tests.test_library_search

The index keeps marks inside words (engine/library.py, TOKENIZE) and every search splits its words the same way
(query_terms). English and Latin-accent searches must find exactly what they found before.
"""
import importlib.util, json, os, re, sqlite3, subprocess, sys, tempfile, unicodedata, unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT)]
LIBRARY_DIR = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)


def load_library():
    """A private copy of engine/library.py whose library folder is a new, empty temporary one. engine.library itself is left
    alone: it fixes its folder when first imported, and test_bridge needs it to be the data folder it sets up."""
    with mock.patch.dict(os.environ, {'LASTBOOK_LIBRARY': LIBRARY_DIR.name}):
        spec = importlib.util.spec_from_file_location('library_under_test', ROOT / 'engine' / 'library.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


library = load_library()

# The table and the split as they were before marks were kept, to show what changes and what must not.
OLD_TABLE = 'CREATE VIRTUAL TABLE pages USING fts5(doc_id UNINDEXED,title,collection,category,path UNINDEXED,page UNINDEXED,body,tokenize="unicode61")'
SQL = "SELECT doc_id FROM pages WHERE pages MATCH ? ORDER BY bm25(pages,0,5,2,1,0,0,1) LIMIT 25"

HINDI = [('hi-water', 'पानी को उबालें।'),          # boil the water
         ('hi-drink', 'रोज़ दवा पीना।')]            # take (drink) medicine daily: the same consonants प and न as पानी
# Thai is written without spaces between words, and unicode61 does not segment it: a run of Thai letters is one word,
# before this change and after. These pages put a space between words, as the fix is about each word staying whole.
THAI = [('th-water', 'น้ำ สะอาด'),                  # clean water
        ('th-lead', 'นำ ทาง'),                       # lead the way
        ('th-sentence', 'ต้มน้ำให้เดือดก่อนดื่ม')]     # boil water before drinking, written as Thai is: no spaces
ARABIC = [('ar-letter', 'هذا حَرْف'),               # this is a letter (of the alphabet)
          ('ar-joy', 'فَرَحٌ كبير')]                  # great joy: the same three letters, ف ر ح, in another order
HEBREW = [('he-peace', 'שָׁלוֹם עֲלֵיכֶם'),          # peace be upon you
          ('he-name', 'שֵׁם לוֹ')]                    # a name for him: ש, לו and ם again, in other words
LATIN = [('la-creme', 'Crème brûlée'), ('la-cafe', 'Café au lait'), ('la-street', 'Die Straße ist nass')]
ENGLISH = [('en-boil', 'Bring water to a rolling boil for one minute.'),
           ('en-store', 'Store drinking-water in clean, food-grade containers.'),
           ('en-dehydration', 'Signs of dehydration: thirst, dark urine, dizziness.'),
           ('en-flood', "Don't drink flood water; it carries sewage."),
           ('en-bleach', 'Use 2-3 drops of bleach per litre of clear water.'),
           ('en-wound', 'wound_care basics: clean, cover, watch for infection'),
           ('en-cafe', 'A café filter is not a water filter.')]
ENGLISH_QUERIES = ['water', 'rolling boil', 'drinking-water', 'food grade', "don't drink", '2-3 drops', 'wound_care',
                   'bleach litre', 'cafe', 'café', 'CAFÉ', 'dehydration thirst', 'water filter', 'nothing-here', '', '!!!',
                   'Straße', 'strasse', 'creme', 'brulee']


def make_db(path, table, pages):
    con = sqlite3.connect(path)
    try:
        con.execute(table)
        for doc, body in pages:
            con.execute('INSERT INTO pages VALUES (?,?,?,?,?,?,?)', (doc, '', '', '', f'documents/{doc}.pdf', 1, body))
        con.commit()
    finally:
        con.close()        # Windows will not remove an open file
    return path


def old_search(db, q):
    """engine/library.py's search() as it was: words by [\\w-]+, each quoted, all of them required."""
    terms = re.findall(r'[\w-]+', q, flags=re.UNICODE)
    if not terms:
        return []
    con = sqlite3.connect(db)
    try:
        return [r[0] for r in con.execute(SQL, (' AND '.join('"' + t.replace('"', '""') + '"' for t in terms),))]
    finally:
        con.close()


def new_search(db, q):
    with mock.patch.object(library, 'DB', Path(db)):
        return [r['doc_id'] for r in library.search(q)]


def vocabulary(db):
    con = sqlite3.connect(db)
    try:
        con.execute("CREATE VIRTUAL TABLE temp.v USING fts5vocab('main','pages','row')")
        return {r[0] for r in con.execute('SELECT term FROM temp.v')}
    finally:
        con.close()


def load_libq():
    spec = importlib.util.spec_from_file_location('libq_under_test', ROOT / 'tools' / 'libq.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Split(unittest.TestCase):
    """query_terms against the old regular expressions, character by character over the whole of Unicode."""
    @classmethod
    def setUpClass(cls):
        chars = [chr(c) for c in range(0x110000) if not 0xD800 <= c <= 0xDFFF]
        cls.marks = [c for c in chars if unicodedata.category(c)[0] == 'M']
        cls.no_marks = ' '.join(c for c in chars if unicodedata.category(c)[0] != 'M')   # each character on its own
        cls.everything = ' '.join(chars)

    def test_without_marks_nothing_changes(self):
        self.assertEqual(library.query_terms(self.no_marks), re.findall(r'[\w-]+', self.no_marks))
        self.assertEqual(library.query_terms(self.no_marks, keep="'-"), re.findall(r"[\w'-]+", self.no_marks))
        for q in ENGLISH_QUERIES + ["can't breathe", "o'clock", 'snake_bite first-aid kit', 'água  potável', 'İstanbul ıslak']:
            self.assertEqual(library.query_terms(q), re.findall(r'[\w-]+', q), q)
            self.assertEqual(library.query_terms(q, keep="'-"), re.findall(r"[\w'-]+", q), q)

    def test_marks_stay_in_the_word(self):
        self.assertTrue(self.marks)
        self.assertEqual(library.query_terms(' '.join('a' + m for m in self.marks)), ['a' + m for m in self.marks])
        self.assertEqual(library.query_terms('पानी उबालें'), ['पानी', 'उबालें'])
        self.assertEqual(library.query_terms('น้ำ'), ['น้ำ'])
        self.assertEqual(library.query_terms('حَرْف'), ['حَرْف'])
        self.assertEqual(library.query_terms('שָׁלוֹם'), ['שָׁלוֹם'])
        self.assertEqual(library.query_terms('café noir'), ['café', 'noir'])    # a decomposed é stays whole

    def test_a_mark_alone_is_not_a_word(self):
        """A stray accent between spaces has no token in the index; kept as a word it would make the whole search fail."""
        self.assertEqual(library.query_terms('boil \u0301 water'), ['boil', 'water'])
        self.assertEqual(library.query_terms(' '.join(self.marks)), [])
        self.assertEqual(library.query_terms('\u0301\u0301-'), ['\u0301\u0301-'])     # with a '-' it is a word, as '-' was before

    def test_libq_splits_the_same_way(self):
        self.assertEqual(load_libq().query_terms(self.everything), library.query_terms(self.everything))


class Search(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        d = Path(cls.dir.name)
        pages = HINDI + THAI + ARABIC + HEBREW + LATIN + ENGLISH
        cls.new = make_db(d / 'new.sqlite', library.PAGES_TABLE, pages)
        cls.old = make_db(d / 'old.sqlite', OLD_TABLE, pages)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def test_the_build_makes_the_table_with_marks(self):
        """build() itself, on a made-up catalog in the private library folder: nothing is read from disk to extract."""
        records = [{'id': d, 'title': d, 'collection': 'Hindi', 'category': 'water', 'path': f'documents/{d}.pdf', 'kind': 'pdf',
                    'pages': 1, 'bytes': 1} for d, _ in HINDI]
        text = dict(HINDI)
        with mock.patch.object(library, 'catalog', lambda: (records, [])), \
                mock.patch.object(library, 'extract', lambda r: (r, [text[r['id']]], None)), \
                mock.patch('builtins.print'):
            library.build()
        self.assertTrue(library.DB.is_file())
        self.assertFalse(library.DB.with_suffix('.building.sqlite').exists())
        con = sqlite3.connect(library.DB)
        try:
            sql = con.execute("SELECT sql FROM sqlite_master WHERE name='pages'").fetchone()[0]
        finally:
            con.close()
        self.assertIn("categories 'L* N* Co M*'", sql)
        self.assertNotIn('remove_diacritics', sql)                                      # Latin accents still fold
        self.assertEqual(new_search(library.DB, 'पानी'), ['hi-water'])

    def test_packs_build_the_same_table(self):
        """packaging/build_packs.py makes each pack's index from the pack spec's schema, not from the builder's file."""
        spec = json.loads((ROOT / 'derived' / 'packs' / 'pack-spec.json').read_text(encoding='utf-8'))
        self.assertEqual('CREATE VIRTUAL TABLE pages USING ' + spec['search_index']['schema'], library.PAGES_TABLE)

    def test_a_stray_accent_does_not_empty_the_search(self):
        self.assertEqual(new_search(self.new, 'boil \u0301 water'), new_search(self.new, 'boil water'))
        self.assertEqual(new_search(self.new, 'boil water'), ['en-boil'])

    def test_hindi_words_stay_whole(self):
        self.assertIn('hi-drink', old_search(self.old, 'पानी'))               # the bug: water also found drink
        self.assertEqual(new_search(self.new, 'पानी'), ['hi-water'])
        self.assertEqual(new_search(self.new, 'पीना'), ['hi-drink'])
        self.assertEqual(new_search(self.new, 'उबालें'), ['hi-water'])
        self.assertEqual(new_search(self.new, 'पानी उबालें'), ['hi-water'])
        self.assertTrue({'पानी', 'पीना', 'उबालें'} <= vocabulary(self.new))

    def test_thai(self):
        self.assertEqual(new_search(self.new, 'น้ำ'), ['th-water'])
        self.assertEqual(new_search(self.new, 'นำ'), ['th-lead'])
        self.assertIn('น้ำ', vocabulary(self.new))
        self.assertNotIn('น้ำ', vocabulary(self.old))
        # The limit that stays: a word inside unspaced Thai is not found, before or after. That needs a word segmenter.
        for q in ('น้ำ', 'ดื่ม', 'เดือด'):
            self.assertNotIn('th-sentence', new_search(self.new, q), q)
        self.assertEqual(new_search(self.new, 'ต้มน้ำให้เดือดก่อนดื่ม'), ['th-sentence'])

    def test_vowelled_arabic_and_pointed_hebrew(self):
        self.assertIn('ar-joy', old_search(self.old, 'حَرْف'))              # the bug: any word with ح, ر and ف
        self.assertEqual(new_search(self.new, 'حَرْف'), ['ar-letter'])
        self.assertEqual(new_search(self.new, 'فَرَحٌ'), ['ar-joy'])
        self.assertIn('he-name', old_search(self.old, 'שָׁלוֹם'))
        self.assertEqual(new_search(self.new, 'שָׁלוֹם'), ['he-peace'])
        # Not covered here, and not changed: an unvowelled search (حرفا) does not find vowelled text. That needs the
        # vowel marks removed on both sides, a normalisation step for each language rather than a tokenizer option.

    def test_latin_accents_still_fold(self):
        self.assertEqual(new_search(self.new, 'creme'), ['la-creme'])
        self.assertEqual(new_search(self.new, 'crème'), ['la-creme'])
        self.assertEqual(new_search(self.new, 'café au lait'), ['la-cafe'])        # typed with a separate accent
        self.assertEqual(new_search(self.new, 'Café'), old_search(self.old, 'Café'))
        for q in ('Straße', 'strasse'):                                                 # ß is not folded, before or after
            self.assertEqual(new_search(self.new, q), old_search(self.old, q), q)

    def test_english_finds_what_it_found_before(self):
        for q in ENGLISH_QUERIES:
            self.assertEqual(new_search(self.new, q), old_search(self.old, q), q)
        self.assertEqual(new_search(self.new, 'water'), old_search(self.old, 'water'))
        self.assertGreater(len(new_search(self.new, 'water')), 3)                    # the fixture really is searched

    def test_new_app_with_an_old_index_is_no_worse(self):
        """The app may be updated before its index is rebuilt. Each word is then cut by the old index's own tokenizer and
        matched as a phrase of its pieces, where before the pieces could sit anywhere on the page: the same pages or fewer,
        never losing the page that has the word, and nothing fails."""
        for q in ENGLISH_QUERIES:
            self.assertEqual(new_search(self.old, q), old_search(self.old, q), q)
        for q, page in (('पानी', 'hi-water'), ('पीना', 'hi-drink'), ('उबालें', 'hi-water'), ('पानी उबालें', 'hi-water'),
                        ('น้ำ', 'th-water'), ('حَرْف', 'ar-letter'), ('שָׁלוֹם', 'he-peace'), ('cafe\u0301', 'la-cafe')):
            found = new_search(self.old, q)
            self.assertIn(page, found, q)
            self.assertLessEqual(set(found), set(old_search(self.old, q)), q)
        self.assertEqual(new_search(self.old, 'पानी'), old_search(self.old, 'पानी'))       # still the old wrong match, until rebuilt
        self.assertNotIn('he-name', new_search(self.old, 'שָׁלוֹם'))                       # already one fewer

    def test_the_app_search_splits_the_same_way(self):
        """server.py's query_groups feeds the app's search box and the assistant's retrieval."""
        import server            # here, not at the top, as in test_address_search: test_bridge sets its data folder first
        content, groups = server.query_groups('पानी उबालें')
        self.assertEqual(content, ['पानी', 'उबालें'])
        con = sqlite3.connect(self.new)
        try:
            found = [r[0] for r in con.execute('SELECT doc_id FROM pages WHERE pages MATCH ?', (server.fts_expr(groups),))]
        finally:
            con.close()
        self.assertEqual(found, ['hi-water'])
        for q in ("don't drink flood water", 'drinking-water containers', 'wound_care'):   # English as before
            words = [w.strip("'") for w in re.findall(r"[\w'-]+", q.lower()) if w.strip("'")]
            expected = [w for w in words if w not in server.STOP] or words
            self.assertEqual(server.query_groups(q)[0], expected, q)


class Libq(unittest.TestCase):
    """tools/libq.py, run as a curator runs it, against an index built with the app's own table."""
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.data = Path(cls.dir.name) / 'data'
        lib = cls.data / 'library-data'
        lib.mkdir(parents=True)
        (lib / 'catalog.json').write_text(json.dumps([{'id': d, 'kind': 'pdf', 'title': d} for d, _ in HINDI]), encoding='utf-8')
        con = sqlite3.connect(lib / 'search.sqlite')
        try:
            con.execute(library.PAGES_TABLE)
            for doc, body in HINDI:
                con.execute('INSERT INTO pages VALUES (?,?,?,?,?,?,?)', (doc, doc, 'Hindi', 'water', f'documents/{doc}.pdf', 1, body))
            con.commit()
        finally:
            con.close()

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def test_hindi_search(self):
        env = {k: v for k, v in os.environ.items() if k != 'LASTBOOK_DATA'}
        r = subprocess.run([sys.executable, '-B', str(ROOT / 'tools' / 'libq.py'), '--data', str(self.data), 'search', 'पानी'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, cwd=self.dir.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('hi-water | hi-water | Hindi | pages [1]', r.stdout)
        self.assertNotIn('hi-drink', r.stdout)


if __name__ == '__main__':
    unittest.main()
