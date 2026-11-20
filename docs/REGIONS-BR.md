# Detailed maps for Brazil: a proposal

This is a proposal for discussion, not a decision. It answers, for Brazil, the questions [MAPS.md](MAPS.md) asks before
coverage can go beyond the United States: which open source replaces each federal list, under what licence, what a
"state" is there, and how addresses are written. It follows the shape of [REGIONS-MX.md](REGIONS-MX.md) and
[REGIONS-AR.md](REGIONS-AR.md) and is meant to feed the same design discussion (issues #23, #25, #31 and #54). The
machine-readable version is [regions-br-proposed.json](regions-br-proposed.json), and a Portuguese translation is
[REGIONS-BR.pt.md](REGIONS-BR.pt.md).

Nothing here changes the app, the engine or a build. No code reads the JSON, and nothing here ships: builds package
`web/` and `content/` only.

**How things were checked.** Research was done on 20 November 2026. Each source carries one of three marks:

- **opened**: the dataset or licence page itself was opened and read;
- **search only**: the fact was seen in a search result or a search snippet, but the page itself was not opened;
- **not checked**: the page could not be reached or read, or it was not looked at in this proposal; the row says what
  is missing.

The state boxes were computed from IBGE's own state polygons, read through IBGE's public malhas API (opened). The
licence of those polygons is **not** settled (see "Licence notes"), so the boxes are a proposal until that is.

## Why Brazil is a useful case

Brazil has its own national scheme for emergency numbers (190, 192, 193 and 199, see "Help points"), and its states use
two-letter codes that, in one case, collide with US codes in this repository. Brazil has no open postal-code
(CEP) area layer that was checked for this proposal. Two things are different from the US and worth deciding once,
because other Portuguese- and Spanish-speaking countries will raise them too:

- **Two-letter codes collide with US codes.** Seven Brazilian codes are also US state codes in `STATE_CODES`
  (`engine/address_search.py`). This is the main reason for hyphenated codes below.
- **No checked CEP-to-state table.** The eight-digit CEP (*Código de Endereçamento Postal*) on an address is what address
  search needs, but no official CEP-to-state table was checked, so addresses cannot be split by state yet.

## What a region is

Brazil has 26 states (*estados*) and the Federal District (*Distrito Federal*, DF). The proposal is one region per
unit, 27 in all, the same level as a US state. DF is a federal unit with its own government, so it is kept as its own
region here; see the note on DF and Goiás below.

### Codes

ISO 3166-2:BR gives each unit the prefix `BR-` and two letters: `BR-SP` São Paulo, `BR-RJ` Rio de Janeiro, `BR-DF` Distrito
Federal, and so on (the 27 codes were read from the Wikipedia article "ISO 3166-2:BR", which lists the names as in ISO 3166-2 from the
ISO 3166/MA; the ISO Online Browsing Platform itself was not opened).

- **Seven two-letter codes collide with US codes.** The two-letter Brazilian codes `AL` (Alagoas), `MA` (Maranhão),
  `MS` (Mato Grosso do Sul), `MT` (Mato Grosso), `PA` (Pará), `PR` (Paraná) and `SC` (Santa Catarina) are also codes in
  `STATE_CODES` (`engine/address_search.py`) for Alabama, Massachusetts, Mississippi, Montana, Pennsylvania, Puerto
  Rico and South Carolina. A bare `PA` already means Pennsylvania in address search. A Brazilian `PA` would be read the
  same way, so the Brazilian codes cannot be used bare.
- **The hyphenated code is needed for the file name too.** `carry_over()` in `engine/setup/install.py` keeps only
  address indexes named `[A-Z]{2}.sqlite` or `.json` (line 335). An index named `BR-SP.sqlite` would be left behind in
  the old library without a message, as REGIONS-MX.md also notes for `MX-AGU`. The change to `carry_over` would be a
  maintainer's decision.

### Boxes

The boxes were computed from IBGE's state polygons (malhas territoriais, state layer, "malha estadual"), read through
IBGE's public malhas API at maximum quality (`qualidade=maxima`) on 20 November 2026 (opened). The API returns one
feature per unit: 27 features, with 1 to 17 polygons each (Pará has 17, and Rio de Janeiro 15). Every vertex of every
polygon was read; the bounding box was then widened by 0.15° and rounded outward to 0.01°, the same margin
`map_sets.state` uses for US states.

As a check, the outer edges match Brazil's known extreme points as recalled from memory (not checked against a published
list in this pass): the northern tip of Roraima (about 5.27° N), the southern tip of Rio Grande do Sul (about 33.75° S),
the eastern tip of Paraíba (about 34.79° W) and the western edge of Acre (about 73.99° W). Those four edges are set by
those states, and the table matches them.

