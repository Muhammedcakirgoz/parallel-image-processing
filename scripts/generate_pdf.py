"""
generate_pdf.py  —  CENG 479 Sub2 Final Report + Presentation (single PDF)
Usage: python scripts/generate_pdf.py
Output: CENG479_Sub2_Final_Report.pdf
"""

import csv, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable

# ── colours ──────────────────────────────────────────────────────────────────
BLUE      = colors.HexColor("#1a3a6b")
BLUE_LIGHT= colors.HexColor("#2e6db4")
GRAY      = colors.HexColor("#555555")
GRAY_LITE = colors.HexColor("#f4f4f4")
ACCENT    = colors.HexColor("#e8f0fc")
WHITE     = colors.white
BLACK     = colors.black
GREEN     = colors.HexColor("#1a7a3a")
SLIDE_BG  = colors.HexColor("#1a3a6b")
SLIDE_ACC = colors.HexColor("#f0c040")

GITHUB    = "https://github.com/Muhammedcakirgoz/parallel-image-processing"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def img(name, w, h=None):
    path = os.path.join(BASE, name)
    if not os.path.exists(path):
        return Spacer(1, 0.3*cm)
    i = Image(path, width=w)
    if h:
        i.drawHeight = h
    return i

# ── styles ────────────────────────────────────────────────────────────────────
def make_styles():
    s = getSampleStyleSheet()

    def add(name, **kw):
        s.add(ParagraphStyle(name=name, **kw))

    add("CoverTitle",   fontName="Helvetica-Bold", fontSize=24,
        textColor=WHITE,  alignment=TA_CENTER, spaceAfter=8)
    add("CoverSub",     fontName="Helvetica",      fontSize=13,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4)
    add("CoverSmall",   fontName="Helvetica",      fontSize=10,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=3)
    add("CoverLink",    fontName="Helvetica-Bold", fontSize=10,
        textColor=SLIDE_ACC, alignment=TA_CENTER, spaceAfter=4)

    add("SecHeader",    fontName="Helvetica-Bold", fontSize=14,
        textColor=BLUE,   spaceBefore=14, spaceAfter=4,
        borderPad=2)
    add("SubHeader",    fontName="Helvetica-Bold", fontSize=11,
        textColor=BLUE_LIGHT, spaceBefore=8, spaceAfter=3)
    add("Body",         fontName="Helvetica",      fontSize=9.5,
        textColor=BLACK,  alignment=TA_JUSTIFY, leading=14, spaceAfter=5)
    add("BulletBody",   fontName="Helvetica",      fontSize=9.5,
        textColor=BLACK,  leftIndent=14, bulletIndent=4,
        leading=13, spaceAfter=3)
    add("Caption",      fontName="Helvetica-Oblique", fontSize=8,
        textColor=GRAY,   alignment=TA_CENTER, spaceAfter=6)
    add("CodeBlock",    fontName="Courier",        fontSize=8.5,
        textColor=colors.HexColor("#1a1a6e"), backColor=GRAY_LITE,
        leading=12, spaceAfter=4, leftIndent=8)

    # slide styles
    add("SlideTitle",   fontName="Helvetica-Bold", fontSize=18,
        textColor=WHITE,  alignment=TA_CENTER, spaceAfter=6)
    add("SlideSubTitle",fontName="Helvetica-Bold", fontSize=12,
        textColor=SLIDE_ACC, alignment=TA_CENTER, spaceAfter=4)
    add("SlideBullet",  fontName="Helvetica",      fontSize=10,
        textColor=WHITE,  leftIndent=16, bulletIndent=4,
        leading=15, spaceAfter=4)
    add("SlideBody",    fontName="Helvetica",      fontSize=10,
        textColor=WHITE,  alignment=TA_CENTER, leading=14, spaceAfter=4)
    add("SlideNote",    fontName="Helvetica-Oblique", fontSize=8.5,
        textColor=SLIDE_ACC, alignment=TA_CENTER, spaceAfter=2)

    return s

