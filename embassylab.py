"""Helper functions for the embassy-embeddings lab.

The notebook calls these so that each methodological choice (which model,
raw or normalised spelling, how many neighbours, whether to ignore passages
from the same stretch of the same book) is a visible argument.
"""
from __future__ import annotations

import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
EMB = os.path.join(DATA, "embeddings")

PROBES = {
    "prostration": "The ambassador was ordered to kneel and knock his head against the ground before the emperor.",
    "throne": "The king sat upon a throne of massy gold set with diamonds, rubies and great pearls.",
    "royal_property": "All the land of the kingdom belongs to the king, and no subject has any property of his own.",
    "punishment": "For a small fault the king commanded the man to be cruelly put to death in his presence.",
    "gifts": "The presents brought by the ambassador were carried in and shown to the king one by one.",
    "seclusion": "The king's wives and concubines are kept shut up in the palace and guarded by eunuchs.",
    "drinking": "The king drank wine with the ambassador and made merry with him late into the night.",
    "officials": "The empire is governed by councils and tribunals of officials who examine every matter in writing.",
    "precedence": "There was a long dispute about where the ambassador should sit and whether he should uncover his head.",
    "royal_religion": "The king is very devout and spends much time with his priests in the temples.",
}

STOP = set("""a about above after again against all almost also although always am among an and another any are
as at be because been before being below between both but by came can come could did do does doing done down
during each either else even ever every few for from further had has have having he her here hers herself him
himself his how however i if in into is it its itself just least less like made make many may me might more most
much must my myself neither never no nor not now of off often on once one only or other others our ours out over
own same shall she should since so some such than that the their theirs them themselves then there these they
this those though through thus to too under until unto up upon us very was we were what when where whereof which
while who whom whose why will with within without would yet you your hath doth also thereof therein thereupon
said saith say says upon unto hither thither whence whereupon wherein whereby whilst amongst toward towards
great good two three four five six ten hundred thousand first second last next part way time times day days
place places thing things manner kind sort sorts well much made make being having another every several""".split())


# ---------------------------------------------------------------- loading

def load_passages(corpus: str = "court") -> pd.DataFrame:
    df = pd.read_csv(os.path.join(DATA, f"passages_{corpus}.csv"), dtype={"page": str})
    src = pd.read_csv(os.path.join(DATA, "sources.csv")).set_index("unit")
    df["author"] = df["unit"].map(src["author"])
    df["observer"] = df["unit"].map(src["observer"]).str.split(" ").str[0]
    df["orig_lang"] = df["unit"].map(src["orig_lang"])
    df["translator"] = df["unit"].map(src["translator"]).fillna("")
    df["pub"] = df["unit"].map(src["pub"])
    df["role"] = df["unit"].map(src["role"])
    df["era"] = np.where(df["pub"] < 1650, "printed 1625-1634", "printed 1653-1698")
    df["pos"] = df["pid"].str.rsplit("-", n=1).str[1].astype(int)
    return df


def load_vectors(corpus: str = "court", model: str = "minilm", variant: str = "norm") -> np.ndarray:
    return np.load(os.path.join(EMB, f"{corpus}__{model}__{variant}.npy")).astype(np.float32)


def manifest() -> dict:
    return json.load(open(os.path.join(EMB, "manifest.json")))


# ---------------------------------------------------------------- similarity

def cosine(X: np.ndarray) -> np.ndarray:
    """Vectors are stored L2-normalised, so the dot product is the cosine similarity."""
    return X @ X.T


def near_mask(df: pd.DataFrame, window: int = 3) -> np.ndarray:
    """True for pairs of passages from the same source unit within `window` positions:
    these are near-duplicates of context and would inflate every 'same author' result."""
    u = df["unit"].to_numpy(object)
    p = df["pos"].to_numpy()
    return (u[:, None] == u[None, :]) & (np.abs(p[:, None] - p[None, :]) <= window)


def neighbours(X: np.ndarray, df: pd.DataFrame, pid: str, k: int = 8, skip_near: bool = True,
               cols=("pid", "author", "court", "page")) -> pd.DataFrame:
    i = int(np.where(df["pid"].to_numpy() == pid)[0][0])
    s = X @ X[i]
    s[i] = -np.inf
    if skip_near:
        u, p = df["unit"].to_numpy(object), df["pos"].to_numpy()
        s[(u == u[i]) & (np.abs(p - p[i]) <= 3)] = -np.inf
    order = np.argsort(-s)[:k]
    out = df.iloc[order][list(cols)].copy()
    out.insert(0, "similarity", s[order].round(3))
    return out.reset_index(drop=True)


