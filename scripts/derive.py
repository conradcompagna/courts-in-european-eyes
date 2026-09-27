"""Derived files used by the notebook and the browser explorer.

  data/embeddings/probes__<model>.npy   query vectors for the ten thematic probes
  data/map_<model>_<variant>.csv        2-D UMAP coordinates of the court corpus
  explorer/data.js                      passages, coordinates, neighbours, clusters, probe scores

Run after scripts/embed.py:  python scripts/derive.py [--models-dir DIR]
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import embassylab as el  # noqa: E402

MODELS = {"minilm": "sentence-transformers/all-MiniLM-L6-v2", "bge": "BAAI/bge-base-en-v1.5"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models-dir", default=None)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    # probe vectors
    for key, name in MODELS.items():
        src = os.path.join(args.models_dir, name.split("/")[-1]) if args.models_dir else name
        m = SentenceTransformer(src, device="cpu")
        P = m.encode(list(el.PROBES.values()), normalize_embeddings=True)
        np.save(os.path.join(el.EMB, f"probes__{key}.npy"), P.astype(np.float16))
        print("probes", key, P.shape)

    df = el.load_passages()
    # maps
    for model, variant in [("minilm", "norm"), ("minilm", "raw"), ("bge", "norm")]:
        X = el.load_vectors(model=model, variant=variant)
        xy = el.umap_coords(X)
        pd.DataFrame({"pid": df["pid"], "x": xy[:, 0].round(4), "y": xy[:, 1].round(4)}).to_csv(
            os.path.join(el.DATA, f"map_{model}_{variant}.csv"), index=False)
        print("map", model, variant)

    # explorer data (MiniLM, normalised spelling)
    X = el.load_vectors(model="minilm", variant="norm")
    xy = pd.read_csv(os.path.join(el.DATA, "map_minilm_norm.csv"))
    S = X @ X.T
    np.fill_diagonal(S, -np.inf)
    S[el.near_mask(df)] = -np.inf
    nn = np.argsort(-S, axis=1)[:, :8]
    labels = el.kmeans(X, k=10, seed=0)
    names, P = el.probe_vectors("minilm")
    PS = X @ P.T
    pz = (PS - PS.mean(0)) / PS.std(0)
    src = pd.read_csv(os.path.join(el.DATA, "sources.csv")).fillna("")
    terms = el.distinctive_terms(df, labels, n=10)
    passages = []
    for i, r in df.iterrows():
        passages.append(dict(
            id=r["pid"], u=r["unit"], c=r["court"], p=str(r["page"]), s=str(r["section"])[:140] if isinstance(r["section"], str) else "",
            x=float(xy.at[i, "x"]), y=float(xy.at[i, "y"]), k=int(labels[i]),
            t=r["text"], n=r["text_norm"],
            nn=[[int(j), round(float(S[i, j]), 3)] for j in nn[i]],
            pr=[round(float(v), 2) for v in pz[i]]))
    out = dict(passages=passages,
               sources=src.to_dict(orient="records"),
               probes=[dict(id=k, text=v) for k, v in el.PROBES.items()],
               clusters={int(k): v for k, v in terms.items()})
    os.makedirs(os.path.join(ROOT, "explorer"), exist_ok=True)
    with open(os.path.join(ROOT, "explorer", "data.js"), "w", encoding="utf-8") as f:
        f.write("window.LAB_DATA = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("explorer data", len(passages))


if __name__ == "__main__":
    main()
