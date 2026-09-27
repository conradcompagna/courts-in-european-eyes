"""Compute sentence embeddings for the passage corpora.

Usage:  python scripts/embed.py [--models-dir DIR]

By default models are loaded from the Hugging Face hub by name. For offline use,
pass --models-dir pointing at a folder containing sub-folders named after each
model (e.g. models/all-MiniLM-L6-v2).

Writes data/embeddings/<corpus>__<model>__<variant>.npy (float16, L2-normalised,
row order = row order of the CSV) and a manifest.json.
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
EMB = os.path.join(DATA, "embeddings")

MODELS = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "bge": "BAAI/bge-base-en-v1.5",
}
RUNS = [
    # corpus, model, text column
    ("court", "minilm", "text_norm"),
    ("court", "minilm", "text"),
    ("court", "bge", "text_norm"),
    ("court", "bge", "text"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models-dir", default=None)
    ap.add_argument("--only", default=None, help="comma list of corpus__model__variant to run")
    args = ap.parse_args()
    os.makedirs(EMB, exist_ok=True)
    manifest_path = os.path.join(EMB, "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    loaded = {}
    for corpus, mkey, col in RUNS:
        variant = "norm" if col == "text_norm" else "raw"
        name = f"{corpus}__{mkey}__{variant}"
        if args.only and name not in args.only.split(","):
            continue
        df = pd.read_csv(os.path.join(DATA, f"passages_{corpus}.csv"))
        if mkey not in loaded:
            src = os.path.join(args.models_dir, MODELS[mkey].split("/")[-1]) if args.models_dir else MODELS[mkey]
            loaded[mkey] = SentenceTransformer(src, device="cpu")
        model = loaded[mkey]
        texts = df[col].fillna("").tolist()
        tok = model.tokenizer(texts, add_special_tokens=True, truncation=False)["input_ids"]
        lens = np.array([len(t) for t in tok])
        t0 = time.time()
        X = model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False,
                         convert_to_numpy=True)
        np.save(os.path.join(EMB, name + ".npy"), X.astype(np.float16))
        manifest[name] = dict(model=MODELS[mkey], column=col, rows=len(df), dim=int(X.shape[1]),
                              max_seq_length=int(model.max_seq_length),
                              share_truncated=round(float((lens > model.max_seq_length).mean()), 3),
                              median_tokens=int(np.median(lens)), seconds=round(time.time() - t0, 1))
        print(name, manifest[name], flush=True)
        json.dump(manifest, open(manifest_path, "w"), indent=2)


if __name__ == "__main__":
    main()
