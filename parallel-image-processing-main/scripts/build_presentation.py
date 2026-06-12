#!/usr/bin/env python3
"""Build the final Submission 2 presentation (self-contained HTML, arrow-key navigation)."""

import base64, os, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def img_b64(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg":"jpeg","jpeg":"jpeg","png":"png"}.get(ext,"png")
    with open(path,"rb") as f:
        return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"

orig  = img_b64(os.path.join(BASE,"test.jpg"))
gray  = img_b64(os.path.join(BASE,"test_Grayscale.png"))
blur  = img_b64(os.path.join(BASE,"test_GaussianBlur5x5.png"))
sobel = img_b64(os.path.join(BASE,"test_Sobel3x3.png"))

with open(os.path.join(BASE,"scripts","_charts.json")) as f:
    charts = json.load(f)
def chart(k): return f"data:image/png;base64,{charts[k]}"

slides_html = []

def slide(content, cls=""):
    slides_html.append(f'<section class="slide {cls}">{content}</section>')

# ── SLIDE 1: Title ────────────────────────────────────────────────────────────
slide(f"""
<div class="title-block">
  <div class="tag">CENG479 — Parallel Computing &nbsp;|&nbsp; Submission 2</div>
  <h1>Parallel Image Processing Engine</h1>
  <h2>Using Java Threads</h2>
  <div class="authors">
    <div class="author"><span class="dot"></span>Muhammed Çakırgöz</div>
    <div class="author"><span class="dot"></span>Musa Bilal Yaz</div>
  </div>
  <div class="institution">Gazi University · Department of Computer Engineering · Spring 2026</div>
</div>
<div class="slide-num-label">1 / 11</div>
""", "title-slide")

# ── SLIDE 2: Motivation ───────────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Problem & Motivation</h2>
<div class="two-col">
  <div>
    <h3>The Problem</h3>
    <ul>
      <li>A single 4K image has <strong>8+ million pixels</strong></li>
      <li>Convolution filter on 2048×2048 takes <strong>~200 ms</strong> sequentially</li>
      <li>Batch pipelines or real-time processing cannot afford this</li>
      <li>Single-core CPU performance has been stagnant since ~2005</li>
    </ul>
    <div class="callout blue" style="margin-top:18px">
      Modern CPUs have <strong>multiple cores</strong> —<br>
      can we exploit them for image filtering?
    </div>
  </div>
  <div>
    <h3>Key Insight: Pixel Independence</h3>
    <div class="callout green">
      Each output pixel depends only on a <em>fixed neighbourhood</em>
      of the <strong>input</strong> image.<br><br>
      → Zero write conflicts between pixels<br>
      → No locking needed<br>
      → Embarrassingly parallel
    </div>
    <div style="margin-top:16px;font-size:13px;color:#555">
      This is why image processing is a <em>textbook parallelism use case</em>.
    </div>
  </div>
</div>
<div class="presenter-tag">Muhammed Çakırgöz</div>
<div class="slide-num-label">2 / 11</div>
""")

# ── SLIDE 3: Solution Overview ────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Solution Design</h2>
<div class="arch-grid">
  <div class="arch-box blue-box">
    <div class="arch-title">Filters (×3)</div>
    <div class="arch-items">
      <div>🔲 Grayscale</div>
      <div>🌫️ Gaussian Blur 5×5</div>
      <div>📐 Sobel Edge Detection</div>
    </div>
  </div>
  <div class="arch-arrow">→</div>
  <div class="arch-box green-box">
    <div class="arch-title">Sequential Baseline</div>
    <div class="arch-items">
      <div><code>SequentialProcessor</code></div>
      <div>Single thread, row by row</div>
      <div>Reference for speedup</div>
    </div>
  </div>
  <div class="arch-arrow">vs</div>
  <div class="arch-box orange-box">
    <div class="arch-title">Parallel (×2)</div>
    <div class="arch-items">
      <div><code>ExecutorParallelProcessor</code></div>
      <div>Strip decomposition</div>
      <div class="sep"></div>
      <div><code>ForkJoinParallelProcessor</code></div>
      <div>Divide &amp; conquer</div>
    </div>
  </div>
</div>
<div style="text-align:center;margin-top:20px;font-size:13px;color:#444">
  Tested on: <strong>3 image sizes</strong> (512, 1024, 2048 px) ×
  <strong>4 thread counts</strong> (1, 2, 4, 8) ×
  <strong>3 filters</strong> = 36 configurations
</div>
<div class="presenter-tag">Muhammed Çakırgöz</div>
<div class="slide-num-label">3 / 11</div>
""")