def knn_agreement(X: np.ndarray, df: pd.DataFrame, label: str, k: int = 10, skip_near: bool = True) -> dict:
    """Share of each passage's k nearest neighbours that carry the same label, compared
    with the share expected if neighbours were drawn at random (sum of squared label shares)."""
    S = cosine(X)
    np.fill_diagonal(S, -np.inf)
    if skip_near:
        S[near_mask(df)] = -np.inf
    idx = np.argpartition(-S, k, axis=1)[:, :k]
    lab = df[label].to_numpy(object)
    agree = (lab[idx] == lab[:, None]).mean()
    share = pd.Series(lab).value_counts(normalize=True)
    chance = float((share ** 2).sum())
    return dict(label=label, groups=int(len(share)), agreement=round(float(agree), 3),
                chance=round(chance, 3), lift=round(float(agree) / chance, 2))


def crossed_test(X: np.ndarray, df: pd.DataFrame, min_n: int = 8) -> pd.DataFrame:
    """For authors who describe two or more courts (at least `min_n` passages each), compare a
    passage's mean similarity to (a) the same author writing about another court, (b) other authors
    writing about the same court, (c) other authors writing about other courts."""
    ct = pd.crosstab(df["author"], df["court"])
    cells = {(a, c) for a in ct.index for c in ct.columns if ct.loc[a, c] >= min_n}
    multi = {a for a in ct.index if sum((a, c) in cells for c in ct.columns) >= 2}
    a = df["author"].to_numpy(object)
    c = df["court"].to_numpy(object)
    in_cell = np.array([(x, y) in cells for x, y in zip(a, c)])
    S = cosine(X)
    near = near_mask(df)
    rows = []
    for i in np.where(in_cell & np.isin(a, list(multi)))[0]:
        base = in_cell.copy()
        base[i] = False
        base &= ~near[i]
        sa, sc = a == a[i], c == c[i]
        oa_sc = base & ~sa & sc
        if not oa_sc.any():
            continue
        rows.append(dict(author=a[i], court=c[i],
                         same_author_other_court=S[i, base & sa & ~sc].mean(),
                         other_author_same_court=S[i, oa_sc].mean(),
                         other_author_other_court=S[i, base & ~sa & ~sc].mean()))
    return pd.DataFrame(rows)


def pair_regression(X: np.ndarray, df: pd.DataFrame, factors=("court", "author", "translator")) -> pd.DataFrame:
    """Ordinary least squares over all pairs of passages (excluding near pairs from the same book):
    similarity = b0 + b1*same_court + b2*same_author + ...  Each coefficient is the average change
    in cosine similarity associated with sharing that attribute, holding the others fixed.
    'translator' only counts as shared when both passages name the same translator."""
    n = len(df)
    iu = np.triu_indices(n, 1)
    y = cosine(X)[iu]
    keep = ~near_mask(df)[iu]
    cols = [np.ones(keep.sum(), dtype=np.float32)]
    names = ["baseline (nothing shared)"]
    for f in factors:
        v = df[f].to_numpy(object)
        same = v[iu[0]] == v[iu[1]]
        if f == "translator":
            same &= v[iu[0]] != ""
        cols.append(same[keep].astype(np.float32))
        names.append("same " + f)
    M = np.column_stack(cols)
    b, *_ = np.linalg.lstsq(M, y[keep], rcond=None)
    share = [1.0] + [float(c.mean()) for c in cols[1:]]
    return pd.DataFrame({"coefficient": np.round(b, 4), "share_of_pairs": np.round(share, 4)}, index=names)


# ---------------------------------------------------------------- clusters

def kmeans(X: np.ndarray, k: int = 10, seed: int = 0) -> np.ndarray:
    from sklearn.cluster import KMeans
    return KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(X)


def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2 and w not in STOP]