| Code | IBGE | Name | Box (west, south, east, north) | Box with 0.15° margin |
|---|---|---|---|---|
| `BR-RO` | 11 | Rondônia | -66.8103, -13.6937, -59.7744, -7.9759 | -66.97, -13.85, -59.62, -7.82 |
| `BR-AC` | 12 | Acre | -73.9904, -11.1456, -66.6239, -7.1118 | -74.15, -11.30, -66.47, -6.96 |
| `BR-AM` | 13 | Amazonas | -73.8016, -9.8180, -56.0976, 2.2466 | -73.96, -9.97, -55.94, 2.40 |
| `BR-RR` | 14 | Roraima | -64.8253, -1.5806, -58.8869, 5.2718 | -64.98, -1.74, -58.73, 5.43 |
| `BR-PA` | 15 | Pará | -58.8983, -9.8412, -46.0618, 2.5910 | -59.05, -10.00, -45.91, 2.75 |
| `BR-AP` | 16 | Amapá | -54.8763, -1.2362, -49.8758, 4.5088 | -55.03, -1.39, -49.72, 4.66 |
| `BR-TO` | 17 | Tocantins | -50.7421, -13.4682, -45.6993, -5.1684 | -50.90, -13.62, -45.54, -5.01 |
| `BR-MA` | 21 | Maranhão | -48.7552, -10.2596, -41.7967, -1.0495 | -48.91, -10.41, -41.64, -0.89 |
| `BR-PI` | 22 | Piauí | -46.0282, -10.9288, -40.3705, -2.7499 | -46.18, -11.08, -40.22, -2.59 |
| `BR-CE` | 23 | Ceará | -41.4233, -7.8576, -37.2527, -2.7843 | -41.58, -8.01, -37.10, -2.63 |
| `BR-RN` | 24 | Rio Grande do Norte | -38.5821, -6.9827, -34.9685, -4.8314 | -38.74, -7.14, -34.81, -4.68 |
| `BR-PB` | 25 | Paraíba | -38.7652, -8.3030, -34.7932, -6.0259 | -38.92, -8.46, -34.64, -5.87 |
| `BR-PE` | 26 | Pernambuco | -41.3583, -9.4829, -32.3971, -3.8358 | -41.51, -9.64, -32.24, -3.68 |
| `BR-AL` | 27 | Alagoas | -38.2376, -10.4986, -35.1527, -8.8161 | -38.39, -10.65, -35.00, -8.66 |
| `BR-SE` | 28 | Sergipe | -38.2450, -11.5685, -36.3959, -9.5150 | -38.40, -11.72, -36.24, -9.36 |
| `BR-BA` | 29 | Bahia | -46.5768, -18.3372, -37.3411, -8.5328 | -46.73, -18.49, -37.19, -8.38 |
| `BR-MG` | 31 | Minas Gerais | -51.0461, -22.9228, -39.8568, -14.2333 | -51.20, -23.08, -39.70, -14.08 |
| `BR-ES` | 32 | Espírito Santo | -41.8796, -21.3011, -39.6678, -17.8919 | -42.03, -21.46, -39.51, -17.74 |
| `BR-RJ` | 33 | Rio de Janeiro | -44.8893, -23.3676, -40.9579, -20.7632 | -45.04, -23.52, -40.80, -20.61 |
| `BR-SP` | 35 | São Paulo | -53.1101, -25.3089, -44.1614, -19.7799 | -53.27, -25.46, -44.01, -19.62 |
| `BR-PR` | 41 | Paraná | -54.6199, -26.7171, -48.0235, -22.5163 | -54.77, -26.87, -47.87, -22.36 |
| `BR-SC` | 42 | Santa Catarina | -53.8371, -29.3551, -48.3585, -25.9558 | -53.99, -29.51, -48.20, -25.80 |
| `BR-RS` | 43 | Rio Grande do Sul | -57.6497, -33.7508, -49.6914, -27.0823 | -57.80, -33.91, -49.54, -26.93 |
| `BR-MS` | 50 | Mato Grosso do Sul | -58.1686, -24.0682, -50.9242, -17.1663 | -58.32, -24.22, -50.77, -17.01 |
| `BR-MT` | 51 | Mato Grosso | -61.6334, -18.0416, -50.2248, -7.3490 | -61.79, -18.20, -50.07, -7.19 |
| `BR-GO` | 52 | Goiás | -53.2485, -19.4981, -45.9072, -12.3954 | -53.40, -19.65, -45.75, -12.24 |
| `BR-DF` | 53 | Distrito Federal | -48.2857, -16.0500, -47.3085, -15.5018 | -48.44, -16.20, -47.15, -15.35 |

