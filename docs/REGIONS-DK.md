# Detailed maps for Denmark: a proposal

This is a proposal for discussion, not a decision. It answers, for Denmark, the questions [MAPS.md](MAPS.md) asks before
coverage can go beyond the United States: which open source replaces each federal list, under what licence, what a
"state" is there, and how addresses are written. It follows the shape of [REGIONS-DE.md](REGIONS-DE.md),
[REGIONS-TH.md](REGIONS-TH.md) and [REGIONS-FR.md](REGIONS-FR.md) and is meant to feed the same design discussion (issue
#31). The machine-readable version is [regions-dk-proposed.json](regions-dk-proposed.json).

Nothing here changes the app, the engine or a build. No code reads the JSON, and nothing here ships: builds package
`web/` and `content/` only.

**How things were checked.** Research was done on 17 November 2026 by reading the publishers' own pages and public APIs,
without an account. Region boxes were computed from the boundary files, populations were read from Danmarks Statistik's
API, extract sizes came from HTTP HEAD requests, and what the engine does with Danish addresses was found by calling
its functions. Each source carries one of three marks:

- **opened**: the dataset page, licence page, API answer or download listing was opened and read;
- **search only**: the fact was seen in a search result from the publisher's own site, but the page itself was not
  opened;
- **not checked**: the page could not be reached or read, or the question was not looked at; the row says what is
  missing.

## Why Denmark is a different case

Like France, most Danish layers have one national source under one licence: since 16 May 2024 the free geographic and
basic data of the Danish mapping agency (elevation, boundaries, buildings, water, place names and addresses) are under
CC BY 4.0. Two things changed in 2026, and they shape the rest of this proposal:

- **DAWA closed on 1 October 2026.** DAWA was the free, account-free API that most open Danish tooling used for
  addresses and boundaries. Its endpoints (`api.dataforsyningen.dk/regioner`, `/kommuner`, `/adresser`, and
  `dawa.aws.dk`) now answer HTTP 410 Gone (opened). The agency's notice of 2 July 2026 names the replacements:
  Adressevælger for address lookup and Datafordeler for everything else (opened).
- **Datafordeler needs a key.** Its boundary WFS and GraphQL services answer 401 without one (opened). A key is free
  with a login and lasts two years (search only). The elevation model, GeoDanmark and place names are listed as
  needing a key too (opened for the elevation model). A build machine can hold a key; the app never needs one,
  because data comes in through a build tool and ships as a file.

The agency's name also changes. SDFI became Klimadatastyrelsen on 14 August 2024, and Klimadatastyrelsen merges with
DMI on 1 December 2026 into "DMI, Kort og Grunddata" (opened). Credit lines written now will need the new name.

## What a region is

Denmark has 5 regions, made of 98 municipalities (*kommuner*). The proposal is one map region per region, 5 in all,
the level closest to a US state. The regions run health care, which matters here: each has its own number for the
out-of-hours doctor (see "Help points").

Greenland and the Faroe Islands are parts of the Danish realm with home rule. Geofabrik, Overture and the Danish
address register all keep them apart from Denmark (opened), and they are not proposed here. Ertholmene (Christiansø),
east of Bornholm, is outside the municipal division and run by the Ministry of Defence (lex.dk, an encyclopedia; opened), but Danmarks
Statistik counts it in Region Hovedstaden (code 411, 89 people), and so does this proposal.

### Codes

ISO 3166-2:DK gives each region two digits after `DK-`: `DK-81` Nordjylland, `DK-82` Midtjylland, `DK-83` Syddanmark,
`DK-84` Hovedstaden, `DK-85` Sjælland (search only: the ISO site refused automated reading, as REGIONS.md and
REGIONS-TH.md also note).

- **The digits are the national code.** They are the last two digits of the DAGI and CPR region codes 1081 to 1085,
  valid since 1 January 2007, and StatBank's 081 to 085 (Danmarks Statistik, opened). Danish data already uses them.
- **No collision with US codes.** A bare `DK` is not in `STATE_CODES` (`engine/address_search.py`).
- **The part after the hyphen is two digits, not two letters.** The engine accepts an address index only under a
  two-letter name: `engine/setup/manifest.py` line 72 and `engine/setup/install.py` line 267 both require `[A-Z]{2}`.
  This is the same question REGIONS-TH.md raises for `TH-10`, and one answer would serve both.

### Boxes

Each box is the extent of every vertex of the region in **Eurostat GISCO's NUTS 2024 level 2 file at 1:1 million**
(`https://gisco-services.ec.europa.eu/distribution/v2/nuts/distribution/DK0{1..5}-region-01m-4326-2024.geojson`;
NUTS level 2 in Denmark is the five regions; opened). Each box was then widened by 0.15° and rounded outward to 0.01°,
the margin `map_sets.state` uses for US states.

The limits of the method:

- GISCO's boundaries are credited "© EuroGeographics for the administrative boundaries", and its terms are read as
  non-commercial (search only). A box is four numbers, but before a build the boxes should be recomputed from DAGI,
  the national boundary register under CC BY 4.0, which now needs a Datafordeler key.
- A cross-check against OpenStreetMap's region relations (through Nominatim; ODbL) agrees within about 0.03° on every
  edge, except that OSM's Region Hovedstaden ends at 15.157° E and leaves out Ertholmene.

| Code | DAGI code | Name | Municipalities | Box (west, south, east, north) | Box with 0.15° margin |
|---|---|---|---|---|---|
| `DK-81` | 1081 | Region Nordjylland | 11 | 8.2227, 56.5511, 11.1979, 57.7512 | 8.07, 56.40, 11.35, 57.91 |
| `DK-82` | 1082 | Region Midtjylland | 19 | 8.0989, 55.6700, 11.6446, 56.8468 | 7.94, 55.52, 11.80, 57.00 |
| `DK-83` | 1083 | Region Syddanmark | 22 | 8.0781, 54.7246, 10.9545, 55.9541 | 7.92, 54.57, 11.11, 56.11 |
| `DK-84` | 1084 | Region Hovedstaden | 29, and Ertholmene | 11.6958, 54.9876, 15.1943, 56.2008 | 11.54, 54.83, 15.35, 56.36 |
| `DK-85` | 1085 | Region Sjælland | 17 | 10.8896, 54.5625, 12.5540, 55.9964 | 10.73, 54.41, 12.71, 56.15 |

The municipalities of each region are listed in the JSON.

### One place that needs a decision: Bornholm

Bornholm, with 38,484 people, belongs to Region Hovedstaden but lies about 150 km east of Copenhagen (Rønne to the city hall), past the south of
Sweden. It makes the region's box 3.8° wide. Split in two, the region looks like this:

| Part | Box (west, south, east, north) | Box with 0.15° margin |
|---|---|---|
| Hovedstaden west of 14° E (north-east Zealand) | 11.6958, 55.5552, 12.7913, 56.2008 | 11.54, 55.40, 12.95, 56.36 |
| Bornholm and Ertholmene | 14.6864, 54.9876, 15.1943, 55.3261 | 14.53, 54.83, 15.35, 55.48 |

The single box holds most of Skåne in Sweden: Malmö, Lund, Helsingborg, Landskrona, Trelleborg, Ystad and Kristianstad
fall inside it (tested against town coordinates). The Denmark extract stops at the Danish border, so Sweden would be
blank in a map built from it, not mapped; but a source cut by box would pick up Swedish rows. Three options:

- **one map, `DK-84`, cut by the region's outline** rather than its box, so the box is used only for display and the
  spatial index, as REGIONS-FR.md proposes for France;
- **two maps**, north-east Zealand and Bornholm, each with its own small box and id; or
- **Bornholm as an extra download** next to `DK-84`.

This proposal suggests the first, because the region is one unit for health care and emergency numbers.

### Boxes that reach another country, or each other

A state map holds every row inside its box. Tested against town coordinates:

- `DK-84` covers most of Skåne, as above.
- `DK-85` covers Helsingborg in Sweden and the north of Fehmarn in Germany. It also holds Copenhagen and most of
  Hovedstaden west of 14° E, the same way Brandenburg's box holds Berlin in REGIONS-DE.md.
- `DK-83` covers Flensburg and the island of Sylt in Germany.
- `DK-82`'s box holds Vejle, which is in `DK-83`.

The Denmark extract's outline (`denmark.poly`, 80 points; opened) has Christiansø inside it and Malmö, Helsingborg,
Ystad, Flensburg and Kiel outside, so foreign rows come only from sources cut by box.

### Size of each region

Population is Danmarks Statistik's table FOLK1A for 1 October 2026 (2026Q4, updated 10 November 2026; read through
`https://api.statbank.dk/v1/data`, opened). The five regions add up to the country's total, 6,044,001.