def distinctive_terms(df: pd.DataFrame, labels, n: int = 12, text_col: str = "text_norm") -> dict:
    """Class-based TF-IDF: words frequent in one cluster and rare across clusters."""
    from collections import Counter
    import math
    groups = {}
    for lab, text in zip(labels, df[text_col]):
        groups.setdefault(lab, Counter()).update(_tokens(text))
    df_count = Counter()
    for c in groups.values():
        df_count.update(set(c))
    K = len(groups)
    out = {}
    for lab, c in groups.items():
        total = sum(c.values())
        score = {w: (f / total) * math.log(1 + K / df_count[w]) for w, f in c.items() if f >= 5}
        out[lab] = [w for w, _ in sorted(score.items(), key=lambda x: -x[1])[:n]]
    return out


def cluster_profile(df: pd.DataFrame, labels, X: np.ndarray, top_courts: int = 3, n_rep: int = 3) -> pd.DataFrame:
    terms = distinctive_terms(df, labels)
    rows = []
    for lab in sorted(set(labels)):
        m = np.asarray(labels) == lab
        sub = df[m]
        cen = X[m].mean(0)
        cen /= np.linalg.norm(cen)
        rep = sub.iloc[np.argsort(-(X[m] @ cen))[:n_rep]]["pid"].tolist()
        courts = sub["court"].value_counts(normalize=True).head(top_courts)
        authors = sub["author"].value_counts(normalize=True).head(top_courts)
        rows.append(dict(cluster=lab, passages=int(m.sum()),
                         courts=", ".join(f"{k} {v:.0%}" for k, v in courts.items()),
                         authors=", ".join(f"{k.split(' / ')[0].split()[-1]} {v:.0%}" for k, v in authors.items()),
                         n_authors=sub["author"].nunique(),
                         terms=", ".join(terms[lab]), representative=", ".join(rep)))
    return pd.DataFrame(rows).set_index("cluster")


# ---------------------------------------------------------------- probes

def probe_vectors(model: str = "minilm") -> tuple[list[str], np.ndarray]:
    P = np.load(os.path.join(EMB, f"probes__{model}.npy")).astype(np.float32)
    return list(PROBES), P


def embed_queries(texts: list[str], model: str = "minilm", models_dir: str | None = None) -> np.ndarray:
    """Embed new query sentences. Needs sentence-transformers and (first time) an internet connection."""
    from sentence_transformers import SentenceTransformer
    name = {"minilm": "sentence-transformers/all-MiniLM-L6-v2", "bge": "BAAI/bge-base-en-v1.5"}[model]
    src = os.path.join(models_dir, name.split("/")[-1]) if models_dir else name
    return SentenceTransformer(src, device="cpu").encode(texts, normalize_embeddings=True)


def probe_by_court(X: np.ndarray, df: pd.DataFrame, q: np.ndarray, courts=None, top_share: float = 0.05) -> pd.DataFrame:
    """For one query vector: each court's mean similarity, and its share of the corpus-wide top 5%
    relative to its share of all passages (1.0 = no over-representation)."""
    s = X @ q
    cut = np.quantile(s, 1 - top_share)
    t = df.assign(sim=s, top=s >= cut)
    if courts is not None:
        t = t[t["court"].isin(courts)]
    g = t.groupby("court").agg(passages=("sim", "size"), mean_sim=("sim", "mean"), in_top=("top", "sum"))
    g["over_representation"] = (g["in_top"] / g["in_top"].sum()) / (g["passages"] / g["passages"].sum())
    return g.sort_values("over_representation", ascending=False).round(3)


def top_passages(X: np.ndarray, df: pd.DataFrame, q: np.ndarray, n: int = 8) -> pd.DataFrame:
    s = X @ q
    o = np.argsort(-s)[:n]
    return df.iloc[o][["pid", "author", "court", "page"]].assign(similarity=s[o].round(3)).reset_index(drop=True)


def show(df: pd.DataFrame, pid: str, variant: str = "text_norm", width: int = 100) -> None:
    import textwrap
    r = df.set_index("pid").loc[pid]
    print(f"{pid} | {r['author']} | {r['court']} | p. {r['page']} | {r['section']}")
    print(textwrap.fill(r[variant], width))


# ---------------------------------------------------------------- map and figures

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, FAINT = "#0b0b0b", "#52514e", "#e4e3df", "#d6d5d0"
MAIN_COURTS = ["Qing", "Mughal", "Safavid", "Kandy", "Siam", "Muscovy", "Tokugawa", "Ottoman"]


def load_map(model: str = "minilm", variant: str = "norm") -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA, f"map_{model}_{variant}.csv"))