# ── SLIDE 4: Filter Algorithms ────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Filter Algorithms</h2>
<div class="filter-grid">
  <div class="fcard">
    <div class="fcard-title">Grayscale</div>
    <div class="fcard-formula">Y = 0.299·R + 0.587·G + 0.114·B</div>
    <ul>
      <li>ITU-R BT.601 luminance</li>
      <li>Zero neighbours needed</li>
      <li>Memory-bandwidth limited</li>
    </ul>
  </div>
  <div class="fcard">
    <div class="fcard-title">Gaussian Blur 5×5</div>
    <div class="fcard-formula">25 multiply-adds / channel / px</div>
    <ul>
      <li>Pascal-triangle kernel</li>
      <li>Sum = 256 → normalise by shift</li>
      <li>Most compute-intensive</li>
    </ul>
  </div>
  <div class="fcard">
    <div class="fcard-title">Sobel Edge Detection</div>
    <div class="fcard-formula">|G| = √(Gx² + Gy²)</div>
    <ul>
      <li>Two 3×3 kernels (Gx, Gy)</li>
      <li>Applied to luminance channel</li>
      <li>Output: edge strength map</li>
    </ul>
  </div>
</div>
<div class="callout blue" style="margin-top:14px;text-align:center">
  Border pixels: <strong>edge-extend clamping</strong> (replicate nearest valid pixel) —
  identical in sequential &amp; parallel → bit-identical outputs guaranteed
</div>
<div class="presenter-tag">Muhammed Çakırgöz</div>
<div class="slide-num-label">4 / 11</div>
""")

# ── SLIDE 5: Executor Strategy ────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Parallel Strategy 1 — ExecutorService</h2>
<div class="two-col">
  <div>
    <h3>Strip Decomposition</h3>
    <div class="strip-diagram">
      <div class="strip s1">Thread 0<br><small>rows 0–511</small></div>
      <div class="strip s2">Thread 1<br><small>rows 512–1023</small></div>
      <div class="strip s3">Thread 2<br><small>rows 1024–1535</small></div>
      <div class="strip s4">Thread 3<br><small>rows 1536–2047</small></div>
    </div>
    <p style="font-size:12px;margin-top:8px;color:#555">
      N = thread count → N horizontal strips<br>
      Strip height = ⌈height / N⌉ (ceiling division)
    </p>
  </div>
  <div>
    <h3>Why No Locking?</h3>
    <ul>
      <li>Each task writes a <strong>disjoint row range</strong></li>
      <li>Source array is <strong>read-only</strong> during processing</li>
      <li>Halo reads (neighbouring rows) are fine — only writes conflict</li>
    </ul>
    <div class="callout green" style="margin-top:14px">
      <code>invokeAll(tasks)</code> + <code>Future.get()</code><br>
      → waits for all strips, propagates exceptions
    </div>
    <div style="margin-top:12px;font-size:12px">
      Pool is reused across calls via <code>AutoCloseable</code> —
      no per-image thread creation overhead.
    </div>
  </div>
</div>
<div class="presenter-tag">Muhammed Çakırgöz</div>
<div class="slide-num-label">5 / 11</div>
""")

