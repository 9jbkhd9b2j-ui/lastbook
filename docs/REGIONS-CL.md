# Detailed maps for Chile: a proposal

This is a proposal for discussion, not a decision. It answers, for Chile, the questions [MAPS.md](MAPS.md) asks before
coverage can go beyond the United States: which open source replaces each federal list, under what licence, what a
"state" is there, and how addresses are written. It follows the shape of [REGIONS.md](REGIONS.md),
[REGIONS-AR.md](REGIONS-AR.md) and [REGIONS-DE.md](REGIONS-DE.md) and is meant to feed the same design discussion
(issues #23, #25 and #31). The machine-readable version is [regions-cl-proposed.json](regions-cl-proposed.json).

Nothing here changes the app, the engine or a build. No code reads the JSON, and nothing here ships: builds package
`web/` and `content/` only.

**How things were checked.** Research was done on 17 November 2026. Each source carries one of three marks:

- **opened**: the page or file itself was opened and read;
- **search only**: the fact was seen in a search result from the publisher's site, but the page itself was not opened;
- **not checked**: the page could not be reached or read; the row says what is missing.

## Why Chile is a useful case

1. **Overture already carries 4,199,023 Chilean addresses** (`CL` in Overture's address theme guide, opened on
   17 November 2026), so address search has an open source on day one rather than a gap.
2. **Extreme north–south shape and Pacific islands.** Continental Chile is roughly 4,300 km long from north to south
   (`-17.5°` to `-56.0°` latitude) and only about 180 km wide on average, while Rapa Nui (Easter Island, `-109.35°`
   longitude) and the Juan Fernández archipelago sit thousands of kilometres west in the Pacific. A single country-wide
   bounding box spans `-113.22°` to `-65.51°` longitude and is mostly ocean, so Chile tests both per-region cuts and
   offshore-island boxes directly.
3. **Borders with Argentina ([REGIONS-AR.md](REGIONS-AR.md)).** Almost the whole eastern edge of Chile meets Argentina's
   Andean provinces (`AR-J`, `AR-M`, `AR-Q`, `AR-R`, `AR-U`, `AR-Z`, `AR-V`), so the two proposals test cross-border
   margin overlap along the Andes and in Tierra del Fuego.

## What a region is

Chile is divided into **16 regions** (*regiones*), each subdivided into provinces (*provincias*, 56 in all) and communes
(*comunas*, 346 in all). The proposal is **one map set per region, 16 in all**, matching the level of US states,
Argentine provinces ([REGIONS-AR.md](REGIONS-AR.md)) and German Länder ([REGIONS-DE.md](REGIONS-DE.md)).

### Codes

ISO 3166-2:CL assigns each region a two-letter code after `CL-`: `CL-RM` (Región Metropolitana de Santiago), `CL-VS`
(Valparaíso), `CL-BI` (Biobío) and so on. Chile also uses official Roman/numeric identifiers (`I` to `XVI`, plus `RM`)
and two-digit *Código Único Territorial* (CUT) prefixes (`01` to `16`), assigned by the *Subsecretaría de Desarrollo
Regional y Administrativo* (SUBDERE) and the *Instituto Nacional de Estadísticas* (INE).

- A bare `CL` is not in `STATE_CODES` (`engine/address_search.py`; California is `CA` and Colorado is `CO`), and
  hyphenated `CL-XX` codes never collide with a two-letter US state code.
- However, several two-letter suffixes on their own (`MA` Magallanes, `AR` La Araucanía, `CO` Coquimbo, `AN` Antofagasta
  vs `AS`/`AL`) collide with US state codes (`MA` Massachusetts, `AR` Arkansas, `CO` Colorado), so the `CL-` prefix must
  stay part of the code everywhere.

### Boxes

Geofabrik publishes Chile as a single country extract (`chile-latest.osm.pbf`, 336 MB; `chile-261116.osm.pbf` is
352,124,743 bytes, and `chile-261116-free.gpkg.zip` is 774,826,582 bytes, opened on 17 November 2026) with no
sub-region extracts on Geofabrik. Its clipping polygon (`chile.poly`, 132 vertices, opened) has outer bounds
`west = -113.2233, south = -58.4519, east = -65.5141, north = -17.4574` because it wraps Rapa Nui and Sala y Gómez in the
same polygon as the mainland.

The per-region land boxes below cover the 16 regions from north to south. For `CL-VS` (Valparaíso), the box shown is the
**continental mainland plus Robinson Crusoe / Juan Fernández**, while Rapa Nui (Easter Island) is noted separately so the
Valparaíso box does not stretch across 3,700 km of open ocean. These regional boxes should be recomputed directly from
BCN (*Biblioteca del Congreso Nacional de Chile*) or IDE Chile / INE 2024 cartography polygons before a build tool cuts
packs from them.

| Code | CUT | Name | Approximate mainland box (west, south, east, north) | Box with 0.15° margin |
|---|---|---|---|---|
| `CL-AP` | 15 | Arica y Parinacota | -70.38, -19.23, -68.91, -17.50 | -70.53, -19.38, -68.76, -17.35 |
| `CL-TA` | 01 | Tarapacá | -70.29, -21.64, -68.40, -18.94 | -70.44, -21.79, -68.25, -18.79 |
| `CL-AN` | 02 | Antofagasta | -70.75, -26.06, -67.00, -20.93 | -70.90, -26.21, -66.85, -20.78 |
| `CL-AT` | 03 | Atacama | -71.59, -29.54, -68.26, -25.29 | -71.74, -29.69, -68.11, -25.14 |
| `CL-CO` | 04 | Coquimbo | -71.72, -32.28, -69.81, -29.04 | -71.87, -32.43, -69.66, -28.89 |
| `CL-VS` | 05 | Valparaíso (continental) | -71.86, -33.90, -70.00, -32.02 | -72.01, -34.05, -69.85, -31.87 |
| `CL-RM` | 13 | Metropolitana de Santiago | -71.72, -34.29, -69.77, -32.92 | -71.87, -34.44, -69.62, -32.77 |
| `CL-LI` | 06 | Libertador General Bernardo O'Higgins | -72.07, -35.01, -70.01, -33.85 | -72.22, -35.16, -69.86, -33.70 |
| `CL-ML` | 07 | Maule | -72.79, -36.55, -70.32, -34.69 | -72.94, -36.70, -70.17, -34.54 |
| `CL-NB` | 16 | Ñuble | -72.90, -37.20, -71.00, -36.01 | -73.05, -37.35, -70.85, -35.86 |
| `CL-BI` | 08 | Biobío | -73.98, -38.49, -70.98, -36.44 | -74.13, -38.64, -70.83, -36.29 |
| `CL-AR` | 09 | La Araucanía | -73.53, -39.64, -70.83, -37.59 | -73.68, -39.79, -70.68, -37.44 |
| `CL-LR` | 14 | Los Ríos | -73.73, -40.68, -71.58, -39.27 | -73.88, -40.83, -71.43, -39.12 |
| `CL-LL` | 10 | Los Lagos | -74.85, -44.07, -71.58, -40.23 | -75.00, -44.22, -71.43, -40.08 |
| `CL-AI` | 11 | Aysén del General Carlos Ibáñez del Campo | -75.68, -49.16, -71.09, -43.64 | -75.83, -49.31, -70.94, -43.49 |
| `CL-MA` | 12 | Magallanes y de la Antártica Chilena (American sector) | -75.73, -56.00, -66.42, -48.60 | -75.88, -56.15, -66.27, -48.45 |

Three decisions are tied to the boxes:

- **`CL-RM` inside `CL-VS` and `CL-LI`.** The Santiago Metropolitan Region is landlocked between Valparaíso and
  O'Higgins, so their rectangular boxes overlap significantly around Santiago and Valparaíso.
- **Insular Chile (`CL-VS`).** Rapa Nui (`-109.46, -27.20, -109.22, -27.04`), Sala y Gómez, the Juan Fernández islands
  and the Desventuradas belong administratively to the Valparaíso region (`CL-VS`). Keeping them as separate island
  polygons or a multi-box cut avoids pulling 3,700 km of the South Pacific into `CL-VS`.
- **Southern Patagonian Ice Field and Antarctic claims.** As noted in [REGIONS-AR.md](REGIONS-AR.md), a short section of
  the Southern Patagonian Ice Field border between `CL-AI`/`CL-MA` and `AR-Z` (Santa Cruz) is not fully demarcated, and
  `CL-MA` excludes Antarctic territorial claims south of 60° S, matching `AR-V` in [REGIONS-AR.md](REGIONS-AR.md).

## Sources, layer by layer

| Layer (file) | US source today | Proposed for Chile | Publisher | Licence | Mark |
|---|---|---|---|---|---|
| Roads, water, land (base map) | OSM extract | OSM extract, `chile-latest.osm.pbf` (336 MB; `.gpkg.zip` is 739 MB) | OSM contributors via Geofabrik | ODbL 1.0 | opened |
| Points of interest (`poi`) | OSM | OSM | OSM contributors | ODbL 1.0 | opened |
| Addresses (`addresses/<code>.sqlite`) | Overture addresses | **Overture addresses (`CL`, 4,199,023 records)** | Overture Maps Foundation | per Overture attribution | opened |
| Places (`places.sqlite`) | GNIS, Census, OSM | OSM named places; BCN / IDE Chile / INE administrative names (regiones, provincias, comunas, localidades) | OSM contributors; BCN / IDE Chile / INE | ODbL 1.0; CC BY 4.0 on BCN cartography (search only) | search only |
| Terrain (`terrain.sqlite`) | USGS 3DEP | Copernicus DEM GLO-30 (1 arc-second, ~30 m) | ESA / Airbus | Copernicus WorldDEM-30 licence | as in REGIONS.md |
| Water: reservoirs, lakes, rivers (`water.sqlite`) | NHD, NID | OSM `water=reservoir`, `natural=water` and `waterway=dam`; DGA (*Dirección General de Aguas*, MOP) hydrographic inventory if licence is confirmed | OSM contributors; DGA | ODbL 1.0; DGA licence not checked | opened for OSM; not checked for DGA |
| Crops (`crops.sqlite`) | USDA CDL | ESA WorldCover 2021 (land cover, 10 m) for the first build; ODEPA / CIREN fruit-orchard (*catastro frutícola*) layers if open licence is confirmed | ESA WorldCover consortium; ODEPA / CIREN | CC BY 4.0; CIREN licence not checked | as in REGIONS.md |
| Buildings (`buildings.sqlite`) | Microsoft US footprints | Overture buildings or Microsoft Global ML Building Footprints + OSM building heights | Overture; Microsoft; OSM contributors | ODbL / CDLA-Permissive-2.0 (see REGIONS.md) | search only |

Notes:

- **Earthquake, tsunami and volcanic shelter layers.** Chile is one of the most seismically active countries in the
  world. SENAPRED (formerly ONEMI) publishes tsunami evacuation zones, safe assembly points (*puntos de encuentro*) and
  flood/volcanic hazard maps through IDE Chile and geoportals. Their reuse licence was not opened; if open, tsunami
  assembly points map cleanly to the `shelter` or `community` help layer in `web/map.js`.
- **Water scarcity and rural *APR* systems.** In central and northern Chile, rural drinking water often comes from
  *Agua Potable Rural* (APR, now *Servicios Sanitarios Rurales* under MOP/DOH) wells and tanks. Whether DGA/DOH lists
  carry an open licence was not checked.

## How addresses are written

Chilean street addresses put the **street name before the house number**, followed by optional apartment/unit, the
*comuna* (municipality), and the city or region:

```
Av. Libertador Bernardo O'Higgins 1371, Santiago
Calle Condell 1490, Valparaíso
Camino Internacional Km 12, Pucón
```

How this affects `engine/address_search.py` and `tools/build_addresses.py`:

1. **Number after street name.** Like Argentina ([REGIONS-AR.md](REGIONS-AR.md)) and Germany ([REGIONS-DE.md](REGIONS-DE.md)),
   the house number comes at the end of the street part (`Av. Providencia 1208`), whereas `engine/address_search.py`
   expects the number first (`1208 Main St`).
2. **Spanish prefixes and abbreviations.** Street names begin with *Calle*, *Avenida* (*Av.* or *Avda.*), *Pasaje*
   (*Pje.*), *Camino*, *Paseo* or *Ruta*, and often include `de`, `del`, `la`, `los` and accented letters (`Ñuñoa`,
   `Curicó`, `Chiloé`, `O'Higgins`).
3. **Seven-digit postal codes (CorreosChile).** Chile has 7-digit numeric postal codes (for example `8320000` for
   Santiago Centro), but in everyday life people rarely write the postal code and identify places by *comuna* instead
   (such as *Providencia*, *Las Condes*, *Maipú*, *Viña del Mar*). Address search for Chile therefore needs to match
   the *comuna* name at the end of a query even when no postal code is given.

## Still undecided

1. **Codes and names in setup.** As in [REGIONS.md](REGIONS.md) item 1, with `CL-AP` to `CL-MA`.
2. **Insular Chile in `CL-VS`.** Whether Rapa Nui and Juan Fernández are cut as separate island boxes inside the
   `CL-VS` pack or offered as an island add-on so the Valparaíso bounding box stays tight around the mainland.
3. **Tight region polygons.** Recomputing exact land boxes from BCN / IDE Chile official regional boundaries (with the
   0.15° margin rule) and deciding how to handle the overlap between `CL-RM` and `CL-VS`/`CL-LI`.
4. **Address parser order.** Supporting `<street> <number>, <comuna>` in `engine/address_search.py` alongside the
   4,199,023 Chilean address rows already in Overture.
5. **SENAPRED tsunami and emergency points.** Checking whether SENAPRED / IDE Chile evacuation points and safe zones
   carry a redistributable open licence.

## What was checked

- Opened: Geofabrik's Chile page (`chile-261116.osm.pbf` 352 MB, `chile-261116-free.gpkg.zip` 775 MB, ODbL, data up to
  16 November 2026), Geofabrik's `chile.poly` (132 vertices, outer box `-113.2233, -58.4519, -65.5141, -17.4574`), and
  Overture Maps' address guide (`CL`: 4,199,023 addresses).
- Search only: SUBDERE / INE CUT codes, BCN (*Biblioteca del Congreso Nacional*) cartography licensing, IDE Chile and
  SENAPRED geoportals.
- Not opened: DGA, DOH, CIREN/ODEPA, SENAPRED and CorreosChile terms pages, and the ISO 3166-2:CL page.
