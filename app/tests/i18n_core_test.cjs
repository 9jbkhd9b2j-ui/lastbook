const assert = require("node:assert/strict");
const { test } = require("node:test");
const { runInNewContext } = require("node:vm");
const createI18n = require("../../web/i18n-core.js");

const catalogs = {
  en: {
    greeting: "Hello, {name}",
    files: { "=0": "No files", one: "{count} file", other: "{count} files" },
    fallback: "English only",
    caption: "Picture {position}",
  },
  "es-419": {
    greeting: "Hola, {name}",
    files: { "=0": "No hay archivos", one: "{count} archivo", other: "{count} archivos" },
    caption: "Imagen {position}",
  },
  "es-AR": { greeting: "Buenas, {name}" },
};

const inheritance = { "es-UY": ["es-419"], "es-AR": ["es-419"], "es-CL": ["es-419"] };

function translator(locale) {
  return createI18n({ catalogs, locale, fallbacks: inheritance });
}

test("regional Spanish routes to es-419, with exact catalogs and English fallback", () => {
  for (const locale of ["ES-uy", "es-CL", "es-UY-u-nu-latn", "es-419"]) {
    assert.deepEqual(translator(locale).resolve("greeting", { name: "Ana" }),
      { text: "Hola, Ana", locale: "es-419" });
  }
  const i18n = translator("es-AR");
  assert.equal(i18n.t("greeting", { name: "Ana" }), "Buenas, Ana");
  assert.equal(i18n.t("files", { count: 2 }), "2 archivos");
  assert.equal(i18n.t("fallback"), "English only");
  for (const locale of ["fr-CA", "es-ES", "es", "es-MX", "es-ES-u-nu-arab"]) {
    i18n.setLocale(locale);
    assert.equal(i18n.t("greeting", { name: "Ana" }), "Hello, Ana");
    assert.equal(i18n.catalogLocale, "en");
  }
  i18n.setLocale("es-UY-u-nu-arab");
  assert.equal(i18n.catalogLocale, "es-419");
  assert.equal(i18n.locale, "es-UY-u-nu-arab");
  assert.equal(i18n.t("constructor"), undefined);
});

test("plural selection uses exact counts and the grammar of the matched catalog", () => {
  for (const [locale, expected] of [
    ["en", ["No files", "1 file", "2 files"]],
    ["es-UY", ["No hay archivos", "1 archivo", "2 archivos"]],
  ]) {
    const i18n = translator(locale);
    assert.deepEqual([0, 1, 2].map(count => i18n.t("files", { count })), expected);
    // No usable count: the "other" form renders and nothing throws.
    assert.equal(i18n.t("files", { count: "2" }), expected[2].replace(/^\d+/, "2"));
    assert.equal(i18n.t("files", { count: Infinity }), expected[2].replace(/^\d+/, "Infinity"));
  }
  const i18n = createI18n({
    locale: "ja", fallbackLocale: "en",
    catalogs: { en: catalogs.en, ja: { files: catalogs.en.files } },
  });
  assert.equal(i18n.t("files", { count: 1 }), "1 files");
});

test("interpolation performs one plain-text pass over own primitive parameters", () => {
  const i18n = translator("en");
  const input = '<img src=x onerror="alert(1)">{name}$&';
  assert.equal(i18n.t("greeting", { name: input }), "Hello, " + input);
  for (const params of [
    Object.create({ name: "Inherited" }),
    { get name() { assert.fail("parameter getter ran"); } },
    { name: { toString() { assert.fail("parameter was coerced"); } } },
  ]) assert.equal(i18n.t("greeting", params), "Hello, {name}");
});