# ── SLIDE 6: ForkJoin Strategy ────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Parallel Strategy 2 — ForkJoinPool</h2>
<div class="two-col">
  <div>
    <h3>Divide &amp; Conquer</h3>
    <div class="tree-diagram">
      <div class="tnode root">rows 0–2047</div>
      <div class="tree-children">
        <div class="tbranch">
          <div class="tnode">rows 0–1023</div>
          <div class="tree-children">
            <div class="tnode leaf">0–511</div>
            <div class="tnode leaf">512–1023</div>
          </div>
        </div>
        <div class="tbranch">
          <div class="tnode">rows 1024–2047</div>
          <div class="tree-children">
            <div class="tnode leaf">1024–1535</div>
            <div class="tnode leaf">1536–2047</div>
          </div>
        </div>
      </div>
    </div>
    <p style="font-size:11px;color:#555;margin-top:6px">Threshold = 32 rows → process directly</p>
  </div>
  <div>
    <h3>Work-Stealing Scheduler</h3>
    <ul>
      <li>Each thread has its own <strong>deque</strong> of tasks</li>
      <li>Idle threads <strong>steal</strong> from the tail of busy threads' queues</li>
      <li>Automatically balances uneven loads</li>
    </ul>
    <div class="compare-table" style="margin-top:14px;font-size:12px">
      <table>
        <tr><th></th><th>Executor</th><th>ForkJoin</th></tr>
        <tr><td>Decomposition</td><td>Static strips</td><td>Recursive halving</td></tr>
        <tr><td>Load balance</td><td>Fixed at start</td><td>Dynamic (stealing)</td></tr>
        <tr><td>Overhead</td><td>Lower</td><td>Higher (small images)</td></tr>
        <tr><td>Best for</td><td>Large, uniform</td><td>Small / uneven</td></tr>
      </table>
    </div>
  </div>
</div>
<div class="presenter-tag">Muhammed Çakırgöz</div>
<div class="slide-num-label">6 / 11</div>
""")

# ── SLIDE 7: Visual Demo ──────────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Demo — Filters Applied to Real Image</h2>
<div class="demo-gallery">
  <figure>
    <img src="{orig}" alt="Original">
    <figcaption><strong>Original</strong><br>225×225 px</figcaption>
  </figure>
  <figure>
    <img src="{gray}" alt="Grayscale">
    <figcaption><strong>Grayscale</strong><br>Y = 0.299R+0.587G+0.114B</figcaption>
  </figure>
  <figure>
    <img src="{blur}" alt="Gaussian Blur">
    <figcaption><strong>Gaussian Blur 5×5</strong><br>25 taps / pixel</figcaption>
  </figure>
  <figure>
    <img src="{sobel}" alt="Sobel">
    <figcaption><strong>Sobel 3×3</strong><br>Edge strength map</figcaption>
  </figure>
</div>
<div class="callout green" style="text-align:center;margin-top:16px;font-size:13px">
  ✓ All 3 filters × Executor × ForkJoin = <strong>6 correctness checks — all PASS</strong><br>
  Parallel outputs are <strong>bit-identical</strong> to sequential baseline
</div>
<div class="presenter-tag">Musa Bilal Yaz</div>
<div class="slide-num-label">7 / 11</div>
""")

