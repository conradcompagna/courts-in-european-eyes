# Answer key: Kings and Courts in European Eyes

## Browser investigation checks

Students select one passage and read its five closest eligible neighbours. Each of the six 100-word notes should summarize one passage's main content with a concrete textual detail. Comparison and interpretation belong in the synthesis. The five neighbours may belong to other computed clusters; their scores rank similarity to the selected passage, not necessarily to each other. Adjacent passages from the same source account are excluded from the ranking. The cluster names in the explorer are provisional thematic labels.

The synthesis should be at least 500 words, draw on all six summaries, and interpret why the embeddings are similar. Good answers may emphasize a historical situation, a European way of describing courts, common genre or translated vocabulary, or a combination. They should explain what evidence supports their reading and what semantic similarity cannot settle. There is no prescribed passage or correct cluster label. The browser checks word counts, not historical reasoning.

Figures come from the executed notebook with default arguments (MiniLM, normalised spelling, k-means seed 0). The corpus and vectors are fixed, so the figures are reproducible. Interpretive answers are examples of strong responses, not the only acceptable ones.

---

## Stage 1 · The sources

Corpus: 2,388 passages in 24 units. Largest contributors: Montanus/Dapper 429, Nieuhof 221, Olearius 202, Chardin 186, Roe 156. Courts: Qing 825, Mughal 535, Safavid 422, Kandy 113, Muscovy 102, Siam 101, Tokugawa 76, Ottoman 71, South India 47, Pegu 41, Caucasus 33, Deccan 22.

**Q1, strong answers** name a mechanism, not just a difference. Examples:
- **Roe (ambassador) vs Knox (captive).** Roe sees the king in public ceremony (durbar, birthday weighing, gift exchange) and in private drinking sessions, and he negotiates. Knox never sees the king of Kandy closely in nineteen years; he knows the king through orders, punishments and rumour. Prediction: Roe will describe ceremony and negotiation, Knox the king's power over subjects' lives, land and labour.
- **Bernier (physician resident at court) vs Tavernier (merchant).** Bernier stayed eight years and wrote political history and analysis addressed to Colbert. Tavernier's audiences were commercial (selling jewels to the king), so expect inventories of treasure, thrones and prices.
- **Le Comte (Jesuit) vs Nieuhof (VOC embassy).** The Jesuits were at the Kangxi court as scholars and wrote systematic descriptions of government; the Dutch saw the court briefly as tribute-bearing envoys. Expect bureaucracy and learning in Le Comte, ritual and negotiation in Nieuhof.

## Stage 2 · From book to passage

Court basis: 1,479 passages from single-court accounts, 909 attributed by gazetteer.

Instructor audit of 40 passages: **about a ruler or court** 31 yes, 6 partly, 3 no; **court correct** 35 of 38 assessable. All three wrong courts came from the gazetteer (3 of 15 gazetteer passages in the sample; none of 23 single-court passages).

**Q2.** Student counts will vary; with ten passages, 0–2 court errors and 1–3 off-topic passages are typical.
- Step 5 (the court filter) admits passages full of court *vocabulary* that are not *about* a court: an embassy's own table orders, coinage at the diamond mines, lists of rulers elsewhere.
- Step 4 (the gazetteer) fails when a passage at one court talks about another: Olearius's account of a Safavid shah's hunt mentions Muscovy; della Valle's description of the Mughal palace at Ahmedabad sits among Persian references.

**Effect:** gazetteer errors move passages between courts, so they make courts look **more alike** (a Safavid passage counted as Muscovite brings Safavid content into the Muscovy group). Off-topic passages add noise to every group equally, which also weakens differences.

## Stage 3 · What a vector notices

