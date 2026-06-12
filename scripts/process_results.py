#!/usr/bin/env python3
"""
process_results.py — Turn raw JMH CSV output into speedup tables and graphs.

Usage:
    python3 scripts/process_results.py jmh-results.csv

Outputs:
    - Prints a tidy speedup table to the console
    - Writes speedup_table.csv
    - Writes speedup_<filter>.png charts (if matplotlib is installed)

The speedup for a given (size, filter, threads) is:
    speedup = sequential_time(size, filter) / parallel_time(size, filter, threads)

JMH's CSV columns of interest:
    "Benchmark"          e.g. com...FilterBenchmark.executorParallel
    "Score"              the measured average time (ms/op)
    "Param: size"
    "Param: threads"
    "Param: filterName"
"""

import csv
import sys
from collections import defaultdict


def load_rows(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def col(row, *candidates):
    """Find a column by trying several possible header spellings."""
    for c in candidates:
        for key in row:
            if key.strip().strip('"').lower() == c.lower():
                return row[key].strip().strip('"')
    return None


def short_method(benchmark):
    # com.ceng479.imaging.benchmark.FilterBenchmark.executorParallel -> executorParallel
    return benchmark.split(".")[-1]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    rows = load_rows(path)
    if not rows:
        print("No rows found in", path)
        sys.exit(1)

    # data[(size, filter)][method][threads] = score
    data = defaultdict(lambda: defaultdict(dict))

    for r in rows:
        bench = col(r, "Benchmark")
        score = col(r, "Score")
        size = col(r, "Param: size", "size")
        threads = col(r, "Param: threads", "threads")
        fname = col(r, "Param: filterName", "filterName")
        if bench is None or score is None:
            continue
        method = short_method(bench)
        try:
            score = float(score.replace(",", "."))
            size_i = int(size)
            threads_i = int(threads)
        except (TypeError, ValueError):
            continue
        data[(size_i, fname)][method][threads_i] = score

    # Build speedup table
    out_rows = []
    header = ["size", "filter", "threads",
              "sequential_ms", "executor_ms", "forkjoin_ms",
              "executor_speedup", "forkjoin_speedup"]
    print("\n" + "  ".join(f"{h:>16}" for h in header))
    print("-" * (18 * len(header)))

    for (size, fname) in sorted(data.keys(), key=lambda k: (k[0], str(k[1]))):
        methods = data[(size, fname)]
        # sequential baseline: use threads=1 sequential score (sequential ignores threads,
        # so any threads key works; prefer 1)
        seq_scores = methods.get("sequential", {})
        if not seq_scores:
            continue
        seq_ms = seq_scores.get(1, next(iter(seq_scores.values())))

        for threads in sorted(set(
                list(methods.get("executorParallel", {}).keys())
                + list(methods.get("forkJoinParallel", {}).keys()))):
            exec_ms = methods.get("executorParallel", {}).get(threads)
            fj_ms = methods.get("forkJoinParallel", {}).get(threads)
            exec_sp = (seq_ms / exec_ms) if exec_ms else None
            fj_sp = (seq_ms / fj_ms) if fj_ms else None

            row = [size, fname, threads,
                   round(seq_ms, 3),
                   round(exec_ms, 3) if exec_ms else "",
                   round(fj_ms, 3) if fj_ms else "",
                   round(exec_sp, 2) if exec_sp else "",
                   round(fj_sp, 2) if fj_sp else ""]
            out_rows.append(row)
            print("  ".join(f"{str(v):>16}" for v in row))

    # Write tidy CSV
    with open("speedup_table.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(out_rows)
    print("\nWrote speedup_table.csv")

    # Optional charts
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        filters = sorted({fname for (_, fname) in data.keys()})
        colors = ["tab:blue", "tab:orange", "tab:green"]

        # Per-filter: Executor vs ForkJoin, largest image only (2048)
        for fname in filters:
            fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
            fig.suptitle(f"Speedup vs Threads — {fname}", fontsize=13)
            sizes = sorted({size for (size, fn) in data.keys() if fn == fname})

            for ax, (method_key, method_label) in zip(
                    axes,
                    [("executorParallel", "ExecutorService"), ("forkJoinParallel", "ForkJoinPool")]):
                for size, color in zip(sizes, colors):
                    methods = data[(size, fname)]
                    seq_scores = methods.get("sequential", {})
                    if not seq_scores:
                        continue
                    seq_ms = seq_scores.get(1, next(iter(seq_scores.values())))
                    threads_sorted = sorted(methods.get(method_key, {}).keys())
                    if not threads_sorted:
                        continue
                    speedups = [seq_ms / methods[method_key][t] for t in threads_sorted]
                    ax.plot(threads_sorted, speedups, marker="o", color=color,
                            label=f"{size}x{size}")
                ax.plot([1, 8], [1, 8], "k--", alpha=0.35, label="ideal")
                ax.set_title(method_label)
                ax.set_xlabel("Thread count")
                ax.set_ylabel("Speedup (T_seq / T_par)")
                ax.legend(fontsize=8)
                ax.grid(True, alpha=0.3)

            plt.tight_layout()
            out = f"speedup_{fname}.png"
            plt.savefig(out, dpi=120, bbox_inches="tight")
            plt.close()
            print("Wrote", out)

        # Combined: all filters on one chart (2048x2048, Executor)
        plt.figure(figsize=(7, 5))
        filter_colors = {"GaussianBlur5x5": "tab:red", "Sobel3x3": "tab:blue", "Grayscale": "tab:green"}
        for fname in filters:
            methods = data.get((2048, fname), {})
            seq_scores = methods.get("sequential", {})
            if not seq_scores:
                continue
            seq_ms = seq_scores.get(1, next(iter(seq_scores.values())))
            threads_sorted = sorted(methods.get("executorParallel", {}).keys())
            if not threads_sorted:
                continue
            speedups = [seq_ms / methods["executorParallel"][t] for t in threads_sorted]
            plt.plot(threads_sorted, speedups, marker="o",
                     color=filter_colors.get(fname, "gray"), label=fname)
        plt.plot([1, 8], [1, 8], "k--", alpha=0.35, label="ideal (linear)")
        plt.title("Speedup vs Threads — All Filters (2048×2048, Executor)")
        plt.xlabel("Thread count")
        plt.ylabel("Speedup (T_seq / T_par)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        out = "speedup_combined.png"
        plt.savefig(out, dpi=120, bbox_inches="tight")
        plt.close()
        print("Wrote", out)
    except ImportError:
        print("\n(matplotlib not installed — skipping charts. "
              "Install with: pip install matplotlib)")


if __name__ == "__main__":
    main()