Notes:

- **DF inside Goiás.** The DF box lies entirely inside the `BR-GO` box, the same case as CABA inside Buenos Aires in
  REGIONS-AR.md. The Brasília metropolitan area crosses the DF and Goiás border, so a person there who installs only one
  of the two maps misses part of their area. Options: keep the two maps separate (simple), or let the `BR-GO` map include
  `BR-DF` (matches how people move in the area, as REGIONS-AR.md suggests for CABA). This proposal does not decide it.
- **Large boxes.** Amazonas, Pará and Mato Grosso are the largest boxes. Their maps will be large, and the
  size of the download has not been estimated for this proposal.
- **Offshore islands.** The IBGE polygons were checked for every unit: any polygon more than 0.5° from the unit's largest
  polygon was listed. Two detached islands are in the polygons, and two offshore islands are not in them at all.
  - **Fernando de Noronha** (`BR-PE`, about 3.4° east of the mainland) is **kept** in the PE box, because it is a
    Pernambuco island with people living on it, and no other map would show it. The PE box reaches -32.40° W for it.
    Without Noronha the box would end at -34.81° W; the cost is about 2.4° of mostly ocean.
  - **Trindade and Martim Vaz** (`BR-ES`, about 10° east of the mainland, around 20.5° S) are **left out** of the ES
    box. Keeping them would stretch the ES box from -39.67° W to -29.30° W, about 13° wide and mostly ocean, so the
    box would stop being useful for the mainland. Whether they need a map of their own is an open question. No resident
    population was checked for them.
  - **Atol das Rocas** (RN) and **São Pedro e São Paulo** (PE) are **not in the IBGE state polygons**, so no box
    includes them and nothing has to be cut. Whether either should have a map is an open question.
  - The rule used here: an island goes in its state's box only if it is part of the state's IBGE polygon **and** either
    is close to the mainland or has people living on it. Only Noronha passes that test. This is a proposal, not a
    settled rule.
- **Overlapping boxes.** Boxes follow each state's own outline, so neighbouring boxes overlap along borders. The
  overlap is expected and is the same as for the US and Mexico.

## Sources, layer by layer

| Layer (file) | US source today | Proposed for Brazil | Publisher | Licence | Checked |
|---|---|---|---|---|---|
| Terrain (`terrain.sqlite`) | USGS 3DEP | Copernicus DEM GLO-30, as for the fallback in REGIONS-AR.md and REGIONS-MX.md; no Brazil-specific national elevation product was checked here | ESA / Airbus | Copernicus licence | Copernicus as in REGIONS-AR.md; Brazil-specific product not checked |
| Water (`water.sqlite`) | NHD | OSM waterways and water areas from Geofabrik's Brazil extract; IBGE hydrography not checked for this proposal | OSM contributors | ODbL | OSM as for US; IBGE not checked |
| Dams | NID | No open national dam list was identified in this pass. OSM `waterway=dam` as a fallback, not counted | OSM contributors | ODbL | not checked |
| Crops (`crops.sqlite`) | USDA Cropland Data Layer | MapBiomas land cover is a candidate, because it covers Brazil's crop classes, but its licence and class list were not checked | MapBiomas | not checked | not checked |
| Buildings (`buildings.sqlite`) | Microsoft US footprints, OSM heights | Google Open Buildings V3, as in REGIONS-MX.md; Brazil coverage not re-checked here; OSM to fill gaps | Google; OSM contributors | CC BY 4.0; ODbL | as REGIONS-MX.md; not re-opened for Brazil |
| Places (`places.sqlite`) | GNIS, Census gazetteers, OSM | IBGE malhas for states, municipalities and localities (the state layer was used for the boxes); OSM named places | IBGE; OSM contributors | IBGE terms unclear (see Licence notes); ODbL | state layer opened; licence not confirmed |
| Addresses (`addresses/<code>.sqlite`) | Overture addresses | Overture addresses: 89,887,635 Brazilian rows in the publisher's per-country table; per-state counts not computed; no open CEP area table found | Overture Maps Foundation; Correios (CEP) | Overture attribution not re-read; CEP not open | Overture guide opened 20 Nov 2026; Correios guide search only |
| Points of interest (`poi` rows) | OSM | OSM, as today, plus the lists in "Help points" | OSM contributors | ODbL | not counted here |

