# Data

## Texts

All texts are **EEBO-TCP Phase I** keyboarded transcriptions of seventeenth-century English printings, released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) by the Text Creation Partnership. Each XML file was downloaded from the Partnership's GitHub organisation (`https://github.com/textcreationpartnership/<ID>`) on 24 September 2026 and is kept unchanged in `tcp_xml/`.

| TCP | Printing | Units drawn from it |
|---|---|---|
| A68617 | Samuel Purchas, *Purchas his Pilgrimes*, part 1 (London, 1625) | Roe, Hawkins, Finch, Coryat, Saris |
| A95658 | Edward Terry, *A Voyage to East-India* (London, 1655) | Terry |
| A27515 | François Bernier, *The History of the Late Revolution of the Empire of the Great Mogol*, trans. Henry Oldenburg (London, 1676) | Bernier |
| A63439 | Jean-Baptiste Tavernier, *The Six Voyages*, trans. John Phillips (London, 1677) | Tavernier (Persia, India, Seraglio) |
| A53322 | Adam Olearius, *The Voyages and Travells of the Ambassadors*, with Mandelslo's *Travels into the Indies*, trans. John Davies (London, 1669) | Olearius, Mandelslo |
| A03065 | Thomas Herbert, *A Relation of Some Yeares Travaile* (London, 1634) | Herbert |
| A31753 | John Chardin, *The Travels of Sir John Chardin into Persia*, vol. 1, with *The Coronation of Solyman* (London, 1686) | Chardin |
| A52346 | Johan Nieuhof, *An Embassy from the East-India Company ... to the Grand Tartar Cham*, trans. John Ogilby (London, 1673) | Nieuhof |
| A36730 | Arnoldus Montanus [Olfert Dapper], *Atlas Chinensis*, trans. John Ogilby (London, 1671) | Montanus/Dapper |
| A29216 | Adam Brand, *A Journal of the Embassy from ... Muscovy ... into China* (London, 1698) | Brand |
| A49911 | Louis Le Comte, *Memoirs and Observations ... in a Late Journey through the Empire of China* (London, 1697) | Le Comte |
| A32752 | Alexandre de Chaumont, *A Relation of the Late Embassy ... to the Court of the King of Siam* (London, 1687) | Chaumont |
| A34454 | François Caron and Joost Schouten, *A True Description of the Mighty Kingdoms of Japan and Siam*, trans. Roger Manley (London, 1663) | Caron, Schouten |
| A47586 | Robert Knox, *An Historical Relation of the Island Ceylon* (London, 1681) | Knox |
| A65012 | Pietro della Valle, *The Travels of Sig. Pietro della Valle ... into East-India*, trans. George Havers (London, 1665) | della Valle |
| A50610 | Fernão Mendes Pinto, *The Voyages and Adventures*, trans. Henry Cogan (London, 1653) | Pinto |

Bibliographic details are taken from each file's TEI header. Where the header names no translator, `sources.csv` says so.

## Files

| File | What it is |
|---|---|
| `tcp_xml/*.xml` | the 16 source files, as downloaded |
| `sources.csv` | one row per source unit: author, observer's origin, original language, translator, printing, years in Asia, role, TCP id, default court, and the heading rules that select the unit |
| `passages_all.csv.gz` | all 20,324 passages from the 24 units (2.65 million words) |
| `passages_court.csv` | the analysis corpus: 2,388 passages about rulers and courts |
| `audit_sample.csv` | instructor's audit of 40 randomly drawn passages from `passages_court.csv` |
| `embeddings/` | vectors for `passages_court.csv`, row for row: two models × two spellings, float16, L2-normalised; ten probe vectors per model; `manifest.json` records model, dimensions and truncation |
| `map_*.csv` | 2-D UMAP coordinates used in the notebook and explorer |

Passage columns: `pid`, `unit`, `author`, `tcp`, `page` (printed page on which the passage begins), `section` (chapter headings), `court`, `court_basis`, `gaz_hits`, `n_words`, `court_core`, `court_secondary`, `court_density`, `ortho_change` (share of words altered by normalisation), `text` (as transcribed), `text_norm`.

## How the corpus was built

