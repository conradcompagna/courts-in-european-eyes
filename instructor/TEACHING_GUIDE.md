# Teaching guide: Kings and Courts in European Eyes

## Place in the course

The lab fits a survey of European expansion in Asia at the point where students have read at least one embassy account in full (Roe's journal, Nieuhof, or Chaumont work well) and have met the idea of "Oriental despotism". The method is secondary: students need to know only that a computer can place texts with similar content close together. The lab's aim is to make them ask what "similar" means and to answer by reading.

Suggested reading before class (choose one):
- Joan-Pau Rubiés, "Oriental Despotism and European Orientalism: Botero to Montesquieu", *Journal of Early Modern History* 9 (2005).
- Sanjay Subrahmanyam, *Courtly Encounters: Translating Courtliness and Violence in Early Modern Eurasia* (Harvard University Press, 2012), introduction.
- A primary source: the account of Roe's first audience with Jahangir (Purchas, *Pilgrimes*, 1625, pp. 542–543; passages `roe-0052` to `roe-0062` in the corpus).

## Preparation

- **Install once:** Python 3.10+, `pip install -r requirements.txt`. The notebook runs without internet; only the optional custom probe in Stage 7 downloads a model. JupyterHub or Colab also work: upload the repository folder.
- **Open the explorer** through the classroom server (`python server.py`, then `http://127.0.0.1:8766/explorer/`) on the projector for Stages 3, 4 and 6. For student devices, see the README's classroom network setup.
- **Read** `data/README.md` (especially the audit and known errors) and the answer key.
- **Assign seeds.** Stage 2 asks each student to draw ten passages with their own seed; tell them to use their student number.

## Browser investigation (90 minutes)

Use the server's `/explorer/` page as the student workspace. The embedding map appears first, with provisional thematic names for its ten clusters. Clicking any passage shows its text and five nearest eligible neighbours below the map. Students summarize the main content of each of the six passages in at least 100 words, then write at least 500 words of synthesis, for a minimum of 1,100 words. Neighbours can cross cluster boundaries.

| Time | Student action |
|---|---|
| 0–10 | Orient students to the map, the source reader, and the difference between a computed cluster and a historical category. |
| 10–25 | Students inspect several named map clusters and click passages to choose one group to study. |
| 25–60 | Read the selected passage and its five nearest neighbours; begin six separate 100-word content summaries. |
| 60–80 | Use the six summaries to outline the 500-word synthesis. |
| 80–90 | Exchange a preliminary interpretation with a partner and use **Save draft** to send partial work to the project folder; complete the full 1,100-word analysis after class. |

Ask students to include author, court, page, and passage ID. Each short response should summarize its passage's main content with a concrete detail; comparison belongs in the synthesis. The displayed neighbours are ranked by cosine similarity of embeddings of normalised text; adjacent passages from one account are excluded, and the source text shown for reading retains its original spelling. In the synthesis, look for an account of why the passages are similar: shared historical situations, recurring European language, genre, translation, or some combination. The key lesson is that semantic similarity does not identify its own historical cause. The browser checks word counts, not the quality of the interpretation. Students enter a name or ID; **Save draft** writes partial work to `submissions/drafts/`, and **Upload completed assignment** writes finished work to `submissions/completed/` on the instructor's computer. Browser storage keeps an interim copy on each device. Use the notebook schedule below for the longer quantitative lab.

## Notebook schedule (90 minutes)

| Time | Activity |
|---|---|
| 0–8 | The question. Read Roe's first audience aloud (`roe-0052`). What in this passage is Mughal, and what is Roe? |
| 8–13 | Stage 1. Students pick two sources and write a prediction. |
| 13–28 | Stage 2. Individual audit of ten passages; pool the counts on the board and compare with the instructor's 40. |
| 28–43 | Stage 3 in pairs. Each pair runs a different anchor (Roe, Chaumont, Nieuhof, Knox) and reports what the neighbours share. |
| 43–53 | Stage 4. Project the court and author maps. |
| 53–68 | Stage 5. Walk through the three tests together; students write Q5 individually. |
| 68–88 | Stage 6. Groups of three take two clusters each; report labels and hit rates. |
| 88–90 | Memo: students write their one-sentence claim; the memo is finished at home. |

**Second session (optional, 75 minutes):** Stage 7 (probes and word search, 35 min), Stage 8 (robustness, 20 min), memo workshop (20 min).

**Shorter version (60 minutes):** Stages 1, 3, 5 (tests a and b only) and 6.

## Concepts to explain before students begin

- **Embedding.** A model trained on modern English text maps each passage to a list of numbers. Passages about similar things, in similar words, get similar numbers. The model knows nothing about the seventeenth century, about courts or about these authors.
- **Cosine similarity.** A score for how alike two passages are. In this corpus a typical pair scores about 0.33 (MiniLM); the most similar pairs score above 0.6.
- **Confounding.** Most authors describe one court, so "same court" and "same author" usually go together. The crossed test and the regression use the few cases where they come apart.
- **Map projections.** UMAP keeps local neighbours; distances between distant regions and the size of empty spaces mean little.

## Likely difficulties

- **Treating the map as the finding.** Students will see "Qing" in one region and stop. Ask: is that the Qing court or Montanus and Nieuhof, both translated by Ogilby?
- **Reading a cluster from its word list.** Distinctive words are frequent words. Insist on reading the representative passages and five random members before naming a cluster.
- **Reading a probe result as a finding about prostration, despotism etc.** The prostration probe's top passages are Dutch negotiation diaries, not prostrations (see the answer key). This is the lab's central lesson; let students find it.
- **Early modern spelling.** Some students will find *vpon*, *haue* and *Embassadour* distracting. The normalised text is the default, and Stage 8 shows what normalisation changes.
- **The sources' own violence and contempt.** Several passages describe executions, mutilation and enslavement, and the authors' judgements of Asian peoples are often contemptuous. Name this at the start and treat it as evidence of the observers.

## Discussion questions

1. Court and author have effects of about the same size. What historical and what textual explanations could each have?
2. Sixteen of the 24 accounts reached English readers through translators. Does this lab compare what Europeans saw, or what English publishers printed?
3. Montanus/Dapper supplies 18% of the corpus. How would the results change if every source had the same number of passages? (Extension below.)
4. Why does the "royal property" probe bring Bernier and Knox to the top? Are they describing similar institutions, making a similar argument, or using similar words?
5. Which kinds of court life are missing from this corpus altogether? Consider who could not be seen by a European visitor, and what the court filter excludes.

## Extensions

- **Balanced corpus.** Sample at most 40 passages per author (`df.groupby("author").sample(...)`) and re-run Stage 5.
- **Genre coding.** Code 60 passages as *audience narrative*, *systematic description* or *history of events*, and add genre to the pair regression.
- **Same scene, different pens.** Roe and Terry describe the same embassy; Nieuhof and Montanus the same company's embassies in the same translator's English. Compare their neighbours directly.
- **Full corpus.** `data/passages_all.csv.gz` holds all 20,324 passages. Embed a sample of non-court passages and ask whether court passages differ from travel description in general.
- **Later embassies.** Add the Macartney embassy accounts (1790s) or Symes's embassy to Ava (1800) and ask whether the template changes.

## What successful completion looks like

A successful student reports their audit counts and explains which pipeline step produced each error; distinguishes the court effect from the author effect with a number; names two clusters by reading them and reports how many random members fit; and writes a memo whose claim is limited by the evidence. For example: *passages about royal punishment are court-crossing, but their similarity comes from shared narrative situations more than from a shared European theory of despotism*, supported by quoted passages and a stated threat to validity.

## Assessment

| Criterion | Weight | Strong work |
|---|---|---|
| Corpus criticism (Q1, Q2) | 20% | Audit counts reported; errors traced to specific pipeline steps; effect on results considered |
| Reading the method (Q3–Q5) | 25% | Distinguishes situation, vocabulary, author and court as sources of similarity; cites numbers correctly |
| Close reading (Q6, Q7) | 35% | Labels tested on random members; passages quoted with id and page; lexical and semantic results compared |
| Memo | 20% | One claim, one number, three passages, one threat to validity, all consistent |