## Licence notes and attribution

- **gov.br content.** The footer of gov.br pages says all content is published under *Creative Commons
  Atribuição-SemDerivações 3.0 Não Adaptada* (CC BY-ND 3.0 Brazil) (opened, read on 20 November 2026 on the gov.br
  "Sobre o portal" page and on the federal SAMU page). The "no derivatives" part means a page cannot be adapted into a
  library guide, so gov.br pages are not proposed as copy sources. Quoting a single number with its source is a question
  for maintainers, not a decision made here.
- **IBGE.** No explicit open licence was found for the malhas. IBGE publishes a technical and legal note with each
  product ("Informações técnicas e legais para a utilização dos dados publicados") (search only, not opened). The BC250
  base map terms describe a restricted use for support of work projects, not an open licence (search only, not opened).
  Until the note for the state malha is read, the IBGE layers are **not proposed for a build**. The boxes in this file
  are numbers computed from the data, and they should be re-checked against the licence before anyone relies on them.

## Help points

The emergency numbers are the part people need most, and they are the same across the country. They are set by Anatel
(the telecoms regulator), not by each state.

| Service | Number | Source for the number | Location data |
|---|---|---|---|
| Ambulance (SAMU) | 192 | gov.br, "SAMU 192: saiba quando acionar o serviço de urgência", published 29 August 2022, updated 26 October 2026 (opened) | not checked |
| Fire (Corpo de Bombeiros) | 193 | Anatel page, opened 20 Nov 2026: "Corpo de Bombeiros 193" | state fire services: not checked |
| Police (Polícia Militar) | 190 | Anatel page, opened 20 Nov 2026: "Polícia Militar 190" | state police: not checked |
| Police, mobile phones only (Polícia Militar) | 112 and 911 | Anatel page, opened 20 Nov 2026: "Polícia Militar - SOMENTE CELULAR 112/911" | state police: not checked |
| Civil defence (Defesa Civil) | 199 | Anatel page, opened 20 Nov 2026: "Defesa Civil 199" | not checked |

Notes:

- The Anatel designation of these codes dates from the 2004 numbering act (search snippet only; the act's own page was
  not found at the URL returned, so it was not read).
- Health establishments with coordinates (the national register, CNES) and fire or police stations were not checked for
  this proposal, so no counts are given for them.