# ── helpers ───────────────────────────────────────────────────────────────────
def section(title, s):
    return [
        HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=2),
        Paragraph(title, s["SecHeader"]),
    ]

def sub(title, s):
    return Paragraph(title, s["SubHeader"])

def body(text, s):
    return Paragraph(text, s["Body"])

def bullet(text, s):
    return Paragraph(f"• &nbsp; {text}", s["BulletBody"])

def code(text, s):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), s["Code"])

def tbl(data, col_widths, header_bg=BLUE, row_bg=ACCENT):
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  header_bg),
        ("TEXTCOLOR",   (0,0), (-1,0),  WHITE),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0),  8.5),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, ACCENT]),
        ("FONTNAME",    (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1), (-1,-1), 8),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("ROWHEIGHT",   (0,0), (-1,-1), 14),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ])
    t.setStyle(style)
    return t

# ── speedup data ──────────────────────────────────────────────────────────────
def load_speedup():
    path = os.path.join(BASE, "speedup_table.csv")
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

# ── COVER PAGE ────────────────────────────────────────────────────────────────
def cover_page(s):
    W, H = A4
    elems = []

    # blue banner
    banner = Table([[""]], colWidths=[W - 4*cm], rowHeights=[3.5*cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), BLUE),
        ("ROUNDEDCORNERS", [6,6,6,6]),
    ]))

    # cover table (full-width blue box)
    cover_data = [[
        Paragraph("CENG 479 — Parallel Computing", s["CoverSub"]),
    ],[
        Paragraph("Parallel Image Processing Engine", s["CoverTitle"]),
    ],[
        Paragraph("Final Implementation Report &amp; Presentation", s["CoverSub"]),
    ],[
        Paragraph("Gazi University · Department of Computer Engineering · Spring 2026", s["CoverSmall"]),
    ],[
        Spacer(1, 0.3*cm),
    ],[
        Paragraph("GitHub Repository (Public):", s["CoverSmall"]),
    ],[
        Paragraph(f'<a href="{GITHUB}" color="#f0c040"><u>{GITHUB}</u></a>', s["CoverLink"]),
    ],[
        Spacer(1, 0.4*cm),
    ],[
        Paragraph("Team Members", s["CoverSub"]),
    ],[
        Paragraph("Muhammed Çakırgöz  ·  Musa Bilal Yaz", s["CoverSmall"]),
    ],[
        Spacer(1, 0.3*cm),
    ],[
        Paragraph("Submission 2 · June 2026", s["CoverSmall"]),
    ]]

    ct = Table(cover_data, colWidths=[W - 4*cm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,-1), BLUE),
        ("ALIGN",       (0,0), (0,-1), "CENTER"),
        ("VALIGN",      (0,0), (0,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0), (0,-1), 4),
        ("BOTTOMPADDING",(0,0),(0,-1), 4),
        ("LEFTPADDING", (0,0), (0,-1), 20),
        ("RIGHTPADDING",(0,0), (0,-1), 20),
        ("ROUNDEDCORNERS", [8,8,8,8]),
    ]))

    elems.append(Spacer(1, 2*cm))
    elems.append(ct)
    elems.append(Spacer(1, 1*cm))

    # tech stack badges
    badge_data = [["Java 17", "Maven 3.6+", "JMH", "ExecutorService", "ForkJoinPool"]]
    bt = Table(badge_data, colWidths=[2.6*cm]*5)
    bt.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), BLUE_LIGHT),
        ("TEXTCOLOR",   (0,0),(-1,0), WHITE),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,0), 8),
        ("ALIGN",       (0,0),(-1,0), "CENTER"),
        ("ROUNDEDCORNERS", [4,4,4,4]),
        ("TOPPADDING",  (0,0),(-1,0), 5),
        ("BOTTOMPADDING",(0,0),(-1,0), 5),
        ("LEFTPADDING", (0,0),(-1,0), 4),
        ("RIGHTPADDING",(0,0),(-1,0), 4),
    ]))
    elems.append(bt)
    elems.append(PageBreak())
    return elems