test("browser preference negotiation ignores unsupported earlier languages", () => {
  const i18n = translator("en");
  assert.equal(i18n.chooseLocale(["fr-CA", "es-UY"]), "es-UY");
  assert.equal(i18n.chooseLocale(["es-ES", "es-CL"]), "es-CL");
  assert.equal(i18n.chooseLocale(["es-ES", "es"]), "en");
  assert.equal(i18n.usePreferredLocales(["fr-CA", "es-CL"]), "es-CL");
  assert.equal(i18n.t("greeting", { name: "Ana" }), "Hola, Ana");
  assert.equal(i18n.chooseLocale(["en-US", "es-UY"]), "en-US");
  assert.equal(i18n.chooseLocale(["malformed_tag", "fr"]), "en");
  assert.equal(i18n.chooseLocale([]), "en");
  assert.equal(i18n.locale, "es-CL"); // chooseLocale is non-mutating
  assert.equal(i18n.usePreferredLocales(["en-US", "es-UY"]), "en-US");
  assert.equal(i18n.t("greeting", { name: "Ana" }), "Hello, Ana");
  assert.throws(() => i18n.setLocale("malformed_tag"), RangeError);
  assert.equal(i18n.locale, "en-US"); // invalid selection is atomic
  assert.deepEqual(i18n.supportedLocales, ["en", "es-419", "es-AR"]);
});

test("plural grammar and count formatting agree for fractional quantities", () => {
  assert.equal(translator("en").t("files", { count: 1.0004 }), "1 file");
  assert.equal(translator("en").t("files", { count: 1.001 }), "1.001 files");
  assert.equal(translator("es-UY").t("files", { count: 1.001 }),
    new Intl.NumberFormat("es-UY").format(1.001) + " archivos");
  for (const count of [NaN, Infinity, "2", undefined]) {
    assert.doesNotThrow(() => translator("en").t("files", { count }));
  }
});

test("a plural message without a numeric count falls back to its other form", () => {
  const en = translator("en");
  assert.equal(en.t("files"), "{count} files");
  assert.equal(en.t("files", {}), "{count} files");
  assert.equal(en.t("files", null), "{count} files");
  assert.equal(en.resolve("files", { count: undefined }).locale, "en");
  assert.equal(translator("es-UY").t("files"), "{count} archivos");
  assert.equal(en.t("files", { count: "many" }), "many files");
  assert.equal(en.t("files", { count: 1 }), "1 file");
});

test("explicit routes to the default never hide later supported preferences", () => {
  const i18n = createI18n({ catalogs, fallbacks: { fr: ["en"], ...inheritance } });
  assert.equal(i18n.chooseLocale(["fr", "es-AR"]), "es-AR");
  assert.equal(i18n.chooseLocale(["fr-CA", "es-UY"]), "es-UY");
  assert.equal(i18n.chooseLocale(["es-ES", "es-CL"]), "es-CL");
  assert.equal(i18n.chooseLocale(["es-ES", "es"]), "en");
  assert.equal(i18n.chooseLocale(["en-US", "es-AR"]), "en-US");
  assert.equal(i18n.chooseLocale(["en", "es-AR"]), "en");
  assert.equal(i18n.chooseLocale(["fr"]), "en");
});

test("plural grammar follows the message while count respects selected numbering", () => {
  const spanish = translator("es-UY-u-nu-arab");
  assert.equal(spanish.t("files", { count: 1.0004 }),
    new Intl.NumberFormat(spanish.locale).format(1.0004) + " archivo");
  assert.equal(spanish.t("files", { count: 2.001 }),
    new Intl.NumberFormat(spanish.locale).format(2.001) + " archivos");
  const en = { quantity: { one: "one {count}", other: "other {count}" } };
  const i18n = createI18n({ locale: "fa-IR-u-nu-latn", catalogs: { en, fa: en } });
  assert.equal(i18n.t("quantity", { count: 0 }), "one \u20680\u2069"); // Persian zero is one
  assert.equal(i18n.t("quantity", { count: 1.0004 }), "one \u20681\u2069");
  assert.equal(i18n.t("quantity", { count: 2.125 }), "other \u20682.125\u2069");
  i18n.setLocale("ja-JP-u-nu-fullwide"); // English fallback still uses English grammar
  assert.equal(i18n.t("quantity", { count: 1 }), "one １");
});

