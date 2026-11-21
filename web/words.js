/* Word handling for topic search: split, fold and match words in any script, not just a-z.
   Loaded before app.js. No DOM, no network: app/tests/test_topic_search.py runs these same functions in Node. */
(function (root) {
  'use strict';

  // Scripts written without spaces between words. A word in one of these matches anywhere in the text, at any length.
  const NO_SPACES = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}\p{Script=Thai}\p{Script=Lao}\p{Script=Khmer}\p{Script=Myanmar}]/u;
  // Accent marks on Latin letters, once a word is decomposed. Only Latin, the same as the library's FTS5 index (unicode61).
  const LATIN_MARKS = /(\p{Script=Latin})\p{M}+/gu;
  // Anything that isn't a letter, mark or digit separates words, as [^a-z0-9] did for a-z.
  const NOT_WORD = /[^\p{L}\p{M}\p{N}]+/u;

  // The key two texts are compared by. Display text is never changed.
  // Order: lower-case, decompose (NFKD), then remove marks. Decomposing before removing marks is the part that
  // matters: NFC "İ" is one character with no mark to remove, and lower-casing it afterwards gives "i" plus a
  // combining dot (U+0307), so "İstanbul" would miss "istanbul". NFKD also splits é into e + accent.
  // Final ς folds to σ and ß stays, as in FTS5. One deliberate difference: NFKD also folds full-width Latin
  // ("ｗａｔｅｒ", typed on Chinese and Japanese keyboards) to "water", which FTS5 keeps apart.
  function fold(s) {
    return String(s).toLowerCase().normalize('NFKD').replace(LATIN_MARKS, '$1').normalize('NFC').replace(/ς/g, 'σ');
  }

  // Intl.Segmenter is in WebView2, WKWebView (macOS 14+) and WebKitGTK; the fallback below covers older engines
  // and any engine whose constructor throws.
  let seg;   // made once; null where Intl.Segmenter is missing or unusable
  function segmenter() {
    if (seg === undefined) {
      try { seg = typeof Intl !== 'undefined' && Intl.Segmenter ? new Intl.Segmenter(undefined, { granularity: 'word' }) : null }
      catch (e) { seg = null }
    }
    return seg;
  }

  // Words of a text, folded. Segment first, then split each segment wherever there's no letter, mark or digit:
  // the segmenter keeps "water's", "first_aid" and "e.coli" whole, but here they split as they always have
  // (water + s, first + aid, e + coli), and ZWJ, ZWNJ and soft hyphens separate words, as in FTS5.
  // Folding comes after segmenting, so the segmenter sees the text as typed. Every segment is kept and that
  // split drops the spaces and punctuation, rather than trusting isWordLike: JavaScriptCore marks numbers
  // such as 112 as not word-like, V8 does not.
  // Without Intl.Segmenter that split is all there is: every script that uses spaces works, but a run of
  // Chinese or Thai stays one word.
  function splitWords(text) {
    const t = String(text), s = segmenter();
    const raw = s ? Array.from(s.segment(t), x => x.segment) : [t];
    const out = [];
    for (const w of raw) for (const part of w.split(NOT_WORD)) { const f = fold(part); if (f) out.push(f) }
    return out;
  }

  // Words worth searching for, counted in characters rather than UTF-16 units: words in scripts without spaces at
  // any length (水, 净化); two-letter words in scripts without case (आग, אש, دم); otherwise three or more, as before.
  function keep(w) {
    const n = Array.from(w).length;
    return NO_SPACES.test(w) || n > 2 || (n === 2 && /\p{L}/u.test(w) && !/\p{Ll}/u.test(w));
  }
  function queryWords(q, stop) {
    return splitWords(q).filter(w => keep(w) && !(stop && stop.has(w)));
  }

  // A test for one piece of text: does a query word start one of its words? For scripts without spaces,
  // is the word anywhere in it? No RegExp is built from what was typed.
  function matcher(text) {
    const words = splitWords(text), whole = fold(text);
    return w => NO_SPACES.test(w) ? whole.includes(w) : words.some(h => h.startsWith(w));
  }

  // Topic search, scored as before: a word found in a topic's title, short line or keywords counts 1,
  // a word found in one of its choices counts 1.5; topics within 60% of the best score, top 3.
  // A choice's "urgent" phrases ("not breathing") pick that choice for its topic whenever the search names one,
  // even if another choice matches more words ("fractured neck and not breathing"). They don't change the score.
  const cache = new WeakMap();   // topics are replaced, never edited in place
  function topicMatchers(t) {
    let m = cache.get(t);
    if (!m) {
      const shown = (t.choices || []).filter(c => !c.goto);
      m = { hay: matcher([t.title, t.short, ...(t.keywords || [])].join(' ')),
            choices: shown.map(c => ({ c, has: matcher(c.label + ' ' + (c.hint || '')) })),
            urgent: shown.filter(c => c.urgent).map(c => ({ c, phrases: c.urgent.map(splitWords).filter(p => p.length) })),
            phrases: shown.filter(c => c.phrases).map(c => ({ c, phrases: c.phrases.map(parts).filter(p => p.length),
                                                             own: new Set(splitWords(c.label + ' ' + (c.hint || ''))),
                                                             context: (c.context || []).map(splitWords).filter(p => p.length) })) };
      cache.set(t, m);
    }
    return m;
  }
  // Does a phrase's words appear in order, as whole words, among all the search's words (stop words included)?
  function names(all, p) {
    return all.some((_, i) => p.every((w, j) => all[i + j] === w));
  }
  // A phrase written "contractions ... minutes" is parts in order, at most GAP words between one part and the next.
  const GAP = 4;
  function parts(text) { return String(text).split('...').map(splitWords).filter(p => p.length) }
  function namesParts(all, ps, from = 0) {
    if (!ps.length) return true;
    const [p, ...rest] = ps, last = from ? Math.min(from + GAP, all.length) : all.length;
    for (let i = from; i <= last; i++)
      if (p.every((w, j) => all[i + j] === w) && namesParts(all, rest, i + p.length)) return true;
    return false;
  }
  // A choice's phrases count only in context: the search names one, and every other word in it is the choice's own,
  // from its label, its hint or a "context" entry the search names. "the baby is coming" counts; "the baby is coming
  // down with a fever" doesn't, and a word nobody foresaw leaves the search ranked as without the field.
  // Returns the phrase words, and the search's other words that only the choice's label or hint allowed ("bleeding"):
  // guides that find those stay listed. Label and hint words that name nothing else belong in "context" too.
  function namedWords(all, words, { phrases, own, context }) {
    const hit = phrases.filter(ps => namesParts(all, ps)).flat(2);
    const near = context.filter(p => names(all, p)).flat();
    // Every word, short and common ones too ("his water broke", "baby coming from the hospital"); numbers pass.
    const fits = w => hit.includes(w) || own.has(w) || near.includes(w) || /^\d+$/.test(w);
    if (!hit.length || !all.every(fits)) return { hit: [], also: [] };
    return { hit, also: words.filter(w => !hit.includes(w) && !near.includes(w) && !/^\d+$/.test(w)) };
  }
  function rankTopics(q, topics, stop) {
    const words = queryWords(q, stop);
    if (!words.length || !topics) return [];
    const all = splitWords(q), out = [], also = new Set(), found = new Map(), phrased = new Set();
    for (const t of topics) {
      const m = topicMatchers(t);
      // A choice's "phrases" ("water broke") count their words as found for that choice and its guide, but only when the
      // search names the whole phrase in context; on their own, "water" and "broke" still point elsewhere.
      const named = new Map(m.phrases.map(x => {
        const { hit, also: more } = namedWords(all, words, x);
        more.forEach(w => also.add(w));
        if (hit.length) phrased.add(t);
        return [x.c, hit];
      }));
      const inNamed = w => [...named.values()].some(ws => ws.includes(w));
      const s = words.filter(w => m.hay(w) || inNamed(w)).length;
      let best = null, bs = 0, bf = [];
      for (const { c, has } of m.choices) {
        const ws = named.get(c) || [], f = words.filter(w => has(w) || ws.includes(w));
        if (f.length > bs || (ws.length && f.length === bs)) { bs = f.length; best = c; bf = f }    // a choice whose phrase the search names wins a tie
      }
      found.set(t, bf);   // the words the shown choice found
      const u = m.urgent.find(x => x.phrases.some(p => names(all, p)));
      if (u) best = u.c;
      if (s || bs) out.push({ t, c: best, s: s + bs * 1.5, u: !!u });
    }
    out.sort((a, b) => b.s - a.s || phrased.has(b.t) - phrased.has(a.t));   // a guide a phrase picked wins a tie
    // When a phrase picks the first guide, a guide whose shown choice finds the search's other words follows it, even
    // below the cut:
    // "umbilical cord bleeding" shows the pregnancy choice first and Bleeding after it. Without a phrase, as before.
    const kept = o => phrased.has(out[0]?.t) && o !== out[0] && !o.u && found.get(o.t).some(w => also.has(w));
    const shown = [out[0], ...out.filter(kept), ...out.filter(o => o !== out[0] && !kept(o) && o.s >= out[0].s * 0.6)]
      .filter(Boolean);
    // A guide whose urgent phrase the search names comes first, even below the cut ("unconscious in the flood water").
    // Without one, the list is exactly as before.
    const urgent = out.filter(o => o.u);
    return [...urgent, ...shown.filter(o => !o.u)].slice(0, 3).map(({ t, c, s }) => ({ t, c, s }));
  }

  root.SearchWords = Object.freeze({ fold, splitWords, queryWords, matcher, rankTopics, hasSegmenter: () => !!segmenter() });
})(globalThis);