# ── REPORT SECTIONS ───────────────────────────────────────────────────────────
def report_section(s, rows):
    e = []

    # ── 1. Introduction ──────────────────────────────────────────────────────
    e += section("1. Introduction", s)
    e.append(body(
        "High-resolution image processing is a computationally demanding task. When executed "
        "sequentially, kernel-based convolution filters create significant performance bottlenecks "
        "especially for large images (e.g. 4K). Because each output pixel depends only on a fixed "
        "neighbourhood of the <i>input</i> image, the problem is embarrassingly parallel: the image "
        "can be divided across threads with zero data dependencies during the compute phase.", s))
    e.append(body(
        "This report presents a parallel image-processing engine implemented in <b>Java</b> using "
        "two distinct concurrency strategies: <b>ExecutorService</b> with horizontal strip "
        "decomposition, and <b>ForkJoinPool</b> with divide-and-conquer work-stealing. Three "
        "convolution filters — Grayscale, Gaussian Blur 5×5, and Sobel 3×3 — were benchmarked with "
        "<b>JMH</b> (Java Microbenchmark Harness) to produce reproducible speedup measurements "
        "across image sizes of 512×512, 1024×1024, and 2048×2048.", s))
    e.append(body(
        f'The complete source code is publicly available on GitHub: '
        f'<a href="{GITHUB}" color="#2e6db4"><u>{GITHUB}</u></a>', s))

    # ── 2. Sequential Baseline ───────────────────────────────────────────────
    e += section("2. Sequential Baseline Implementation", s)
    e.append(body(
        "<b>SequentialProcessor</b> iterates over every pixel row-by-row and applies the given "
        "filter. The <b>Filter</b> interface defines a single <i>apply(pixels[], width, height, x, y)</i> "
        "method, making filter implementations interchangeable. Edge handling uses <b>clamped "
        "coordinates</b>, ensuring identical boundary behaviour across all implementations.", s))

    filter_data = [
        ["Filter", "Type", "Kernel", "Cost per pixel"],
        ["GrayscaleFilter",     "Point-wise",   "None (r=0)", "Low — 3 reads, 1 write"],
        ["GaussianBlurFilter",  "Convolution",  "5×5",        "High — 25 weighted taps"],
        ["SobelFilter",         "Gradient",     "3×3 (Gx+Gy)","Medium — 18 taps + √"],
    ]
    e.append(tbl(filter_data, [4.5*cm, 2.8*cm, 2.8*cm, 5.4*cm]))
    e.append(Spacer(1, 0.2*cm))

    # ── 3. Parallel Implementation ───────────────────────────────────────────
    e += section("3. Parallel Implementation", s)
    e.append(sub("3.1  ExecutorService — Horizontal Strip Decomposition", s))
    e.append(body(
        "<b>ExecutorParallelProcessor</b> partitions the image into <i>N</i> equal horizontal strips "
        "(one per thread). Each <b>Callable</b> task processes a contiguous band of rows and writes "
        "results into a pre-allocated output array at its assigned offset. Because strips are "
        "disjoint and the source array is read-only, <b>no locking is required</b> during computation. "
        "The thread pool is created once and reused via try-with-resources.", s))

    e.append(sub("3.2  ForkJoinPool — Divide-and-Conquer", s))
    e.append(body(
        "<b>ForkJoinParallelProcessor</b> uses a <b>RecursiveAction</b> that halves the row range "
        "until it falls below a threshold (64 rows), then processes the sub-range directly. "
        "The work-stealing scheduler dynamically rebalances load — particularly beneficial for "
        "larger images where strip-count imbalance would arise in static decomposition.", s))

    e.append(sub("3.3  Correctness Verification", s))
    e.append(body(
        "All parallel implementations are verified against the sequential baseline using "
        "<b>CorrectnessVerifier.firstDifference()</b>, which performs a pixel-for-pixel comparison. "
        "All six combinations (3 filters × 2 parallel strategies) produce <b>bit-identical</b> "
        "output on a 2048×2048 synthetic image:", s))
    cv_data = [
        ["Filter", "Executor (12 threads)", "ForkJoin (12 threads)"],
        ["Grayscale",       "✓ PASS", "✓ PASS"],
        ["GaussianBlur5x5", "✓ PASS", "✓ PASS"],
        ["Sobel3x3",        "✓ PASS", "✓ PASS"],
    ]
    e.append(tbl(cv_data, [5.5*cm, 5.5*cm, 5.5*cm], header_bg=GREEN))
    e.append(Spacer(1, 0.2*cm))

    # ── 4. Performance Comparison ────────────────────────────────────────────
    e += section("4. Performance Comparison", s)
    e.append(body(
        "Benchmarks were run with <b>JMH</b> (10 warm-up + 10 measurement iterations, "
        "AverageTime mode, ms/op) on a machine with 12 logical cores. The speedup formula is: "
        "<b>Speedup = T_sequential / T_parallel</b>.", s))

    e.append(sub("4.1  GaussianBlur 5×5 Speedup", s))
    gb_data = [["Size", "Threads", "Seq (ms)", "Executor (ms)", "ForkJoin (ms)", "Exec ×", "FJ ×"]]
    for r in rows:
        if r["filter"] == "GaussianBlur5x5":
            gb_data.append([f'{r["size"]}²', r["threads"],
                r["sequential_ms"], r["executor_ms"], r["forkjoin_ms"],
                r["executor_speedup"]+"×", r["forkjoin_speedup"]+"×"])
    e.append(tbl(gb_data, [1.8*cm,1.6*cm,2.2*cm,2.5*cm,2.5*cm,1.9*cm,1.9*cm]))

    e.append(Spacer(1, 0.15*cm))
    e.append(sub("4.2  Sobel 3×3 Speedup", s))
    sob_data = [["Size", "Threads", "Seq (ms)", "Executor (ms)", "ForkJoin (ms)", "Exec ×", "FJ ×"]]
    for r in rows:
        if r["filter"] == "Sobel3x3":
            sob_data.append([f'{r["size"]}²', r["threads"],
                r["sequential_ms"], r["executor_ms"], r["forkjoin_ms"],
                r["executor_speedup"]+"×", r["forkjoin_speedup"]+"×"])
    e.append(tbl(sob_data, [1.8*cm,1.6*cm,2.2*cm,2.5*cm,2.5*cm,1.9*cm,1.9*cm]))

    e.append(Spacer(1, 0.15*cm))
    e.append(sub("4.3  Grayscale Speedup", s))
    gs_data = [["Size", "Threads", "Seq (ms)", "Executor (ms)", "ForkJoin (ms)", "Exec ×", "FJ ×"]]
    for r in rows:
        if r["filter"] == "Grayscale":
            gs_data.append([f'{r["size"]}²', r["threads"],
                r["sequential_ms"], r["executor_ms"], r["forkjoin_ms"],
                r["executor_speedup"]+"×", r["forkjoin_speedup"]+"×"])
    e.append(tbl(gs_data, [1.8*cm,1.6*cm,2.2*cm,2.5*cm,2.5*cm,1.9*cm,1.9*cm]))

    e.append(Spacer(1, 0.3*cm))
    e.append(sub("4.4  Speedup Charts", s))

    # charts side by side
    chart_row = [[
        img("speedup_GaussianBlur5x5.png", 8.5*cm),
        img("speedup_Sobel3x3.png", 8.5*cm),
    ]]
    ct = Table(chart_row, colWidths=[8.8*cm, 8.8*cm])
    ct.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    e.append(ct)
    e.append(Paragraph("Figure 1 — Left: GaussianBlur5x5  |  Right: Sobel3x3  (Executor vs ForkJoin)", s["Caption"]))

    chart_row2 = [[
        img("speedup_Grayscale.png", 8.5*cm),
        img("speedup_combined.png", 8.5*cm),
    ]]
    ct2 = Table(chart_row2, colWidths=[8.8*cm, 8.8*cm])
    ct2.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    e.append(ct2)
    e.append(Paragraph("Figure 2 — Left: Grayscale  |  Right: All Filters Combined (2048×2048, Executor)", s["Caption"]))

    e.append(sub("4.5  Analysis", s))
    e.append(body(
        "<b>Compute-bound filters (Gaussian Blur, Sobel)</b> scale well, reaching 4.3×–5.1× at "
        "8 threads. ForkJoinPool outperforms ExecutorService on larger images due to dynamic "
        "work-stealing load balancing.", s))
    e.append(body(
        "<b>Memory-bound filter (Grayscale)</b> plateaus at ~1.5× regardless of thread count. "
        "The trivial single-channel lookup saturates memory bandwidth before CPU utilisation "
        "can be maximised. This is consistent with the <b>Roofline Model</b>: operations with "
        "low arithmetic intensity are bounded by memory bandwidth, not compute throughput.", s))
    e.append(body(
        "<b>Amdahl's Law</b> interpretation: the empirical ceiling for Gaussian Blur aligns with "
        "a ~95% parallel fraction, where sequential overhead is limited to array allocation and "
        "thread setup.", s))

    # ── 5. Academic Background ───────────────────────────────────────────────
    e += section("5. Academic Background", s)
    e.append(body(
        "The parallelization strategy in this project aligns with established literature. "
        "<b>Seinstra et al. (2002)</b> demonstrated that convolution-based image filters exhibit "
        "near-linear speedup when workload partitioning minimises inter-thread communication — "
        "consistent with our strip-decomposition results for compute-intensive kernels.", s))
    e.append(body(
        "<b>Amdahl (1967)</b> provides the theoretical speedup ceiling <i>S = 1 / (1−p)</i>. "
        "For Gaussian Blur our empirical data suggests p ≈ 0.95, yielding a theoretical maximum "
        "of 20×; the observed 4–5× at 8 threads is expected given practical overhead.", s))
    e.append(body(
        "<b>Williams et al. (2009)</b> — the Roofline Model — explains the divergent scalability "
        "of Grayscale vs. Gaussian Blur via arithmetic intensity: memory-bound kernels saturate "
        "bandwidth before compute capacity is reached. <b>Lea (2000)</b> provides the theoretical "
        "foundation for ForkJoinPool's work-stealing scheduler, which explains its advantage over "
        "static decomposition for uneven workloads.", s))

    # ── 6. Challenges & Solutions ────────────────────────────────────────────
    e += section("6. Challenges and Solutions", s)
    challenges = [
        ("JVM JIT Warm-up & GC Noise",
         "Initial System.nanoTime() measurements were skewed by JIT compilation and garbage "
         "collection. <b>Solution:</b> Adopted JMH with dedicated warm-up iterations and "
         "fork-per-configuration to eliminate noise and produce statistically reliable results."),
        ("Pixel-Identical Correctness Across Implementations",
         "Strip boundaries required careful handling to ensure parallel results were bit-identical "
         "to the sequential baseline. <b>Solution:</b> Implemented CorrectnessVerifier with "
         "pixel-for-pixel comparison; clamped-coordinate edge handling ensures identical "
         "border pixel treatment across all strategies."),
        ("Varying Scalability Between Filters",
         "Grayscale achieved only ~1.5× speedup despite 8 threads, while Gaussian Blur reached "
         "4.3×. <b>Solution:</b> Profiling identified memory bandwidth saturation (Roofline Model) "
         "as the root cause for Grayscale — confirmed that the algorithm is memory-bound, not "
         "thread-limited. This insight informed our Amdahl analysis in the report."),
        ("ForkJoin Recursive Overhead on Small Images",
         "For 512×512 images, ForkJoinPool's divide-and-conquer recursion overhead slightly "
         "exceeded ExecutorService. <b>Solution:</b> Tuned SEQUENTIAL_THRESHOLD to 64 rows, "
         "preventing excessive task granularity at small image sizes."),
    ]
    for title, desc in challenges:
        e.append(KeepTogether([
            bullet(f"<b>{title}:</b> {desc}", s),
        ]))

    # ── 7. Conclusion & Future Work ──────────────────────────────────────────
    e += section("7. Conclusion and Future Improvements", s)
    e.append(body(
        "This project successfully demonstrated the efficacy of parallelizing image processing "
        "algorithms using Java's concurrency frameworks. Empirical JMH benchmarking confirmed "
        "significant speedups for compute-bound operations: Gaussian Blur achieved ~4.3× "
        "(Executor) and ~4.81× (ForkJoin) at 8 threads on 2048×2048 images; Sobel reached "
        "~4.49× and ~5.10× respectively. The Grayscale filter was confirmed as memory-bound, "
        "limited to ~1.55× regardless of thread count. ForkJoinPool's work-stealing advantage "
        "over static strip decomposition became more pronounced at larger image sizes.", s))
    future = [
        "GPU/CUDA acceleration — exploit thousands of CUDA cores for pixel-independent kernels",
        "SIMD vectorisation — leverage AVX2/AVX-512 for intra-core throughput gains",
        "4K and 8K image benchmarks — evaluate boundary overhead at ultra-high resolution",
        "Adaptive thread pool — dynamically tune thread count based on image size and hardware",
        "Memory-bound filter optimisation — cache-blocking and prefetching for Grayscale",
    ]
    for f in future:
        e.append(bullet(f, s))

    # ── 8. References ─────────────────────────────────────────────────────────
    e += section("8. References", s)
    refs = [
        "Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale "
        "computing capabilities. <i>Proceedings of the Spring Joint Computer Conference</i>, 483–485. "
        "https://doi.org/10.1145/1465482.1465560",
        "Seinstra, F. J., Koelma, D., &amp; Bagdanov, A. D. (2002). Finite state machine-based "
        "optimization of data parallel regular domain problems applied to low-level image processing. "
        "<i>IEEE Transactions on Parallel and Distributed Systems</i>, 15(10), 865–877. "
        "https://doi.org/10.1109/TPDS.2004.45",
        "Williams, S., Waterman, A., &amp; Patterson, D. (2009). Roofline: An insightful visual "
        "performance model for multicore architectures. <i>Communications of the ACM</i>, 52(4), "
        "65–76. https://doi.org/10.1145/1498765.1498785",
        "Lea, D. (2000). A Java fork/join framework. <i>Proceedings of the ACM 2000 Conference on "
        "Java Grande</i>, 36–43. https://doi.org/10.1145/337449.337465",
    ]
    for i, r in enumerate(refs, 1):
        e.append(body(f"[{i}] {r}", s))

    return e