| Code | Name | Municipalities | Population, 1 October 2026 |
|---|---|---|---|
| `DK-81` | Region Nordjylland | 11 | 594,293 |
| `DK-82` | Region Midtjylland | 19 | 1,389,638 |
| `DK-83` | Region Syddanmark | 22 | 1,245,181 |
| `DK-84` | Region Hovedstaden | 29 | 1,954,759 |
| `DK-85` | Region Sjælland | 17 | 860,130 |

### OpenStreetMap extract

Geofabrik has one extract for Denmark and no sub-regions (opened; data up to 2026-11-16T21:22:36Z). Every region map
would be cut from it, as PR #80's tool does for Bangkok. Sizes from HEAD requests on 17 November 2026 (opened):

| File | Bytes |
|---|---|
| `denmark-latest.osm.pbf` (dated 17 November; its MD5 matched Geofabrik's `.md5`) | 498,163,345 |
| `denmark-latest-free.gpkg.zip` (dated 16 November) | 841,513,543 |
| `denmark-latest-free.shp.zip` (dated 16 November) | 814,578,465 |

Two open pull requests already cut maps from this extract: #84 lists all of Denmark as `eu-dk`, boxed by Geofabrik's
outline (7.7011, 54.4406, 15.6545, 58.0624), and #35 has a Copenhagen box, `dk-kob` (12.26, 55.38, 12.86, 55.98).
