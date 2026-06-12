#!/usr/bin/env python3
"""Generate all charts needed for the final report."""

import csv
import base64
import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV  = os.path.join(BASE, "speedup_table.csv")

# ── load data ────────────────────────────────────────────────────────────────
rows = []
with open(CSV) as f:
    for r in csv.DictReader(f):
        rows.append({
            "size":    int(r["size"]),
            "filter":  r["filter"],
            "threads": int(r["threads"]),
            "seq":     float(r["sequential_ms"]),
            "exec":    float(r["executor_ms"]),
            "fj":      float(r["forkjoin_ms"]),
            "exec_su": float(r["executor_speedup"]),
            "fj_su":   float(r["forkjoin_speedup"]),
        })

FILTERS = ["Grayscale", "GaussianBlur5x5", "Sobel3x3"]
SIZES   = [512, 1024, 2048]
THREADS = [1, 2, 4, 8]

COLORS = {"512": "#4e79a7", "1024": "#f28e2b", "2048": "#e15759"}
FILTER_LABELS = {
    "Grayscale":      "Grayscale (memory-bound)",
    "GaussianBlur5x5":"Gaussian Blur 5×5 (compute-bound)",
    "Sobel3x3":       "Sobel 3×3 (compute-bound)",
}

def get(filter_, size, threads, col):
    for r in rows:
        if r["filter"] == filter_ and r["size"] == size and r["threads"] == threads:
            return r[col]
    return None

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

charts = {}

# ── Chart 1: Speedup vs Threads (Executor) — one subplot per filter ──────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=False)
fig.suptitle("Executor — Speedup vs Thread Count", fontsize=13, fontweight="bold")
for ax, fname in zip(axes, FILTERS):
    for size in SIZES:
        sus = [get(fname, size, t, "exec_su") for t in THREADS]
        ax.plot(THREADS, sus, marker="o", label=f"{size}×{size}",
                color=COLORS[str(size)], linewidth=2)
    ax.plot([1, 8], [1, 8], "k--", alpha=0.35, linewidth=1, label="Ideal")
    ax.set_title(FILTER_LABELS[fname], fontsize=9)
    ax.set_xlabel("Threads")
    ax.set_ylabel("Speedup")
    ax.set_xticks(THREADS)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
plt.tight_layout()
charts["speedup_executor"] = fig_to_b64(fig)

# ── Chart 2: Speedup vs Threads (ForkJoin) ───────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=False)
fig.suptitle("ForkJoin — Speedup vs Thread Count", fontsize=13, fontweight="bold")
for ax, fname in zip(axes, FILTERS):
    for size in SIZES:
        sus = [get(fname, size, t, "fj_su") for t in THREADS]
        ax.plot(THREADS, sus, marker="s", label=f"{size}×{size}",
                color=COLORS[str(size)], linewidth=2, linestyle="--")
    ax.plot([1, 8], [1, 8], "k--", alpha=0.35, linewidth=1, label="Ideal")
    ax.set_title(FILTER_LABELS[fname], fontsize=9)
    ax.set_xlabel("Threads")
    ax.set_ylabel("Speedup")
    ax.set_xticks(THREADS)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
plt.tight_layout()
charts["speedup_forkjoin"] = fig_to_b64(fig)

# ── Chart 3: Executor vs ForkJoin @ 2048 ─────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
fig.suptitle("Executor vs ForkJoin — 2048×2048 image", fontsize=13, fontweight="bold")
x = np.array(THREADS)
w = 0.35
for ax, fname in zip(axes, FILTERS):
    exec_su = [get(fname, 2048, t, "exec_su") for t in THREADS]
    fj_su   = [get(fname, 2048, t, "fj_su")   for t in THREADS]
    bars1 = ax.bar(x - w/2, exec_su, w, label="Executor", color="#4e79a7")
    bars2 = ax.bar(x + w/2, fj_su,   w, label="ForkJoin", color="#f28e2b")
    ax.plot([0.5, 8.5], [1, 8], "k--", alpha=0.25, linewidth=1)
    ax.set_title(FILTER_LABELS[fname], fontsize=9)
    ax.set_xlabel("Threads")
    ax.set_ylabel("Speedup")
    ax.set_xticks(x)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(f"{h:.2f}", xy=(bar.get_x()+bar.get_width()/2, h),
                    xytext=(0, 2), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7)
plt.tight_layout()
charts["exec_vs_fj"] = fig_to_b64(fig)

# ── Chart 4: Execution time bar — 2048, 8 threads ────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4.5))
filters_short = ["Grayscale", "Gaussian\nBlur 5×5", "Sobel\n3×3"]
seq_times  = [get(f, 2048, 8, "seq")  for f in FILTERS]
exec_times = [get(f, 2048, 8, "exec") for f in FILTERS]
fj_times   = [get(f, 2048, 8, "fj")   for f in FILTERS]
x = np.arange(len(FILTERS))
w = 0.25
ax.bar(x - w, seq_times,  w, label="Sequential", color="#76b7b2")
ax.bar(x,     exec_times, w, label="Executor (8T)", color="#4e79a7")
ax.bar(x + w, fj_times,   w, label="ForkJoin (8T)", color="#f28e2b")
ax.set_xticks(x); ax.set_xticklabels(filters_short)
ax.set_ylabel("Average time (ms)")
ax.set_title("Execution Time — 2048×2048, 8 Threads", fontsize=12, fontweight="bold")
ax.legend(); ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
charts["time_2048_8t"] = fig_to_b64(fig)

# ── print sizes for sanity check ─────────────────────────────────────────────
for k, v in charts.items():
    print(f"{k}: {len(v)//1024} KB")

# ── save to file so HTML generator can import ────────────────────────────────
import json
out = os.path.join(BASE, "scripts", "_charts.json")
with open(out, "w") as f:
    json.dump(charts, f)
print("Charts saved to", out)
