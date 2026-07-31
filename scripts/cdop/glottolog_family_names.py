"""Glottocode -> family name, for the 79 top-level language families that actually appear in
`family_id` across the WO8-family D-PLACE substrate (`output/cdop/wo8c_substrate.parquet`,
2026-07-30).

Source: Glottolog's own `languages.csv` (glottolog-cldf,
https://github.com/glottolog/glottolog-cldf/blob/master/cldf/languages.csv), matched by `ID`,
`Level == 'family'`. Fetched fresh and checked against all 79 codes actually present -- not
guessed from memory. One correction this caught: `nilo1247` is **Nilotic**, not "Nilo-Saharan" --
Glottolog deliberately does not recognize Nilo-Saharan as a valid genealogical unit (a disputed
macro-family hypothesis); WO8d's own prose called it Nilo-Saharan in a couple of places
(`wo8d_findings.md`, `CDOP_PILOT_tracker.md`), which is frozen historical record and not corrected
here, but user-facing display from CITYKIN WO4 onward uses the Glottolog-correct name.

Not a general-purpose Glottolog client -- this is a closed lookup for the codes this substrate
actually contains. `family_name()` falls back to the raw code for anything not in the table
(e.g. if the substrate is regenerated and picks up a family not seen here) rather than failing.
"""
from __future__ import annotations

FAMILY_NAMES: dict = {
    'abkh1242': 'Abkhaz-Adyge',
    'afro1255': 'Afro-Asiatic',
    'algi1248': 'Algic',
    'araw1281': 'Arawakan',
    'atha1245': 'Athabaskan-Eyak-Tlingit',
    'atla1278': 'Atlantic-Congo',
    'aust1305': 'Austroasiatic',
    'aust1307': 'Austronesian',
    'ayma1253': 'Aymaran',
    'boro1281': 'Bororoan',
    'cadd1255': 'Caddoan',
    'cari1283': 'Cariban',
    'cent2225': 'Central Sudanic',
    'chib1249': 'Chibchan',
    'chin1490': 'Chinookan',
    'chon1288': 'Chonan',
    'chuk1271': 'Chukotko-Kamchatkan',
    'coch1271': 'Cochimi-Yuman',
    'dizo1235': 'Dizoid',
    'drav1251': 'Dravidian',
    'eski1264': 'Eskimo-Aleut',
    'gong1255': 'Ta-Ne-Omotic',
    'guai1249': 'Guaicuruan',
    'haid1248': 'Haida',
    'heib1242': 'Heibanic',
    'hmon1336': 'Hmong-Mien',
    'indo1319': 'Indo-European',
    'iroq1247': 'Iroquoian',
    'japo1237': 'Japonic',
    'kadu1256': 'Kadugli-Krongo',
    'kart1248': 'Kartvelian',
    'kere1287': 'Keresan',
    'khoe1240': 'Khoe-Kwadi',
    'kiow1265': 'Kiowa-Tanoan',
    'koia1260': 'Koiarian',
    'krua1234': 'Kru',
    'kwer1242': 'Greater Kwerba',
    'kxaa1236': 'Kxa',
    'maid1262': 'Maiduan',
    'mand1469': 'Mande',
    'mata1289': 'Mataguayan',
    'maya1287': 'Mayan',
    'miwo1274': 'Miwok-Costanoan',
    'mixe1284': 'Mixe-Zoque',
    'mong1349': 'Mongolic-Khitan',
    'musk1252': 'Muskogean',
    'nduu1242': 'Ndu',
    'nilo1247': 'Nilotic',
    'nubi1251': 'Nubian',
    'nucl1708': 'Nuclear Torricelli',
    'nucl1709': 'Nuclear Trans New Guinea',
    'nucl1710': 'Nuclear-Macro-Je',
    'otom1299': 'Otomanguean',
    'pala1350': 'Palaihnihan',
    'pama1250': 'Pama-Nyungan',
    'pano1259': 'Pano-Tacanan',
    'pomo1273': 'Pomoan',
    'quec1387': 'Quechuan',
    'saha1239': 'Sahaptian',
    'saha1256': 'Saharan',
    'sali1255': 'Salishan',
    'sino1245': 'Sino-Tibetan',
    'siou1252': 'Siouan',
    'song1307': 'Songhay',
    'sout2845': 'South Omotic',
    'surm1244': 'Surmic',
    'taik1256': 'Tai-Kadai',
    'tuca1253': 'Tucanoan',
    'tung1282': 'Tungusic',
    'tupi1275': 'Tupian',
    'turk1311': 'Turkic',
    'tuuu1241': 'Tuu',
    'ural1272': 'Uralic',
    'utoa1244': 'Uto-Aztecan',
    'waka1280': 'Wakashan',
    'wint1258': 'Wintuan',
    'yano1268': 'Yanomamic',
    'yoku1255': 'Yokutsan',
    'yuki1242': 'Yuki-Wappo',
}


def family_name(code: str) -> str:
    """Display name for a Glottolog family code; falls back to the raw code if unknown."""
    return FAMILY_NAMES.get(code, code)