def umap_coords(X: np.ndarray, seed: int = 42, n_neighbors: int = 15, min_dist: float = 0.1) -> np.ndarray:
    import umap
    return umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric="cosine", random_state=seed).fit_transform(X)


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    return ax


def facet_map(xy: np.ndarray, df: pd.DataFrame, by: str = "court", groups=None, ncols: int = 4, title: str = ""):
    """Small multiples: each panel shows one group in colour over the whole corpus in grey."""
    import matplotlib.pyplot as plt
    groups = groups or df[by].value_counts().index[:8].tolist()
    nrows = int(np.ceil(len(groups) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.2 * ncols, 3.1 * nrows), sharex=True, sharey=True)
    for ax, g in zip(np.ravel(axes), groups):
        m = (df[by] == g).to_numpy()
        ax.scatter(xy[~m, 0], xy[~m, 1], s=3, c=FAINT, linewidths=0)
        ax.scatter(xy[m, 0], xy[m, 1], s=7, c=BLUE, linewidths=0.3, edgecolors="#fcfcfb")
        ax.set_title(f"{g}  (n={m.sum()})", fontsize=10, loc="left", color=INK)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(GRID)
    for ax in np.ravel(axes)[len(groups):]:
        ax.axis("off")
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    return fig


def crossed_plot(res: pd.DataFrame):
    """Dot plot of the crossed test: one row per author x court cell."""
    import matplotlib.pyplot as plt
    g = res.groupby(["author", "court"]).mean(numeric_only=True)
    g.index = [f"{a.split(' / ')[0].split()[-1]} on {c}" for a, c in g.index]
    fig, ax = plt.subplots(figsize=(7.5, 0.42 * len(g) + 1.2))
    y = np.arange(len(g))
    ax.hlines(y, g.min(axis=1), g.max(axis=1), color=GRID, lw=2)
    for col, c, lab in [("other_author_other_court", "#8a8984", "other author, other court (baseline)"),
                        ("same_author_other_court", ORANGE, "same author, other court"),
                        ("other_author_same_court", BLUE, "other author, same court")]:
        ax.scatter(g[col], y, s=46, color=c, label=lab, zorder=3, edgecolors="#fcfcfb", linewidths=1)
    ax.set_yticks(y); ax.set_yticklabels(g.index, fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("mean cosine similarity", color=MUTED, fontsize=9)
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1)
    ax.set_title("Is a passage closer to its author's other courts, or to other authors on its court?", loc="left",
                 fontsize=10.5, color=INK)
    return _style(ax)


def coef_plot(tab: pd.DataFrame, title: str = "Change in similarity when two passages share..."):
    import matplotlib.pyplot as plt
    t = tab.drop(index="baseline (nothing shared)")["coefficient"]
    fig, ax = plt.subplots(figsize=(6.5, 0.45 * len(t) + 1))
    ax.barh(range(len(t)), t.values, color=[BLUE if v >= 0 else ORANGE for v in t.values], height=0.6)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_yticks(range(len(t))); ax.set_yticklabels(t.index, fontsize=9, color=INK); ax.invert_yaxis()
    for i, v in enumerate(t.values):
        ax.text(v, i, f" {v:+.3f} ", va="center", ha="left" if v >= 0 else "right", fontsize=8, color=MUTED)
    ax.set_xlabel("cosine similarity (baseline pair = %.3f)" % tab.loc["baseline (nothing shared)", "coefficient"],
                  color=MUTED, fontsize=9)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK)
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    return _style(ax)


def heatmap(tab: pd.DataFrame, title: str, fmt: str = "{:.1f}", cmap: str = "Blues"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(0.95 * tab.shape[1] + 2.2, 0.45 * tab.shape[0] + 1.4))
    im = ax.imshow(tab.values, cmap=cmap, aspect="auto", vmin=0, vmax=max(3, np.nanmax(tab.values)))
    ax.set_xticks(range(tab.shape[1])); ax.set_xticklabels(tab.columns, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(tab.shape[0])); ax.set_yticklabels(tab.index, fontsize=9)
    vmax = max(3, np.nanmax(tab.values))
    for i in range(tab.shape[0]):
        for j in range(tab.shape[1]):
            v = tab.values[i, j]
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=8,
                    color="#ffffff" if v > 0.55 * vmax else INK)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK)
    for s in ax.spines.values():
        s.set_visible(False)
    return ax