# ── SLIDE 8: Benchmark Methodology + Summary Table ────────────────────────────
slide(f"""
<h2 class="sh">Benchmark Results — 2048 × 2048 (Focus)</h2>
<div class="callout blue" style="margin-bottom:12px;font-size:12px">
  <strong>Methodology:</strong> 5 warm-up iterations (JIT compile) + 10 measurement iterations (averaged)
  · Synthetic image, seed=42 · 16 logical threads (8 physical cores)
</div>
<table class="res-table">
  <thead><tr><th>Filter</th><th>Threads</th><th>Sequential</th><th>Executor</th><th>Exec Speedup</th><th>ForkJoin</th><th>FJ Speedup</th></tr></thead>
  <tbody>
    <tr class="r1"><td rowspan="4">Grayscale</td><td>1</td><td>19.37 ms</td><td>18.99 ms</td><td class="su ok">1.02×</td><td>21.12 ms</td><td class="su ok">0.92×</td></tr>
    <tr class="r1"><td>2</td><td>–</td><td>10.09 ms</td><td class="su ok">1.92×</td><td>12.92 ms</td><td class="su ok">1.50×</td></tr>
    <tr class="r1"><td>4</td><td>–</td><td>7.56 ms</td><td class="su med">2.56×</td><td>8.09 ms</td><td class="su med">2.39×</td></tr>
    <tr class="r1"><td>8</td><td>–</td><td>6.95 ms</td><td class="su med">2.79×</td><td>6.91 ms</td><td class="su med">2.80×</td></tr>
    <tr class="r2"><td rowspan="4">Gaussian Blur</td><td>1</td><td>209.13 ms</td><td>215.03 ms</td><td class="su ok">0.97×</td><td>228.35 ms</td><td class="su ok">0.92×</td></tr>
    <tr class="r2"><td>2</td><td>–</td><td>120.68 ms</td><td class="su med">1.73×</td><td>109.67 ms</td><td class="su med">1.91×</td></tr>
    <tr class="r2"><td>4</td><td>–</td><td>62.60 ms</td><td class="su good">3.34×</td><td>64.86 ms</td><td class="su good">3.22×</td></tr>
    <tr class="r2"><td>8</td><td>–</td><td>54.50 ms</td><td class="su good">3.84×</td><td>59.51 ms</td><td class="su good">3.51×</td></tr>
    <tr class="r3"><td rowspan="4">Sobel 3×3</td><td>1</td><td>112.95 ms</td><td>114.37 ms</td><td class="su ok">0.99×</td><td>118.90 ms</td><td class="su ok">0.95×</td></tr>
    <tr class="r3"><td>2</td><td>–</td><td>56.95 ms</td><td class="su med">1.98×</td><td>64.79 ms</td><td class="su med">1.74×</td></tr>
    <tr class="r3"><td>4</td><td>–</td><td>34.06 ms</td><td class="su good">3.32×</td><td>34.96 ms</td><td class="su good">3.23×</td></tr>
    <tr class="r3"><td>8</td><td>–</td><td>30.48 ms</td><td class="su good">3.71×</td><td>29.39 ms</td><td class="su good">3.84×</td></tr>
  </tbody>
</table>
<div class="presenter-tag">Musa Bilal Yaz</div>
<div class="slide-num-label">8 / 11</div>
""")

# ── SLIDE 9: Speedup Charts ────────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Speedup Analysis</h2>
<div style="text-align:center">
  <img src="{chart('speedup_executor')}" style="max-width:100%;border-radius:6px;border:1px solid #ddd">
  <p style="font-size:11px;color:#666;margin-top:6px">
    Figure — Executor speedup vs thread count across image sizes. Dashed = ideal linear scaling.
  </p>
</div>
<div class="presenter-tag">Musa Bilal Yaz</div>
<div class="slide-num-label">9 / 11</div>
""")

# ── SLIDE 10: Key Findings ────────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Key Findings</h2>
<div class="findings-grid">
  <div class="finding good">
    <div class="finding-icon">📈</div>
    <div class="finding-title">Compute-bound filters scale well</div>
    <div class="finding-body">
      Gaussian Blur &amp; Sobel reach <strong>~3.7–4.0×</strong> speedup at 8 threads (2048×2048).
      Efficiency ≈ 47–50% — consistent with Amdahl's Law.
    </div>
  </div>
  <div class="finding warn">
    <div class="finding-icon">📊</div>
    <div class="finding-title">Grayscale hits memory wall</div>
    <div class="finding-body">
      Only <strong>2.8×</strong> at 8 threads. Low arithmetic intensity means
      DRAM bandwidth is the bottleneck, not compute. Adding more threads doesn't help.
    </div>
  </div>
  <div class="finding neutral">
    <div class="finding-icon">⚖️</div>
    <div class="finding-title">ForkJoin ≈ Executor at large sizes</div>
    <div class="finding-body">
      At 2048×2048 results are comparable. ForkJoin wins on small images
      (512×512 Grayscale: <strong>6.53×</strong> vs 2.75×) — work-stealing
      redistributes tiny remaining work better.
    </div>
  </div>
  <div class="finding good">
    <div class="finding-icon">✅</div>
    <div class="finding-title">100% correctness</div>
    <div class="finding-body">
      All 6 (filter × implementation) combinations are
      <strong>bit-identical</strong> to sequential baseline.
      No locking required during compute phase.
    </div>
  </div>
</div>
<div class="presenter-tag">Musa Bilal Yaz</div>
<div class="slide-num-label">10 / 11</div>
""")