- The number table itself belongs to [issue #261](https://github.com/Immortal-Protocols/lastbook/issues/261), not to
  this map proposal. It is listed here so that the map and the number table agree.

## Checking a map change

- A change to a layer in `web/map.js` is a change you can see: include screenshots in light and dark mode.
- A change to a pack or map tool: `packaging/test_pack_tools.py` and `packaging/scan_pack.py` check what a map set may
  hold, and `scan_pack.py` lists the allowed files under `derived/geo/` (`GEO_FILES`).
- Nothing a contributor adds may make the app open a connection. New data comes in through a build tool and ships as a
  file.

## Addresses in Overture, from the publisher's guide

- **Brazil: 89,887,635 addresses**, in the per-country table of the Overture addresses guide
  (docs.overturemaps.org/guides/addresses/, opened 20 November 2026). This is the publisher's count, not one made for
  this proposal. The same table lists the US and Mexico (Mexico 30,726,687, as REGIONS-MX.md reads it).
- Per-state counts were not computed. The first digit of a CEP is not a state code (see below), so splitting on it
  would put addresses in the wrong state.
- The Overture guide says address IDs are not stable enough to register in GERS, so IDs may change between releases.
  A build would need a fixed release.

## How addresses are written

Read from the Correios' *Guia Técnico de Endereçamento de Correspondências* (version 1.4, 2021) and the Correios
addressing guide page: **search snippets only**; the PDF was not opened.

- **Postcode (CEP).** Eight digits, written `00000-000` with a hyphen after the fifth digit, for example `01311-000`
  (the Correios example). The Correios API accepts eight digits without the hyphen. Keep it as text, because leading
  zeros occur.
- **Order.** Street type, street name and number, then complement and neighbourhood, then city and state (UF), with
  the CEP last. The Correios guide puts the CEP alone on the last line of a hand-written address.
- **No number.** Correios writes `SN` (*sem número*, "no number"). The CEP complement is then `00000` (search snippet
  only).
- **The CEP is not a state code.** The first digit is a broad region, not a state, and no CEP-to-state table was
  checked. Address indexes cannot be split by state until one is found or a state polygon is used.
- **What the code does now** (read in this repository, 20 November 2026):
  - `tools/build_addresses.py` keeps only `country = 'US'`; the Brazilian rows would need the country changed.
  - `normalize()` in `engine/address_search.py` replaces every character outside `a-z` and `0-9` with a space, so
    Portuguese accents split words: "Ação" becomes "a o". Accent folding would be needed, as noted for Spanish in
    REGIONS-MX.md.
  - `is_address_query()` needs a number first, so "Rua do Lago 50, 01311" is not treated as an address today.

## Still undecided

Each of these needs the maintainers' decision before any code changes.

1. **Codes in setup.** Whether `BR-AC` and the others are acceptable as a manifest `id`, and the `carry_over()` rule in
   `engine/setup/install.py` (line 335), which keeps only `[A-Z]{2}` index names.
2. **DF and Goiás.** Separate maps, or the Goiás map includes DF (the box overlap, as for CABA in REGIONS-AR.md).
3. **Trindade and Martim Vaz.** A separate small map, or no map. No resident population was checked.
4. **Atol das Rocas and São Pedro e São Paulo.** Not in the IBGE polygons; whether either should have a map.
5. **IBGE licence.** Whether the technical and legal note for the state malha allows a copy in a build.
6. **CEP.** An open CEP-area or CEP-to-state source with clear rights. Without one, address search cannot split by state.
7. **Crop classes.** MapBiomas is a candidate; its licence and class list were not checked, and the crop kinds in
   `tools/build_crops.py` have no Brazilian equivalents yet.
8. **Overlapping boxes.** Boxes follow each state's outline, so neighbours overlap along borders. Whether that is
   acceptable is the same question as in REGIONS-MX.md.

## What was checked, and what was not

- **Opened on 20 November 2026:** the IBGE malhas API, state polygons at maximum quality, for all 27 units; the gov.br
  "Sobre o portal" page and the federal SAMU 192 article (footer licence CC BY-ND 3.0 Brazil); the Anatel public-utility
  and emergency codes page (190, 192, 193, 199, and 112/911 listed as mobile only); the Overture addresses guide
  (Brazil 89,887,635); the Wikipedia article "ISO 3166-2:BR" (27 codes, names from the ISO 3166/MA).
- **Computed on 20 November 2026:** the 27 tight boxes and the 0.15° margins (floor for west and south, ceiling for
  east and north, to 0.01°); the detached-island check across all 27 units; the Espírito Santo box without Trindade and
  Martim Vaz.
- **Seen only in search results:** the IBGE technical and legal note and the BC250 terms (restricted use); the Correios
  addressing guide; a 2017 federal open-data resolution that lists CC0, PDDL, CC BY 4.0 and ODbL as acceptable.
- **Not checked:** the ISO Online Browsing Platform (iso.org); the IBGE technical and legal note itself; the CNES health
  register; state fire and police station lists; MapBiomas licence and class list; Google Open Buildings coverage for
  Brazil; OSM counts for Brazil; per-state Overture address counts; the populations of Trindade and Martim Vaz.

