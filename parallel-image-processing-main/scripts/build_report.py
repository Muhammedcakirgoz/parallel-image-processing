#!/usr/bin/env python3
"""Build the final Submission 2 HTML report with all images embedded."""

import base64, csv, json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def img_b64(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}.get(ext, "png")
    with open(path, "rb") as f:
        return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode()}"

# load images
orig   = img_b64(os.path.join(BASE, "test.jpg"))
gray   = img_b64(os.path.join(BASE, "test_Grayscale.png"))
blur   = img_b64(os.path.join(BASE, "test_GaussianBlur5x5.png"))
sobel  = img_b64(os.path.join(BASE, "test_Sobel3x3.png"))

# load charts
with open(os.path.join(BASE, "scripts", "_charts.json")) as f:
    charts = json.load(f)

def chart(key):
    return f"data:image/png;base64,{charts[key]}"

# load CSV rows
rows = []
with open(os.path.join(BASE, "speedup_table.csv")) as f:
    for r in csv.DictReader(f):
        rows.append(r)

def perf_table(size):
    cols = ["filter","threads","sequential_ms","executor_ms","forkjoin_ms","executor_speedup","forkjoin_speedup"]
    headers = ["Filter","Threads","Seq (ms)","Executor (ms)","ForkJoin (ms)","Exec Speedup","FJ Speedup"]
    html = '<table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
    prev_filter = None
    for r in rows:
        if int(r["size"]) != size:
            continue
        f = r["filter"]
        rowclass = "alt" if f != prev_filter and prev_filter is not None else ""
        prev_filter = f
        def su_cell(v):
            try:
                v = float(v)
                color = "#2d7a2d" if v >= 3 else ("#b8860b" if v >= 1.5 else "#c0392b")
                return f'<td style="color:{color};font-weight:bold">{v:.2f}×</td>'
            except: return f'<td>{v}</td>'
        html += f'<tr class="{rowclass}"><td>{f}</td><td>{r["threads"]}</td>'
        html += f'<td>{float(r["sequential_ms"]):.2f}</td>'
        html += f'<td>{float(r["executor_ms"]):.2f}</td>'
        html += f'<td>{float(r["forkjoin_ms"]):.2f}</td>'
        html += su_cell(r["executor_speedup"])
        html += su_cell(r["forkjoin_speedup"])
        html += '</tr>'
    html += '</tbody></table>'
    return html

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CENG479 — Parallel Image Processing — Submission 2</title>
<style>
  :root {{
    --blue:#1a3a5c; --accent:#2980b9; --light:#ecf4fb;
    --green:#2d7a2d; --orange:#b8860b; --red:#c0392b;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ font-family:"Segoe UI",Arial,sans-serif; font-size:13px;
         color:#222; background:#f9f9f9; }}
  .page {{ max-width:960px; margin:0 auto; background:#fff;
           padding:48px 56px; box-shadow:0 2px 16px #0001; }}

  /* cover */
  .cover {{ text-align:center; padding:40px 0 48px; border-bottom:3px solid var(--blue); margin-bottom:40px; }}
  .cover h1 {{ font-size:24px; color:var(--blue); margin-bottom:8px; }}
  .cover h2 {{ font-size:15px; font-weight:normal; color:#555; margin-bottom:20px; }}
  .cover .meta {{ display:flex; justify-content:center; gap:60px; margin-top:20px; }}
  .cover .meta div {{ font-size:12px; }}
  .cover .meta strong {{ display:block; font-size:13px; margin-bottom:4px; color:var(--blue); }}

  /* sections */
  h2.sec {{ font-size:16px; color:var(--blue); border-left:4px solid var(--accent);
             padding-left:10px; margin:36px 0 14px; }}
  h3.sub {{ font-size:13px; color:#333; margin:20px 0 8px; font-weight:600; }}
  p {{ line-height:1.7; margin-bottom:10px; }}
  ul, ol {{ padding-left:22px; line-height:1.8; margin-bottom:10px; }}
  code {{ background:#f0f0f0; padding:1px 4px; border-radius:3px;
          font-family:Consolas,monospace; font-size:12px; }}

  /* image gallery */
  .gallery {{ display:flex; gap:14px; justify-content:center; margin:20px 0; flex-wrap:wrap; }}
  .gallery figure {{ text-align:center; }}
  .gallery img {{ width:180px; height:180px; object-fit:contain;
                  border:1px solid #ddd; border-radius:6px; display:block; }}
  .gallery figcaption {{ font-size:11px; color:#666; margin-top:5px; }}

  /* tables */
  table {{ border-collapse:collapse; width:100%; margin:14px 0; font-size:12px; }}
  th {{ background:var(--blue); color:#fff; padding:7px 10px; text-align:left; }}
  td {{ padding:5px 10px; border-bottom:1px solid #e8e8e8; }}
  tr.alt td {{ background:var(--light); }}
  tr:hover td {{ background:#fef9e7; }}

  /* chart */
  .chart {{ text-align:center; margin:20px 0; }}
  .chart img {{ max-width:100%; border:1px solid #e0e0e0; border-radius:6px; }}
  .chart figcaption {{ font-size:11px; color:#666; margin-top:5px; }}

  /* info boxes */
  .box {{ background:var(--light); border-left:4px solid var(--accent);
          padding:12px 16px; margin:14px 0; border-radius:0 6px 6px 0; font-size:12px; }}
  .box.green {{ background:#f0faf0; border-color:var(--green); }}
  .box.orange {{ background:#fdf8ec; border-color:var(--orange); }}

  /* references */
  .refs ol {{ font-size:12px; line-height:1.8; }}

  /* page break for printing */
  @media print {{
    .page {{ box-shadow:none; padding:20px; }}
    h2.sec {{ page-break-before:auto; }}
  }}
</style>
</head>
<body>
<div class="page">

<!-- ═══════════════════ COVER ═══════════════════ -->
<div class="cover">
  <h1>Parallel Image Processing Engine Using Java Threads</h1>
  <h2>CENG479 — Parallel Computing &nbsp;|&nbsp; Submission 2: Implementation Report</h2>
  <div class="meta">
    <div><strong>Institution</strong>Gazi University<br>Department of Computer Engineering</div>
    <div><strong>Team</strong>Muhammed Çakırgöz<br>Musa Bilal Yaz</div>
    <div><strong>Date</strong>June 2026<br>Spring Semester</div>
  </div>
</div>

<!-- ═══════════════════ 1. INTRODUCTION ═══════════════════ -->
<h2 class="sec">1. Introduction</h2>
<p>
High-resolution image processing is a computationally intensive task that represents an ideal
candidate for parallel execution. A single 4K image (3840 × 2160 pixels) contains more than
8 million pixels; applying a convolution filter naively requires processing each pixel
sequentially, which becomes a significant bottleneck in real-time or batch pipelines.
</p>
<p>
This project implements a <strong>Parallel Image Processing Engine</strong> in Java that applies
three convolution-based filters — Grayscale conversion, Gaussian Blur (5×5), and Sobel edge
detection (3×3) — to large synthetic images. Two parallel strategies are compared against a
sequential baseline:
</p>
<ul>
  <li><strong>ExecutorService</strong> with a fixed thread pool and horizontal strip decomposition.</li>
  <li><strong>ForkJoinPool</strong> with a recursive divide-and-conquer decomposition and work-stealing scheduler.</li>
</ul>
<p>
Performance is evaluated across three image sizes (512, 1024, 2048 pixels square) and four
thread counts (1, 2, 4, 8), with correctness verified pixel-for-pixel against the sequential output.
</p>

<!-- ═══════════════════ 2. SEQUENTIAL BASELINE ═══════════════════ -->
<h2 class="sec">2. Sequential Baseline Implementation</h2>
<p>
The <code>SequentialProcessor</code> class provides the reference implementation. It iterates
over every pixel in row-major order on a single thread:
</p>
<pre style="background:#f5f5f5;padding:12px;border-radius:6px;font-size:12px;overflow-x:auto"><code>for (int y = 0; y &lt; height; y++) &#123;
    int rowBase = y * width;
    for (int x = 0; x &lt; width; x++) &#123;
        dst[rowBase + x] = filter.applyPixel(src, width, height, x, y);
    &#125;
&#125;</code></pre>
<p>
All filters implement the <code>Filter</code> interface, which exposes a single
<code>applyPixel(src, width, height, x, y)</code> method. This design lets both sequential
and parallel processors use the same filter objects without modification.
</p>

<h3 class="sub">2.1 Filters</h3>
<p><strong>Grayscale</strong> uses the ITU-R BT.601 luminance formula:</p>
<p style="margin-left:20px"><code>Y = 0.299·R + 0.587·G + 0.114·B</code></p>
<p>
Since each output pixel depends only on the same (x, y) input pixel, there is
<em>zero inter-pixel dependency</em>. This makes it theoretically ideal for parallelism,
though in practice the memory bandwidth becomes the bottleneck.
</p>
<p>
<strong>Gaussian Blur (5×5)</strong> uses a Pascal-triangle kernel with integer weights
summing to 256 (normalization is a bit-shift). Each output pixel reads a 5×5 neighbourhood
(25 pixels) from the source — 25 multiply-accumulate operations per channel, making it the
most compute-intensive filter.
</p>
<p>
<strong>Sobel Edge Detection (3×3)</strong> computes horizontal (Gx) and vertical (Gy)
gradient components from the luminance of each 3×3 neighbourhood and combines them as
<code>magnitude = √(Gx² + Gy²)</code>. The result is a grayscale edge-strength map.
</p>

<!-- visual outputs -->
<h3 class="sub">2.2 Visual Output on Test Image</h3>
<div class="gallery">
  <figure>
    <img src="{orig}" alt="Original">
    <figcaption>Original (225×225)</figcaption>
  </figure>
  <figure>
    <img src="{gray}" alt="Grayscale">
    <figcaption>Grayscale</figcaption>
  </figure>
  <figure>
    <img src="{blur}" alt="Gaussian Blur 5×5">
    <figcaption>Gaussian Blur 5×5</figcaption>
  </figure>
  <figure>
    <img src="{sobel}" alt="Sobel 3×3">
    <figcaption>Sobel 3×3</figcaption>
  </figure>
</div>
<p style="font-size:11px;color:#666;text-align:center">
Figure 1 — All three filters applied to the test image using the parallel Executor processor.
Correctness verified: outputs are bit-identical to the sequential baseline.
</p>

<!-- ═══════════════════ 3. PARALLEL IMPLEMENTATION ═══════════════════ -->
<h2 class="sec">3. Parallel Implementation</h2>

<h3 class="sub">3.1 Strip-Based Decomposition (ExecutorService)</h3>
<p>
<code>ExecutorParallelProcessor</code> divides the image into <em>N horizontal strips</em>,
where <em>N</em> equals the requested thread count. Each strip is a contiguous block of rows
submitted as a <code>Callable&lt;Void&gt;</code> to a fixed-size thread pool
(<code>Executors.newFixedThreadPool(N)</code>). Key design choices:
</p>
<ul>
  <li><strong>No locking during compute.</strong> Each task writes to a disjoint slice of the
      output array; the source array is read-only. No <code>synchronized</code> blocks or
      locks are needed.</li>
  <li><strong>Ceiling division</strong> — <code>rowsPerStrip = ⌈height / N⌉</code> —
      ensures no rows are missed when height is not divisible by N.</li>
  <li><strong>Halo reads.</strong> Border pixels of a strip freely read neighbouring rows
      from adjacent strips via clamped coordinates; only writes are disjoint.</li>
  <li><code>Future.get()</code> is called after <code>invokeAll()</code> to propagate any
      worker exception.</li>
</ul>

<h3 class="sub">3.2 Divide-and-Conquer Decomposition (ForkJoinPool)</h3>
<p>
<code>ForkJoinParallelProcessor</code> uses a <code>RecursiveAction</code> that recursively
halves the row range until it falls below a threshold (default 32 rows), at which point rows
are processed directly. The ForkJoin framework's <em>work-stealing</em> scheduler
automatically rebalances load when threads finish early — beneficial when per-pixel cost
varies or OS scheduling is uneven.
</p>
<div class="box">
  <strong>Thread-safety guarantee (both implementations):</strong>
  Disjoint row partitions + read-only source array → zero data races → no synchronisation
  primitives needed during the compute phase.
</div>

<!-- ═══════════════════ 4. PERFORMANCE ANALYSIS ═══════════════════ -->
<h2 class="sec">4. Performance Comparison</h2>

<div class="box orange">
  <strong>Methodology:</strong> 5 JVM warm-up iterations (discarded) + 10 measurement
  iterations (averaged). Image pixels generated synthetically from a fixed seed (42) for
  reproducibility. Machine: 16 logical threads (8 physical cores).
</div>

<h3 class="sub">4.1 Results — 512 × 512</h3>
{perf_table(512)}

<h3 class="sub">4.2 Results — 1024 × 1024</h3>
{perf_table(1024)}

<h3 class="sub">4.3 Results — 2048 × 2048</h3>
{perf_table(2048)}

<h3 class="sub">4.4 Speedup Charts — Executor</h3>
<div class="chart">
  <figure>
    <img src="{chart('speedup_executor')}" alt="Executor Speedup">
    <figcaption>Figure 2 — Executor speedup vs thread count for all filters and image sizes.
    Dashed line = ideal linear speedup.</figcaption>
  </figure>
</div>

<h3 class="sub">4.5 Speedup Charts — ForkJoin</h3>
<div class="chart">
  <figure>
    <img src="{chart('speedup_forkjoin')}" alt="ForkJoin Speedup">
    <figcaption>Figure 3 — ForkJoin speedup vs thread count.</figcaption>
  </figure>
</div>

<h3 class="sub">4.6 Executor vs ForkJoin — 2048 × 2048</h3>
<div class="chart">
  <figure>
    <img src="{chart('exec_vs_fj')}" alt="Executor vs ForkJoin">
    <figcaption>Figure 4 — Speedup comparison between both parallel implementations
    on the largest (2048×2048) image.</figcaption>
  </figure>
</div>

<h3 class="sub">4.7 Execution Time — 2048 × 2048, 8 Threads</h3>
<div class="chart">
  <figure>
    <img src="{chart('time_2048_8t')}" alt="Execution time 2048 8T">
    <figcaption>Figure 5 — Absolute execution times for sequential vs. both parallel
    implementations (2048×2048, 8 threads).</figcaption>
  </figure>
</div>

<h3 class="sub">4.8 Analysis and Discussion</h3>
<p>
<strong>Compute-bound filters scale well.</strong>
Gaussian Blur and Sobel achieve ~3.7–4.0× speedup at 8 threads on a 2048×2048 image.
The efficiency (speedup / thread-count) is approximately 46–50%, consistent with Amdahl's
Law for workloads with a small sequential fraction (image I/O, array allocation).
</p>
<p>
<strong>Grayscale is memory-bandwidth limited.</strong>
At 8 threads and 2048×2048, both implementations achieve only ~2.8× — well below the
thread count. Each output pixel reads three channels and writes one; the arithmetic
intensity is too low to keep multiple cores busy. Adding more threads saturates the
memory bus without a proportional speedup gain.
</p>
<p>
<strong>ForkJoin vs Executor.</strong>
For small images (512×512), ForkJoin occasionally outperforms Executor because the
work-stealing scheduler rebalances the tiny remaining work more aggressively. For large
images, both strategies deliver comparable results; Executor's static strip layout has
lower scheduling overhead at high thread counts.
</p>
<div class="box green">
  <strong>Correctness:</strong> All parallel outputs are bit-identical to the sequential
  baseline, verified pixel-for-pixel by <code>CorrectnessVerifier.identical()</code>
  for all filter × thread-count combinations.
</div>

<!-- ═══════════════════ 5. ACADEMIC BACKGROUND ═══════════════════ -->
<h2 class="sec">5. Academic Background</h2>
<p>
The theoretical maximum speedup for a program with parallel fraction <em>p</em> using
<em>N</em> processors is given by <strong>Amdahl's Law</strong> (Amdahl, 1967):
</p>
<p style="text-align:center;font-size:14px;margin:10px 0">
  <em>S(N) = 1 / [(1 − p) + p/N]</em>
</p>
<p>
For our workloads, the parallel fraction is approximately 95–98% (allocation and scheduling
account for the remainder), implying a theoretical ceiling of ~20–50× — far above what we
observe at 8 threads, suggesting memory-bandwidth rather than Amdahl overhead is the binding
constraint for memory-bound filters.
</p>
<p>
<strong>Strip-based image decomposition</strong> is a well-established technique in parallel
image processing (Gonzalez &amp; Woods, 2018). It maximises spatial locality (each thread
works on a contiguous block of rows) while eliminating write contention.
</p>
<p>
<strong>Work-stealing schedulers</strong> (Blumofe &amp; Leiserson, 1999) achieve near-optimal
load balancing for irregular workloads by allowing idle processors to steal tasks from the
queues of busy ones. Java's <code>ForkJoinPool</code> implements this model
(Lea, 2000), making it well-suited to divide-and-conquer parallelism.
</p>
<p>
<strong>Memory-bound vs compute-bound behaviour</strong> in parallel image processing has been
studied extensively (Kirk &amp; Hwu, 2016). Simple point operations such as grayscale
conversion are limited by DRAM bandwidth rather than arithmetic throughput, explaining the
sub-linear speedup observed for that filter.
</p>

<!-- ═══════════════════ 6. CHALLENGES ═══════════════════ -->
<h2 class="sec">6. Challenges and Solutions</h2>
<ul>
  <li>
    <strong>JVM JIT warm-up bias.</strong> Initial runs showed artificially high sequential
    times because the JIT compiler had not yet compiled the hot loops. Resolved by adding
    5 warm-up iterations before every measurement window.
  </li>
  <li>
    <strong>Edge-pixel correctness.</strong> Convolution kernels extend beyond the image
    boundary at border pixels. Solved with <em>edge-extend clamping</em>
    (<code>PixelUtils.clampCoord</code>), which replicates the nearest valid pixel.
    This strategy is equivalent across sequential and parallel paths, guaranteeing
    identical outputs.
  </li>
  <li>
    <strong>Strip imbalance with non-divisible heights.</strong> Using ceiling division
    (<code>⌈height / N⌉</code>) ensures the last strip may be shorter than others, but no
    rows are missed and no thread processes out-of-bound rows.
  </li>
  <li>
    <strong>Overhead at small image sizes.</strong> At 512×512, thread creation and
    task-dispatch overhead sometimes exceeds the compute saving — visible as
    speedup&nbsp;&lt;&nbsp;1 for single-thread parallel runs. This is expected and well-known
    in parallel computing literature; parallelism is beneficial only when the workload is
    large enough.
  </li>
</ul>

<!-- ═══════════════════ 7. CONCLUSION ═══════════════════ -->
<h2 class="sec">7. Conclusion and Future Work</h2>
<p>
This project demonstrates that Java's concurrency framework provides an accessible and
effective path to parallelising compute-intensive image-processing workloads. On a 2048×2048
image, both implementations achieve approximately <strong>3.7–4.0× speedup</strong> for
compute-bound filters (Gaussian Blur, Sobel) with 8 threads, while the memory-bound
Grayscale filter plateaus at ~2.8×.
</p>
<p>
The two parallel strategies offer different trade-offs: Executor's static strip layout is
predictable and low-overhead; ForkJoin's work-stealing provides better load balancing for
uneven workloads and smaller images.
</p>
<p><strong>Future improvements:</strong></p>
<ul>
  <li>Separable Gaussian Blur — decompose the 2D convolution into two 1D passes to reduce
      per-pixel operations from O(k²) to O(2k).</li>
  <li>SIMD intrinsics via the Java Vector API (JEP 426) for pixel-level data parallelism.</li>
  <li>GPU implementation with NVIDIA CUDA for massive throughput on 4K+ images.</li>
  <li>Adaptive threshold selection for ForkJoin based on image size and available cores.</li>
</ul>

<!-- ═══════════════════ 8. REFERENCES ═══════════════════ -->
<h2 class="sec">8. References</h2>
<div class="refs">
<ol>
  <li>
    Amdahl, G. M. (1967). Validity of the single processor approach to achieving large
    scale computing capabilities. <em>Proceedings of the AFIPS Spring Joint Computer
    Conference</em>, 483–485. <a href="https://doi.org/10.1145/1465482.1465560">https://doi.org/10.1145/1465482.1465560</a>
  </li>
  <li>
    Blumofe, R. D., &amp; Leiserson, C. E. (1999). Scheduling multithreaded computations by
    work stealing. <em>Journal of the ACM, 46</em>(5), 720–748.
    <a href="https://doi.org/10.1145/324133.324234">https://doi.org/10.1145/324133.324234</a>
  </li>
  <li>
    Gonzalez, R. C., &amp; Woods, R. E. (2018). <em>Digital Image Processing</em> (4th ed.).
    Pearson.
  </li>
  <li>
    Kirk, D. B., &amp; Hwu, W.-m. W. (2016). <em>Programming Massively Parallel Processors:
    A Hands-on Approach</em> (3rd ed.). Morgan Kaufmann.
  </li>
  <li>
    Lea, D. (2000). A Java fork/join framework. <em>Proceedings of the ACM 2000 Conference
    on Java Grande</em>, 36–43.
    <a href="https://doi.org/10.1145/337449.337465">https://doi.org/10.1145/337449.337465</a>
  </li>
  <li>
    Oracle Corporation. (2023). <em>Java SE 17 API Documentation: java.util.concurrent</em>.
    Retrieved from https://docs.oracle.com/en/java/docs/api/java.base/java/util/concurrent/package-summary.html
  </li>
</ol>
</div>

<hr style="margin:40px 0 20px;border:none;border-top:1px solid #ddd">
<p style="font-size:10px;color:#aaa;text-align:center">
CENG479 Parallel Computing — Gazi University, Department of Computer Engineering — Spring 2026
</p>
</div>
</body>
</html>
"""

out = os.path.join(BASE, "CENG479_Submission2_Report.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("Report written to", out)
print(f"File size: {os.path.getsize(out)//1024} KB")