# ── SLIDE 11: Conclusion ──────────────────────────────────────────────────────
slide(f"""
<h2 class="sh">Conclusion & Future Work</h2>
<div class="two-col">
  <div>
    <h3>What We Achieved</h3>
    <ul>
      <li>Sequential baseline + 2 parallel implementations</li>
      <li>3 convolution filters, fully verified</li>
      <li>Up to <strong>4.0× speedup</strong> for compute-bound workloads</li>
      <li>Demonstrated memory-bandwidth ceiling for simple filters</li>
      <li>Clean Maven project, JMH-ready benchmark harness</li>
    </ul>
    <div class="callout green" style="margin-top:16px">
      <strong>Bottom line:</strong> Java Threads provide effective parallelism
      for image processing with zero data-race risk when partitions are disjoint.
    </div>
  </div>
  <div>
    <h3>Future Directions</h3>
    <ul>
      <li><strong>Separable Gaussian</strong> — two 1D passes instead of one 2D: O(2k) vs O(k²)</li>
      <li><strong>Java Vector API</strong> (JEP 426) for SIMD pixel operations</li>
      <li><strong>CUDA / GPU</strong> — thousands of cores, ideal for 4K+</li>
      <li><strong>Adaptive ForkJoin threshold</strong> based on image size &amp; core count</li>
      <li>Pipeline parallelism for multi-filter chains</li>
    </ul>
  </div>
</div>
<div style="text-align:center;margin-top:24px;padding:14px;background:#f0f7ff;border-radius:8px;font-size:13px">
  <strong>Thank you for listening!</strong> &nbsp;·&nbsp; Questions welcome
</div>
<div class="presenter-tag" style="right:20px">Musa Bilal Yaz</div>
<div class="slide-num-label">11 / 11</div>
""")

# ── Build HTML ────────────────────────────────────────────────────────────────
slides_joined = "\n".join(slides_html)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CENG479 — Parallel Image Processing — Presentation</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#1a1a2e; font-family:"Segoe UI",Arial,sans-serif;
       overflow:hidden; height:100vh; width:100vw; }}

/* ── slideshow container ── */
#deck {{ position:relative; width:100vw; height:100vh; }}
.slide {{
  display:none; position:absolute; inset:0;
  padding:44px 60px 36px;
  background:#ffffff;
  flex-direction:column;
  animation:fadeIn 0.25s ease;
}}
.slide.active {{ display:flex; }}
@keyframes fadeIn {{ from{{opacity:0;transform:translateY(6px)}} to{{opacity:1;transform:translateY(0)}} }}