`scripts/build_corpus.py`, using `scripts/tei.py`, `scripts/sources.py` and `scripts/normalise.py`.

1. **Reading.** Paragraphs (`<p>`, and `<item>` without paragraphs) from `<body>` only. Front and back matter and marginal notes (`<note>`) are dropped. Line-end hyphens marked by TCP are joined, the long s is printed as *s*, combining abbreviation marks are removed, and illegible characters (`<gap>`) become spaces.
2. **Units.** A unit is selected by regular expressions on its chapter headings (`include` / `exclude` in `sources.csv`). Olearius and Mandelslo share one file without distinguishing top-level headings; they are separated at paragraph 2,099, where Mandelslo's travels begin with their own pagination. Mandelslo's chapters on Japan, Formosa and China are excluded because they describe countries he did not visit. Terry's closing moral "Corollarie", Chaumont's return voyage, and Knox's last four chapters (his arrival among the Dutch and his notes on other nations) are excluded.
3. **Passages.** Consecutive paragraphs in one chapter are merged until they reach 140 words; longer paragraphs are split at sentence ends. Target 90–170 words; fragments under 40 words are dropped. Median length 142 words.
4. **Court.** Units written at one court take that court (1,479 passages). For the ten units that travel between courts, a gazetteer of ruler titles, capitals and court place-names in period spellings (`GAZETTEER` in `sources.py`) is counted in the passage (double weight) and its two neighbours; a court is assigned when it has at least two hits and 60% of all hits (909 passages). Other passages in those units are left unassigned and excluded.
5. **About rulers and courts.** A passage enters the analysis corpus if its normalised text has at least two core terms (*king, emperor, queen, shah, sultan, majesty, court, throne, audience, palace, ambassador, embassy*...) and a weighted density of court vocabulary of at least 5 per 100 words (core terms count double; secondary terms include *nobles, eunuchs, presents, ceremony, prostrate, tribute, reign, tyranny, justice, revenue*...).
6. **Spelling.** `normalise.py` regularises u/v, i/j and vv, some final *-ie* and *-ll*, and about 90 frequent variant spellings (*haue, vpon, emperour, embassadour, souldiers, citie*...). It does not modernise vocabulary or names. `text` keeps the transcription.

## Embeddings

`scripts/embed.py` encodes each passage with **sentence-transformers/all-MiniLM-L6-v2** (384 dimensions, 256-token limit: 2.8% of normalised passages are truncated) and **BAAI/bge-base-en-v1.5** (768 dimensions, 512-token limit: none truncated), for both `text` and `text_norm`. Model weights were obtained from Hugging Face on 24 September 2026. `scripts/derive.py` computes the probe vectors, the UMAP maps (cosine metric, 15 neighbours, minimum distance 0.1, seed 42) and the explorer data.

## Audit and known errors

The instructor read 40 passages drawn at random (`audit_sample.csv`, seed 2024):

- **About a ruler or court:** 31 yes, 6 partly, 3 no. The three failures are an embassy's own table orders, diamond-mine coinage, and a list of Muslim rulers in Africa.
- **Court correct:** 35 of 38 assessable passages. All three errors come from the gazetteer (3 of its 15 passages in the sample): a Safavid hunt and a Muscovite envoy at a Safavid khan's palace both labelled *Muscovy* (Olearius), and the Mughal palace at Ahmedabad labelled *Safavid* (della Valle). No errors in single-court units.

Known systematic problems:

- **"Court" means the court the passage is mainly about.** For single-court accounts it is the court where the author was; a Mughal envoy at the Qing court is a Qing scene. For multi-court travellers it is the court most named, which fails when a passage at one court discusses another.
- **Unequal sizes.** Montanus/Dapper supplies 18% of the corpus, and Qing passages 35%. The notebook's statistics use all passages; students should ask what that weighting does.
- **Genre is not coded.** Journals of audiences, systematic descriptions of government, and histories of succession wars sit side by side.
- **Translation.** Sixteen of the 24 units are English translations. The embedding therefore compares translators' English as much as observers' perceptions.
- **Damaged originals.** TCP marks illegible characters; a few passages (especially Knox) contain broken words.