test("exact plural integers reject unsafe precision and cover the safe boundary", () => {
  for (const form of ["=1000000000000000000000", "=9007199254740992", "=9007199254740993", "=1e21", "=-1", "=1.5", "=01"]) {
    assert.throws(() => createI18n({ catalogs: { en: { n: { [form]: "exact", other: "other" } } } }), TypeError);
  }
  const i18n = createI18n({ catalogs: { en: { n: {
    "=9007199254740991": "exact", "=0": "zero", other: "other {count}",
  } } } });
  assert.equal(i18n.t("n", { count: Number.MAX_SAFE_INTEGER }), "exact");
  assert.equal(i18n.t("n", { count: -0 }), "zero");
  assert.match(i18n.t("n", { count: 1e21 }), /^other /);
});

test("catalogs have explicit contracts and reject accessors or unexpected shapes", () => {
  const bad = [
    { en: { hello: "Hello, {name}" }, es: { hello: "Hola, {persona}" } },
    { en: { hello: "Hello" }, es: { surprise: "Sorpresa" } },
    { en: { hello: "   " } },
    { en: { n: { "=0": "Nothing", other: "{count} items" } }, es: { n: { other: "{count} cosas" } } },
    { en: { hello: "{incomplete" } },
    { en: { hello: {} } },
    { en: { hello: { one: "One" } } },
    { en: { hello: { other: "{count} file", one: "{count} {x} file" } } },
    { en: { hello: { other: "{count} file", invalid: "{count} files" } } },
    { en: { get hello() { assert.fail("catalog getter executed"); } } },
    { en: { hello: ["A", "B"] } },
    { en: { hello: "Hi" }, EN: { hello: "Hello" } },
  ];
  for (const catalogs of bad) {
    assert.throws(() => createI18n({ catalogs }), TypeError);
  }
  assert.throws(() => createI18n({ catalogs: { fr: { hi: "Bonjour" } } }), /Missing fallback catalog/);
  assert.throws(() => createI18n({ catalogs: { en: {} } }), /Missing fallback catalog/);
  assert.throws(() => createI18n({
    catalogs: { en: { hi: "Hi" } }, fallbacks: { fr: "en" },
  }), TypeError);
  const original = { en: { hello: "Hi" } };
  const i18n = createI18n({ catalogs: original });
  original.en.hello = "Changed later";
  assert.equal(i18n.t("hello"), "Hi");
});

test("number and date formatting use the selected locale", () => {
  const i18n = translator("es-UY");
  assert.equal(i18n.number(1234.5), new Intl.NumberFormat("es-UY").format(1234.5));
  const date = new Date("2024-01-15T12:00:00.000Z");
  const options = { timeZone: "UTC", dateStyle: "short" };
  assert.equal(i18n.date(date, options), new Intl.DateTimeFormat("es-UY", options).format(date));
});

test("cyclic fallback routes terminate and invalid catalogs never execute accessors", () => {
  const i18n = createI18n({ catalogs, locale: "es-UY", fallbacks: { ...inheritance, "es-419": ["es-UY"] } });
  assert.equal(i18n.t("greeting", { name: "Ana" }), "Hola, Ana");
  const hidden = {};
  Object.defineProperty(hidden, "greeting", { value: "Hi" });
  const symbol = { [Symbol("key")]: "Hi" };
  const inherited = Object.create({ greeting: "Hi" });
  for (const en of [hidden, symbol, inherited]) assert.throws(() => createI18n({ catalogs: { en } }), TypeError);
});

test("prototype-named keys and plural forms stay isolated from the source catalogue", () => {
  const original = {
    en: { constructor: "A constructor", files: { other: "{count} files" } },
    "es-419": { files: { other: "{count} archivos" } },
  };
  const i18n = createI18n({ catalogs: original, locale: "es-419" });
  original["es-419"].files.other = "changed";
  delete original.en.constructor;
  assert.equal(i18n.t("files", { count: 2 }), "2 archivos");
  assert.equal(i18n.t("constructor"), "A constructor");
  assert.equal(i18n.t("toString"), undefined);
  assert.throws(() => createI18n({ catalogs: JSON.parse('{"en":{"__proto__":"invalid"}}') }), TypeError);
});