/* ── title slide ── */
.title-slide {{ background:linear-gradient(135deg,#1a3a5c 0%,#2c5f8a 60%,#1a3a5c 100%);
                color:#fff; justify-content:center; align-items:center; text-align:center; }}
.title-block .tag {{ font-size:13px; opacity:.8; letter-spacing:1px; margin-bottom:18px; }}
.title-block h1 {{ font-size:32px; font-weight:700; line-height:1.2; margin-bottom:10px; }}
.title-block h2 {{ font-size:18px; font-weight:300; opacity:.85; margin-bottom:36px; }}
.authors {{ display:flex; gap:50px; justify-content:center; margin-bottom:30px; }}
.author {{ font-size:16px; display:flex; align-items:center; gap:8px; }}
.dot {{ width:8px;height:8px;background:#60b3f0;border-radius:50%;display:inline-block; }}
.institution {{ font-size:12px; opacity:.6; }}

/* ── section heading ── */
.sh {{ font-size:20px; color:#1a3a5c; border-bottom:3px solid #2980b9;
       padding-bottom:8px; margin-bottom:18px; }}

/* ── two-column ── */
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:30px; flex:1; }}
.two-col h3 {{ font-size:13px; color:#1a3a5c; margin-bottom:8px; border-left:3px solid #2980b9; padding-left:8px; }}
ul {{ padding-left:18px; font-size:13px; line-height:1.8; }}
li {{ margin-bottom:2px; }}

/* ── callout boxes ── */
.callout {{ border-radius:6px; padding:10px 14px; font-size:12px; line-height:1.6; }}
.callout.blue {{ background:#e8f4fd; border-left:4px solid #2980b9; }}
.callout.green {{ background:#e8f8ec; border-left:4px solid #27ae60; }}
.callout.orange {{ background:#fef9ec; border-left:4px solid #e67e22; }}

/* ── arch diagram ── */
.arch-grid {{ display:flex; align-items:center; gap:16px; flex:1; justify-content:center; margin-top:10px; }}
.arch-box {{ border-radius:8px; padding:16px 20px; min-width:180px; text-align:center; }}
.blue-box {{ background:#e8f4fd; border:2px solid #2980b9; }}
.green-box {{ background:#e8f8ec; border:2px solid #27ae60; }}
.orange-box {{ background:#fef9ec; border:2px solid #e67e22; }}
.arch-title {{ font-weight:700; font-size:13px; margin-bottom:10px; }}
.arch-items {{ font-size:12px; line-height:1.8; }}
.arch-arrow {{ font-size:22px; color:#888; font-weight:bold; }}
.sep {{ border-top:1px solid #ccc; margin:6px 0; }}
code {{ background:#f0f0f0; padding:1px 5px; border-radius:3px; font-size:11px; font-family:Consolas,monospace; }}

/* ── filter cards ── */
.filter-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; flex:1; margin-top:4px; }}
.fcard {{ background:#f8f9fa; border:1px solid #dee2e6; border-radius:8px; padding:16px; }}
.fcard-title {{ font-weight:700; font-size:14px; color:#1a3a5c; margin-bottom:8px; }}
.fcard-formula {{ background:#fff3cd; border-radius:4px; padding:6px 10px; font-family:Consolas,monospace;
                  font-size:12px; margin-bottom:10px; text-align:center; }}
.fcard ul {{ font-size:12px; }}

/* ── strip diagram ── */
.strip-diagram {{ display:flex; flex-direction:column; gap:3px; border:2px solid #ccc; border-radius:4px; overflow:hidden; }}
.strip {{ padding:8px 12px; font-size:12px; font-weight:600; color:#fff; text-align:center; }}
.s1 {{ background:#4e79a7; }} .s2 {{ background:#f28e2b; }}
.s3 {{ background:#e15759; }} .s4 {{ background:#76b7b2; }}

/* ── tree diagram ── */
.tree-diagram {{ text-align:center; margin-top:8px; }}
.tnode {{ display:inline-block; background:#e8f4fd; border:1px solid #2980b9; border-radius:4px;
          padding:4px 10px; font-size:11px; margin:2px; }}
.root {{ background:#2980b9; color:#fff; font-weight:700; font-size:12px; }}
.leaf {{ background:#e8f8ec; border-color:#27ae60; }}
.tree-children {{ display:flex; justify-content:center; gap:20px; margin-top:8px; position:relative; }}
.tbranch {{ display:flex; flex-direction:column; align-items:center; gap:4px; }}

/* ── compare table ── */
.compare-table table {{ border-collapse:collapse; width:100%; font-size:12px; }}
.compare-table th {{ background:#1a3a5c; color:#fff; padding:5px 8px; }}
.compare-table td {{ border-bottom:1px solid #eee; padding:4px 8px; }}

/* ── demo gallery ── */
.demo-gallery {{ display:flex; gap:20px; justify-content:center; align-items:flex-start; flex:1; margin-top:8px; }}
.demo-gallery figure {{ text-align:center; }}
.demo-gallery img {{ width:175px; height:175px; object-fit:contain; border:2px solid #dee2e6; border-radius:6px; }}
.demo-gallery figcaption {{ font-size:12px; color:#555; margin-top:6px; line-height:1.4; }}

/* ── results table ── */
.res-table {{ border-collapse:collapse; width:100%; font-size:12px; flex:1; }}
.res-table th {{ background:#1a3a5c; color:#fff; padding:6px 8px; text-align:left; }}
.res-table td {{ padding:4px 8px; border-bottom:1px solid #eee; }}
.r1 td {{ background:#fafcff; }} .r2 td {{ background:#fffaf5; }} .r3 td {{ background:#f5fff8; }}
.su {{ font-weight:700; }}
.su.ok {{ color:#888; }} .su.med {{ color:#b8860b; }} .su.good {{ color:#27ae60; }}

/* ── findings grid ── */
.findings-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; flex:1; margin-top:4px; }}
.finding {{ border-radius:8px; padding:14px 16px; display:flex; flex-direction:column; gap:6px; }}
.finding.good {{ background:#e8f8ec; border-left:4px solid #27ae60; }}
.finding.warn {{ background:#fef9ec; border-left:4px solid #e67e22; }}
.finding.neutral {{ background:#f0f4ff; border-left:4px solid #6c8ebf; }}
.finding-icon {{ font-size:20px; }}
.finding-title {{ font-weight:700; font-size:13px; color:#1a3a5c; }}
.finding-body {{ font-size:12px; line-height:1.6; color:#333; }}

/* ── presenter badge ── */
.presenter-tag {{
  position:absolute; bottom:16px; right:20px;
  font-size:11px; color:#fff; background:#2980b9;
  padding:3px 10px; border-radius:12px; opacity:.85;
}}
.slide-num-label {{
  position:absolute; bottom:16px; left:20px;
  font-size:11px; color:#aaa;
}}

/* ── nav bar ── */
#nav {{
  position:fixed; bottom:0; left:0; right:0; height:48px;
  background:#1a1a2e; display:flex; align-items:center;
  justify-content:center; gap:16px; z-index:100;
}}
#nav button {{
  background:#2980b9; color:#fff; border:none; border-radius:6px;
  padding:7px 20px; cursor:pointer; font-size:13px;
}}
#nav button:hover {{ background:#3498db; }}
#nav button:disabled {{ background:#444; cursor:not-allowed; }}
#nav #counter {{ color:#aaa; font-size:13px; min-width:60px; text-align:center; }}
#nav .hint {{ color:#666; font-size:11px; }}

/* fullscreen mode */
body.fullscreen .slide {{ padding:60px 80px 60px; }}
body.fullscreen #nav {{ display:none; }}
</style>
</head>
<body>
<div id="deck">
{slides_joined}
</div>

<div id="nav">
  <button id="btnFirst" onclick="go(0)">⏮</button>
  <button id="btnPrev"  onclick="prev()">◀ Prev</button>
  <span id="counter">1 / 11</span>
  <button id="btnNext"  onclick="next()">Next ▶</button>
  <button id="btnLast"  onclick="go(total-1)">⏭</button>
  <span class="hint">← → arrow keys &nbsp;·&nbsp; F = fullscreen &nbsp;·&nbsp; Esc = exit</span>
</div>

<script>
const slides = document.querySelectorAll('.slide');
const total  = slides.length;
let cur = 0;

function show(n) {{
  slides[cur].classList.remove('active');
  cur = Math.max(0, Math.min(n, total-1));
  slides[cur].classList.add('active');
  document.getElementById('counter').textContent = (cur+1) + ' / ' + total;
  document.getElementById('btnPrev').disabled  = cur === 0;
  document.getElementById('btnFirst').disabled = cur === 0;
  document.getElementById('btnNext').disabled  = cur === total-1;
  document.getElementById('btnLast').disabled  = cur === total-1;
}}

function go(n)   {{ show(n); }}
function next()  {{ show(cur+1); }}
function prev()  {{ show(cur-1); }}

document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ')  next();
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   prev();
  if (e.key === 'Home') go(0);
  if (e.key === 'End')  go(total-1);
  if (e.key === 'f' || e.key === 'F') {{
    document.body.classList.toggle('fullscreen');
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen();
  }}
}});

show(0);
</script>
</body>
</html>
"""

out = os.path.join(BASE, "CENG479_Presentation.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("Presentation written to", out)
print(f"File size: {os.path.getsize(out)//1024} KB")