# ── SLIDE BUILDER ─────────────────────────────────────────────────────────────
def slide_box(content_rows, title, s, title_col=BLUE, accent=SLIDE_ACC):
    """Build a single slide as a coloured Table."""
    W, _ = A4
    inner_w = W - 4*cm

    rows = [[Paragraph(title, s["SlideTitle"])]]
    rows += [[c] for c in content_rows]

    t = Table(rows, colWidths=[inner_w])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0),  title_col),
        ("BACKGROUND",   (0,1),(0,-1), BLUE),
        ("ALIGN",        (0,0),(0,-1), "LEFT"),
        ("VALIGN",       (0,0),(0,-1), "TOP"),
        ("TOPPADDING",   (0,0),(0,-1), 8),
        ("BOTTOMPADDING",(0,0),(0,-1), 6),
        ("LEFTPADDING",  (0,0),(0,-1), 16),
        ("RIGHTPADDING", (0,0),(0,-1), 16),
        ("ROUNDEDCORNERS",[6,6,6,6]),
    ]))
    return t

def presentation_section(s, rows):
    e = []
    W, _ = A4
    inner_w = W - 4*cm

    def sl(title, content_rows):
        return slide_box(content_rows, title, s)

    def sb(text): return Paragraph(f"▶  {text}", s["SlideBullet"])
    def sn(text): return Paragraph(text, s["SlideNote"])
    def ss(h=0.2): return Spacer(1, h*cm)

    e.append(Paragraph("PRESENTATION SLIDES", s["SecHeader"]))
    e.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=6))

    # Slide 1 — Title
    e.append(sl("Slide 1 — Title", [
        ss(),
        Paragraph("Parallel Image Processing Engine", s["SlideSubTitle"]),
        ss(0.1),
        Paragraph("CENG 479 — Parallel Computing · Gazi University · Spring 2026", s["SlideBody"]),
        ss(0.1),
        Paragraph("Muhammed Çakırgöz  ·  Musa Bilal Yaz", s["SlideBody"]),
        ss(0.2),
        Paragraph(f'GitHub: <a href="{GITHUB}" color="#f0c040"><u>{GITHUB}</u></a>', s["SlideNote"]),
        ss(),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 2 — Problem & Motivation
    e.append(sl("Slide 2 — Problem &amp; Motivation", [
        ss(0.1),
        sb("High-res image filtering (4K+) is slow on a single thread"),
        sb("Kernel convolution = O(W × H × K²) per filter"),
        sb("Each output pixel is independent of others → embarrassingly parallel"),
        sb("Goal: multi-threaded speedup with zero correctness compromise"),
        ss(0.1),
        sn("Amdahl's Law: theoretical max speedup = 1 / (1 − p),  p ≈ 0.95 for Gaussian Blur"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 3 — Architecture Overview
    e.append(sl("Slide 3 — Architecture Overview", [
        ss(0.1),
        sb("3 Filters: Grayscale (point-wise), Gaussian Blur 5×5, Sobel 3×3"),
        sb("SequentialProcessor — single-thread row-by-row baseline"),
        sb("ExecutorParallelProcessor — fixed thread pool + horizontal strip decomposition"),
        sb("ForkJoinParallelProcessor — RecursiveAction + work-stealing divide-and-conquer"),
        sb("CorrectnessVerifier — pixel-for-pixel comparison against baseline"),
        sb("JMH Benchmark — reproducible timing, eliminates JIT warm-up noise"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 4 — ExecutorService Design
    e.append(sl("Slide 4 — ExecutorService Design", [
        ss(0.1),
        sb("Image split into N equal horizontal strips (N = thread count)"),
        sb("Each Callable processes rows [start, end) → writes to pre-allocated output[]"),
        sb("Source array is READ-ONLY during compute → zero locking overhead"),
        sb("Thread pool reused across filter calls (try-with-resources)"),
        ss(0.1),
        sn("Strip[i] covers rows:  i×(H/N)  to  (i+1)×(H/N)"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 5 — ForkJoinPool Design
    e.append(sl("Slide 5 — ForkJoinPool Design", [
        ss(0.1),
        sb("RecursiveAction splits row range in half recursively"),
        sb("Base case: range ≤ 64 rows → process directly (sequential threshold)"),
        sb("Work-stealing: idle threads steal tasks from busy threads' queues"),
        sb("Better dynamic load balance than static strips for large images"),
        sb("ForkJoin outperforms Executor on 2048×2048 (Gaussian: 4.81× vs 4.30×)"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 6 — Correctness Results
    e.append(sl("Slide 6 — Correctness Verification", [
        ss(0.1),
        sb("CorrectnessVerifier.firstDifference() → pixel-by-pixel scan"),
        sb("Tested on 2048×2048 synthetic image, all 6 combinations"),
        ss(0.1),
        Paragraph("All results: ✓ PASS — bit-identical to sequential baseline", s["SlideBody"]),
        ss(0.1),
        sn("Grayscale Executor/ForkJoin · GaussianBlur5x5 Executor/ForkJoin · Sobel3x3 Executor/ForkJoin"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 7 — Performance Results
    e.append(sl("Slide 7 — Performance Results (8 threads, 2048×2048)", [
        ss(0.1),
        sb("Gaussian Blur:  Executor 4.30×  |  ForkJoin 4.81×"),
        sb("Sobel 3×3:      Executor 4.49×  |  ForkJoin 5.10×"),
        sb("Grayscale:      Executor 1.55×  |  ForkJoin 1.54×  ← memory-bound"),
        ss(0.1),
        sn("JMH benchmark · 10 warm-up + 10 measurement iterations · AverageTime (ms/op)"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 8 — Charts
    e.append(sl("Slide 8 — Speedup Charts", [ss(0.15)]))
    chart_row = [[
        img("speedup_GaussianBlur5x5.png", 8.2*cm),
        img("speedup_combined.png",        8.2*cm),
    ]]
    ct = Table(chart_row, colWidths=[8.4*cm, 8.4*cm])
    ct.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
    e.append(ct)
    e.append(Paragraph(
        "Left: GaussianBlur5x5 — Executor vs ForkJoin  |  Right: All filters combined (Executor, 2048×2048)",
        s["Caption"]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 9 — Challenges & Key Findings
    e.append(sl("Slide 9 — Challenges &amp; Key Findings", [
        ss(0.1),
        sb("JIT warm-up → solved with JMH (fork-per-config, warm-up iters)"),
        sb("Bit-identical correctness → clamped edges + CorrectnessVerifier"),
        sb("Grayscale bottleneck → memory bandwidth saturated (Roofline Model)"),
        sb("ForkJoin recursive overhead on small images → tuned threshold (64 rows)"),
        ss(0.1),
        sn("Key insight: parallel speedup is filter-dependent — arithmetic intensity determines scalability"),
        ss(0.1),
    ]))
    e.append(Spacer(1, 0.4*cm))

    # Slide 10 — Conclusion & Future Work
    e.append(sl("Slide 10 — Conclusion &amp; Future Work", [
        ss(0.1),
        sb("Successfully parallelised 3 convolution filters with 2 Java strategies"),
        sb("Up to 5.10× speedup (Sobel, ForkJoin, 8 threads, 2048×2048)"),
        sb("Memory-bound filters (Grayscale) need different optimisation strategy"),
        ss(0.1),
        Paragraph("Future Work:", s["SlideSubTitle"]),
        sb("GPU/CUDA — exploit thousands of concurrent cores"),
        sb("SIMD vectorisation (AVX2/AVX-512) for intra-core throughput"),
        sb("Adaptive thread pool — dynamic tuning per image size"),
        ss(0.1),
    ]))

    return e

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    out = os.path.join(BASE, "CENG479_Sub2_Final_Report.pdf")
    doc = SimpleDocTemplate(
        out,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="CENG 479 Parallel Image Processing — Final Report",
        author="Muhammed Çakırgöz, Musa Bilal Yaz",
    )

    s = make_styles()
    rows = load_speedup()
    story = []
    story += cover_page(s)
    story += report_section(s, rows)
    story.append(PageBreak())
    story += presentation_section(s, rows)

    doc.build(story)
    print(f"PDF written: {out}")

if __name__ == "__main__":
    main()
