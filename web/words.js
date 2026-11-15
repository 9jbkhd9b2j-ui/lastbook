/* Word handling for topic search: split, fold and match words in any script, not just a-z.
   Loaded before app.js. No DOM, no network: app/tests/test_topic_search.py runs these same functions in Node. */
(function (root) {
  'use strict';

  // Scripts written without spaces between words. A word in one of these matches anywhere in the text, at any length.
  const NO_SPACES = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}\p{Script=Thai}\p{Script=Lao}\p{Script=Khmer}\p{Script=Myanmar}]/u;
  // Accent marks on Latin letters, once a word is decomposed. Only Latin, the same as the library's FTS5 index (unicode61).
  const LATIN_MARKS = /(\p{Script=Latin})\p{M}+/gu;
  const APOSTROPHE = /['’]/;

  // The key two texts are compared by. Display text is never changed.
  // Order: lower-case, decompose (NFKD), then remove marks. Decomposing before removing marks is the part that
  // matters: NFC "İ" is one character with no mark to remove, and lower-casing it afterwards gives "i" plus a
  // combining dot (U+0307), so "İstanbul" would miss "istanbul". NFKD also splits é into e + accent and turns
  // full-width "ｗ" into "w".
  // ß and final ς fold the way case folding does, so "strasse" finds "Straße" and σ matches ς.
  function fold(s) {
    return String(s).toLowerCase().normalize('NFKD').replace(LATIN_MARKS, '$1').normalize('NFC')
      .replace(/ß/g, 'ss').replace(/ς/g, 'σ');
  }

  let seg;   // made once; null where Intl.Segmenter is missing
  function segmenter() {
    if (seg === undefined) {
      try { seg = typeof Intl !== 'undefined' && Intl.Segmenter ? new Intl.Segmenter(undefined, { granularity: 'word' }) : null }
      catch (e) { seg = null }
    }
    return seg;
  }

  // Words of a text, folded. Apostrophes split a word as they always have here: water's -> water + s, l'eau -> l + eau.
  // Without Intl.Segmenter, anything that is not a letter, mark or digit separates words; that keeps every script
  // that uses spaces, but a run of Chinese or Japanese stays one word.
  function splitWords(text) {
    const s = segmenter();
    const raw = s ? Array.from(s.segment(String(text)), x => x.isWordLike ? x.segment : '')
                  : String(text).split(/[^\p{L}\p{M}\p{N}'’]+/u);
    const out = [];
    for (const w of raw) for (const part of w.split(APOSTROPHE)) { const f = fold(part); if (f) out.push(f) }
    return out;
  }

  // Words worth searching for: Latin, Greek, Cyrillic and similar need three characters or more, counted as
  // characters rather than UTF-16 units; words in scripts without spaces count at any length (水, 净化).
  function queryWords(q, stop) {
    return splitWords(q).filter(w => (NO_SPACES.test(w) || Array.from(w).length > 2) && !(stop && stop.has(w)));
  }

  // A test for one piece of text: does a query word start one of its words? For scripts without spaces,
  // is the word anywhere in it? No RegExp is built from what was typed.
  function matcher(text) {
    const words = splitWords(text), whole = fold(text);
    return w => NO_SPACES.test(w) ? whole.includes(w) : words.some(h => h.startsWith(w));
  }

  // Topic search, scored as before: a word found in a topic's title, short line or keywords counts 1,
  // a word found in one of its choices counts 1.5; topics within 60% of the best score, top 3.
  const cache = new WeakMap();
  function topicMatchers(t) {
    let m = cache.get(t);
    if (!m) {
      m = { hay: matcher([t.title, t.short, ...(t.keywords || [])].join(' ')),
            choices: (t.choices || []).filter(c => !c.goto).map(c => ({ c, has: matcher(c.label + ' ' + (c.hint || '')) })) };
      cache.set(t, m);
    }
    return m;
  }
  function rankTopics(q, topics, stop) {
    const words = queryWords(q, stop);
    if (!words.length || !topics) return [];
    const out = [];
    for (const t of topics) {
      const m = topicMatchers(t);
      const s = words.filter(m.hay).length;
      let best = null, bs = 0;
      for (const { c, has } of m.choices) { const n = words.filter(has).length; if (n > bs) { bs = n; best = c } }
      if (s || bs) out.push({ t, c: best, s: s + bs * 1.5 });
    }
    out.sort((a, b) => b.s - a.s);
    return out.filter(o => o.s >= out[0]?.s * 0.6).slice(0, 3);
  }

  root.SearchWords = Object.freeze({ fold, splitWords, queryWords, matcher, rankTopics, hasSegmenter: () => !!segmenter() });
})(globalThis);