Anchor `roe-0052` (Roe's first audience at the durbar, p. 542). Nearest neighbours, skipping the adjacent passages:

| sim. | passage | author | page |
|---|---|---|---|
| 0.657 | roe-0378 | Roe | 583 |
| 0.654 | roe-0062 | Roe | 543 |
| 0.641 | roe-0172 | Roe | 557 |
| 0.624 | tavernier_india-0164 | Tavernier | 46 |
| 0.620 | roe-0194 | Roe | 559 |
| 0.620 | bernier-0474 | Bernier | 176 |
| 0.617 | hawkins-0003 | Hawkins | 206 |
| 0.615 | roe-0042 | Roe | 540 |

**Q3, strong answer.** The neighbours share the **situation** (being brought before the king: rails, courts, a raised seat, a crowd), the **court** (all Mughal) and in five of eight cases the **author**. The nearest, `roe-0378` (p. 583), describes another audience, where Roe says Jahangir did not require of him "the barbarous custome of kneeling and knocking the ground with the head", which the king demanded of Turkish and Persian ambassadors. What the neighbours do *not* share is the point of the anchor: Roe's negotiation of his own ceremonial (asking in advance "to use the customes of my Country"). The model finds the setting; the historian's question is about the bargaining over ritual, which only reading reveals.

Other anchors:
- `chaumont-0047` (Siam: courtyards of prostrate mandarins on the way to the audience) → another Chaumont audience passage first (0.732), then two Montanus audiences at the Qing court (0.712, 0.693), a Pinto passage from Japan, and another Chaumont passage. The **situation of the audience procession** crosses courts.
- `knox-0582` (the king of Kandy's anger at a servant who spoke to ambassadors) → two more Knox passages, then Hawkins's account of Jahangir having a servant whipped (0.649) and Tavernier's story of a Safavid shah receiving a son's head (0.639). The situation of **royal anger and punishment** crosses courts.

## Stage 4 · The map

**Q4.** Qing and Mughal passages occupy largely separate regions; Safavid overlaps with Mughal. Tavernier's passages spread across the Mughal and Safavid regions and follow the courts he describes (the centres of his Persian and Indian material are distinct), with his seraglio chapters among them. The small detached Ottoman group is Chardin's account of the French embassy at Constantinople, not Tavernier. Each author's passages are somewhat more concentrated than the corpus as a whole (mean distance to their centre 1.85–2.27 map units against 2.52 overall). Before trusting any of this, a student should (a) check the quantitative tests in Stage 5, since UMAP distorts distances; (b) read some passages at the boundary between regions; (c) remember that the largest regions are dominated by the largest sources (Montanus, Nieuhof).

## Stage 5 · Court or author?

**(a) Nearest-neighbour agreement (k = 10, near passages skipped)**

| label | groups | agreement | chance | lift |
|---|---|---|---|---|
| court | 12 | 0.639 | 0.209 | 3.05 |
| author | 22 | 0.436 | 0.083 | 5.24 |
| translator | 9 | 0.576 | 0.177 | 3.26 |
| observer | 6 | 0.633 | 0.246 | 2.57 |
| era | 2 | 0.858 | 0.769 | 1.12 |

The author lift is higher, but this test cannot separate author from court: most authors describe one court.

**(b) Crossed test** (authors with at least 8 passages on each of two or more courts; 637 passages). Means across all of them: same author, other court 0.365; other author, same court 0.376; baseline 0.337. Selected cells:

| author on court | same author, other court | other author, same court | baseline |
|---|---|---|---|
| Tavernier on Safavid | 0.361 | 0.382 | 0.333 |
| Tavernier on Mughal | 0.361 | 0.368 | 0.323 |
| Olearius on Safavid | 0.361 | 0.378 | 0.333 |
| Mandelslo on Safavid | 0.365 | 0.391 | 0.341 |
| Pinto on Qing | 0.391 | 0.338 | 0.351 |
| Pinto on Siam | 0.407 | 0.390 | 0.359 |
| Herbert on Mughal | 0.397 | 0.392 | 0.321 |

**(c) Pair regression** (2.8 million pairs, near pairs excluded): baseline 0.332; same court +0.042; same author +0.035; same translator +0.011.

**Q5, strong answer.** "Court and author both raise similarity well above the baseline, and the court effect is slightly larger: sharing a court adds 0.042 to the cosine similarity of two passages, sharing an author 0.035 (regression). For travellers who wrote about several courts, a passage is usually closer to other writers on the same court than to the same writer on another court (Tavernier on Safavid: 0.382 vs 0.361). Pinto is the exception: his China passages are closer to his own Siam passages (0.391) than to other writers on China (0.338), which fits his account's reputation as a narrative shaped more by its author than by what he saw."

A weaker answer reads the kNN lift for author (5.24) as proof that authorship dominates, without noticing the confounding.

## Stage 6 · Clusters and close reading

k = 10, seed 0:

| cluster | n | courts | authors | distinctive words | suggested label |
|---|---|---|---|---|---|
| 0 | 238 | Mughal 51%, Qing 11%, Siam 10% | Roe 28%, Hawkins 12%, Terry 8% | king, majesty, court, sent, letter, give, present, told, ambassador | Envoy's dealings with the king |
| 1 | 312 | Mughal 34%, Safavid 26%, Kandy 16% | Tavernier 18%, Knox 16%, Roe 15% | king, prince, sent, man, put, father, commanded, gave | What the king did and ordered |
| 2 | 184 | Qing 49%, Safavid 16%, Muscovy 12% | Montanus 26%, Olearius 19%, Nieuhof 17% | emperor, ambassadors, gold, silver, presents, horses | Audiences, banquets and gifts |
| 3 | 193 | Safavid 75%, Mughal 16% | Tavernier 24%, Chardin 23%, Olearius 20% | king, persia, persian, prince, son | Persian politics and provinces |
| 4 | 200 | Mughal 30%, Qing 16%, Safavid 12% | Tavernier 20%, Knox 10%, Roe 8% | palace, elephants, city, gold, gate, throne | Palaces, thrones and display |
| 5 | 295 | Qing 96% | Montanus 73%, Nieuhof 20% | ambassador, peking, emperor, presents, general, batavia | VOC negotiations with Qing officials |
| 6 | 279 | Qing 32%, Safavid 19%, Muscovy 19% | Olearius 27%, Montanus 24%, Chardin 16% | ambassador, answer, vizier, highness, duke, letter | Diplomatic correspondence and visits |
| 7 | 245 | Mughal 49%, Safavid 14%, Ottoman 6% | Tavernier 21%, Bernier 17%, Chardin 10% | king, sultan, son, emir, prince, father, army, aureng | Succession struggles |
| 8 | 280 | Qing 95% | Le Comte 32%, Montanus 31%, Nieuhof 30% | emperor, city, china, peking, empire, province | Describing the Chinese empire |
| 9 | 162 | Mughal 45%, Safavid 20%, Kandy 9% | Tavernier 20%, Terry 13%, Bernier 12% | king, gold, pay, money, present, horse, crowns | Revenue, treasure and gifts |

**Q6, example answers.**

- *Single-source cluster:* **5, "VOC negotiations with Qing officials."** Representative passages (`montanus-0903`, `montanus-1101`, `montanus-0521`) are the Dutch ambassador's requests and replies to the Fujian general and the court. In the default draw of five random members, four are Montanus negotiation passages and the fifth is Saris waiting for the shogun's answer at the Japanese court, so 4/5 fit the label as stated and 5/5 fit "an embassy negotiating with officials". Evidence: "the Ambassador desires, that his Lordship would please to give Order for the speedy procuring of Vessels" (`montanus-0903`). This cluster is a *genre* (a diplomatic day-book) more than a representation of the Qing court.
- *Mixed cluster:* **1.** The representative passages suggest "royal commands and punishments": a Safavid shah receiving the head of a courtier's son in a golden basin (`tavernier_persia-0720`, p. 196); a Mughal prince's hostility to the English (`roe-0080`); the "king" of Hirado leaving Saris's ship (`saris-0004`). The five random members do not support that label: Jahangir's letter to James I (`terry-0825`), Kandyan royal titles (`knox-0457`), the king of Pegu receiving Portuguese envoys (`pinto-2022`), a Safavid shah's day (`chardin-1412`), and a king's defence against a Dutch fleet (`tavernier_india-0936`). Only the broader label "what the king did and ordered" fits (4–5/5). This is the expected lesson: labels taken from representative passages are too specific. The cluster joins Mughal, Safavid and Kandyan material through a shared **narrative situation**: the ruler commands, someone suffers or benefits. Whether that reflects a shared European theory of despotism has to be argued from passages that *generalise* ("the King is absolute master of...") rather than narrate. Cluster 9 (revenue) and the royal-property probe are the place to look for such generalisations.
- **Cluster 3** (default in the notebook) is weaker: in the default random draw only two of five members fit "Persian politics and provinces" (a Georgian prince in Taurus, horse breeding, a governor's patent, Kandahar's surrender, and a della Valle passage from Ikkeri). A strong student reports this as a failure of the label, not of their reading.

## Stage 7 · (optional) Themes across courts

Over-representation among the 5% most similar passages (1.0 = as expected):

| court | prostration | throne | royal property | punishment | gifts | seclusion | drinking | officials | precedence | royal religion |
|---|---|---|---|---|---|---|---|---|---|---|
| Qing | **2.4** | 0.2 | 0.2 | 0.2 | 1.5 | 0.4 | 0.4 | **1.8** | **1.8** | 0.4 |
| Mughal | 0.0 | **2.0** | 1.5 | 1.5 | 0.5 | 1.2 | 1.3 | 0.3 | 0.3 | 1.3 |
| Safavid | 0.3 | 1.0 | 0.9 | 1.4 | 0.7 | 1.6 | 1.1 | 0.8 | 0.5 | 0.8 |
| Kandy | 0.0 | 1.7 | **4.2** | **4.7** | 0.3 | **2.5** | 1.3 | 0.3 | 0.2 | **3.3** |
| Siam | 0.4 | **2.3** | **3.5** | 1.0 | 1.7 | 1.2 | **2.0** | 0.4 | 0.6 | **2.8** |
| Muscovy | 0.4 | 1.2 | 0.0 | 0.2 | 1.9 | 0.6 | 1.8 | 0.2 | **2.4** | 0.4 |
| Tokugawa | 0.5 | 1.1 | 0.5 | 0.3 | 1.0 | 1.6 | 1.6 | **2.0** | 0.3 | 1.3 |
| Ottoman | 0.3 | 0.0 | 0.3 | 0.0 | 0.3 | 0.6 | 0.6 | 0.5 | 0.8 | 0.8 |

**What close reading shows (Q7):**

- **Prostration → Qing 2.4 is an artefact.** 82 of the 120 most similar passages are Montanus's; the top five are about purveyors, departures and visits to the general, not prostration. The probe matches *ambassador + emperor + ceremony* vocabulary, and Montanus's diaries are full of it. A word search tells a different story: *prostrat-* occurs in 27 passages (Siam 11, Qing 7, Safavid 5, Mughal 3), *kneel* in 26 (Qing 18). The Mughal score of 0.0 is also misleading: Roe reports prostration as something Jahangir required of other ambassadors (`roe-0378`), and two Roe passages use the word *prostrate*, but none resembles the probe sentence closely enough to enter the top 5%.
- **Royal property → Kandy 4.2, Siam 3.5, Mughal 1.5 is substantive.** The top passage is Bernier's letter to Colbert: "the King is the sole proprietor of all the Lands of the Kingdom" (`bernier-0450`, p. 157), the classic statement of the thesis Rubiés discusses. Knox supplies 23 of the top 5%, from his chapters on the king of Kandy and "Of the King's Tyrannical Reign". A strong answer notes that Bernier makes an *argument* about property while Knox *describes* service tenure, and asks whether the probe is detecting a shared European model or two different things phrased alike.
- **Punishment → Kandy 4.7.** Knox again (27 of the top 5%), then Tavernier, Roe and Hawkins. The top passage is Hawkins on Jahangir's whipping of a servant who broke a dish (`hawkins-0107`, p. 220). The theme is real, but it follows a genre: narratives of the king's anger.
- **Officials → Qing 1.8, Tokugawa 2.0.** Nieuhof's and Montanus's descriptions of the Chinese councils and Le Comte's account of imperial power over the law. This fits the historiography: the Jesuit and Dutch image of China as governed by learned officials, set against the image of India and Persia as governed by the ruler's will.
- **Drinking → Siam 2.0, Muscovy 1.8, Mughal 1.3.** Top passages: Jahangir drinking with the Persian ambassador (`roe-0173`), a Safavid shah's drinking party (`tavernier_persia-0698`), Terry on Jahangir's toasts. A student who reads them will see that the high Siam score rests on few passages (Siam has only 101).

**Rewording test.** Rewording reorders the courts completely. *"The ambassador was made to prostrate himself before the king"* gives Muscovy 2.4, Ottoman 1.7, Safavid 1.3, Siam 1.2, Qing 1.0. *"Everyone threw himself flat on the ground before the ruler"* gives Kandy 2.1, Safavid 1.6, Mughal 1.0, Qing 0.8. Students should conclude that the original Qing result came from the probe's wording (*emperor*, *ambassador*), not from a court-specific representation of prostration. This is the expected finding.

## Stage 8 · (optional) Does the result survive?

| model | spelling | court lift | author lift | era lift | baseline | same court | same author | court / author |
|---|---|---|---|---|---|---|---|---|
| MiniLM | norm | 3.05 | 5.24 | 1.12 | 0.332 | 0.042 | 0.035 | 1.20 |
| MiniLM | raw | 3.11 | 5.47 | 1.17 | 0.333 | 0.044 | 0.038 | 1.14 |
| bge | norm | 2.89 | 4.84 | 1.11 | 0.613 | 0.020 | 0.018 | 1.09 |
| bge | raw | 2.93 | 4.91 | 1.13 | 0.614 | 0.021 | 0.020 | 1.06 |

Nearest-neighbour overlap, MiniLM vs bge: 0.29.

**Q8, strong answer.** The aggregate conclusion holds everywhere: court and author effects are of similar size, with court slightly ahead. bge's scores are compressed (the average pair already scores 0.61), so raw coefficients cannot be compared across models; their ratio can. Normalising spelling lowers the era lift (1.17 → 1.12) and the author lift (5.47 → 5.24): part of what held each author together was his printer's spelling, which matters most for the 1625–1634 texts (Purchas, Herbert). The individual neighbour lists are **not** stable (only 29% overlap), so any argument built on "the nearest passage to X is Y" must be checked with a second model and, above all, by reading.

## Stage 9 · Memo: what a strong memo does

> Court-specific representation is real but narrower than the maps suggest. Passages about the same court are more alike than passages by the same author (+0.042 against +0.035 in cosine similarity), and some themes attach to particular courts: councils and tribunals to China (over-represented 1.8 times), claims that the king owns the land to Mughal India and Kandy. Reading shows that these are different things. Bernier argues that "the King is the sole proprietor of all the Lands of the Kingdom" (bernier-0450, p. 157) as a general proposition about Indostan addressed to Colbert, while Knox describes lands held in return for service to the king of Kandy [quote, knox-…, p. …]. […] The strongest apparent theme, prostration at the Qing court, dissolves on reading: most of the matching passages are Montanus's negotiation diaries, and the word *prostrate* is commonest in Chaumont's account of Siam […]. One threat to validity: the Qing results rest on two books translated by the same man, Ogilby, so a translator effect could pass for a court effect; comparing Le Comte's passages separately would test this.

## Common misconceptions

- "Nearby on the map means similar." Only locally.
- "The model understands prostration." It matches words and situations in modern English.
- "A cluster is a theme." It can be one author's genre (cluster 5).
- "The probe measures how much a court was represented as X." It measures resemblance to a sentence, and it is sensitive to the probe's wording and to the size of each source.
- "Normalising spelling is neutral." It removes part of the era and author signal; that is a choice.
