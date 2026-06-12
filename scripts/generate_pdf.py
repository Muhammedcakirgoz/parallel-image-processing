"""
generate_pdf.py  -  CENG 479 Sub2 Final Report + Presentation (single PDF)
Usage: python scripts/generate_pdf.py
Output: CENG479_Sub2_Final_Report.pdf
"""

import csv, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether, BaseDocTemplate,
    Frame, PageTemplate
)
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus.flowables import Flowable

PAGE_W, PAGE_H = A4

BLUE       = colors.HexColor("#1a3a6b")
BLUE_MID   = colors.HexColor("#2e6db4")
BLUE_LIGHT = colors.HexColor("#d6e4f7")
GOLD       = colors.HexColor("#f0c040")
GRAY_D     = colors.HexColor("#444444")
GRAY_L     = colors.HexColor("#f5f5f5")
GREEN_D    = colors.HexColor("#1a6b3a")
WHITE      = colors.white
BLACK      = colors.black
ACCENT_ROW = colors.HexColor("#eaf1fb")

GITHUB = "https://github.com/Muhammedcakirgoz/parallel-image-processing"
BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def imgf(name, width, max_height=None):
    path = os.path.join(BASE, name)
    if not os.path.exists(path):
        return Spacer(1, 0.5*cm)
    im = Image(path)
    ratio = im.imageHeight / im.imageWidth
    h = width * ratio
    if max_height and h > max_height:
        h = max_height
        width = h / ratio
    im.drawWidth  = width
    im.drawHeight = h
    return im


def load_speedup():
    path = os.path.join(BASE, "speedup_table.csv")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def make_styles():
    base = getSampleStyleSheet()
    existing = set(base.byName.keys())

    def add(name, **kw):
        if name not in existing:
            base.add(ParagraphStyle(name=name, **kw))

    # report body
    add("RTitle",   fontName="Helvetica-Bold", fontSize=16, textColor=BLUE,
        alignment=TA_CENTER, spaceAfter=4, spaceBefore=2)
    add("RSec",     fontName="Helvetica-Bold", fontSize=12, textColor=BLUE,
        spaceBefore=12, spaceAfter=3)
    add("RSubSec",  fontName="Helvetica-Bold", fontSize=10, textColor=BLUE_MID,
        spaceBefore=6, spaceAfter=2)
    add("RBody",    fontName="Helvetica",      fontSize=9,  textColor=BLACK,
        alignment=TA_JUSTIFY, leading=13.5, spaceAfter=4)
    add("RBullet",  fontName="Helvetica",      fontSize=9,  textColor=BLACK,
        leftIndent=12, bulletIndent=2, leading=13, spaceAfter=2)
    add("RCaption", fontName="Helvetica-Oblique", fontSize=8, textColor=GRAY_D,
        alignment=TA_CENTER, spaceAfter=6, spaceBefore=2)
    add("RSmall",   fontName="Helvetica",      fontSize=8,  textColor=GRAY_D,
        spaceAfter=2)

    # slide styles
    add("STitle",   fontName="Helvetica-Bold", fontSize=15, textColor=WHITE,
        alignment=TA_CENTER, spaceAfter=6, spaceBefore=2)
    add("SHead",    fontName="Helvetica-Bold", fontSize=11, textColor=GOLD,
        alignment=TA_LEFT,   spaceAfter=4, spaceBefore=2)
    add("SBullet",  fontName="Helvetica",      fontSize=9.5,textColor=WHITE,
        leftIndent=14, bulletIndent=2, leading=14, spaceAfter=3)
    add("SNote",    fontName="Helvetica-Oblique", fontSize=8, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=2)
    add("SBody",    fontName="Helvetica",      fontSize=9,  textColor=WHITE,
        alignment=TA_CENTER, leading=13, spaceAfter=3)

    return base


# ---------------------------------------------------------------------------
# Cover page drawn with canvas (full control)
# ---------------------------------------------------------------------------
class CoverPage(Flowable):
    def __init__(self):
        Flowable.__init__(self)
        self.width  = PAGE_W - 4*cm
        self.height = PAGE_H - 4*cm

    def draw(self):
        c = self.canv
        W = self.width
        H = self.height

        # full blue background
        c.setFillColor(BLUE)
        c.roundRect(0, 0, W, H, 10, fill=1, stroke=0)

        # gold top bar
        c.setFillColor(GOLD)
        c.roundRect(0, H - 1.8*cm, W, 1.8*cm, 10, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(0, H - 1.8*cm, W, 0.9*cm, fill=1, stroke=0)

        # top bar text
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(W/2, H - 1.25*cm, "CENG 479 -- Parallel Computing  |  Gazi University  |  Spring 2026")

        # main title
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(W/2, H - 3.8*cm, "Parallel Image Processing Engine")

        c.setFont("Helvetica", 13)
        c.setFillColor(GOLD)
        c.drawCentredString(W/2, H - 4.8*cm, "Final Implementation Report & Presentation")

        # divider
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.5)
        c.line(1.5*cm, H - 5.4*cm, W - 1.5*cm, H - 5.4*cm)

        # tech badges
        badges = ["Java 17", "Maven 3.6+", "JMH", "ExecutorService", "ForkJoinPool"]
        bw, bh, gap = 3.2*cm, 0.55*cm, 0.25*cm
        total = len(badges)*bw + (len(badges)-1)*gap
        bx = (W - total) / 2
        by = H - 6.6*cm
        c.setFont("Helvetica-Bold", 8)
        for b in badges:
            c.setFillColor(BLUE_MID)
            c.roundRect(bx, by, bw, bh, 4, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.drawCentredString(bx + bw/2, by + 0.15*cm, b)
            bx += bw + gap

        # filters section
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(W/2, H - 7.8*cm, "Filters Implemented")
        filters = [
            ("Grayscale",        "Point-wise  --  Low compute"),
            ("Gaussian Blur 5x5","Convolution  --  High compute (25 taps/pixel)"),
            ("Sobel 3x3",        "Gradient  --  Edge detection"),
        ]
        fy = H - 8.6*cm
        c.setFont("Helvetica", 9)
        for fname, fdesc in filters:
            c.setFillColor(GOLD)
            c.circle(1.6*cm, fy + 0.1*cm, 0.07*cm, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1.9*cm, fy, fname)
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor("#aaccee"))
            c.drawString(1.9*cm + 3.8*cm, fy, fdesc)
            fy -= 0.65*cm

        # team section
        c.setFillColor(colors.HexColor("#0d2244"))
        c.roundRect(1.2*cm, H - 13.2*cm, W - 2.4*cm, 2.8*cm, 6, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(W/2, H - 11.2*cm, "Team Members")
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(W/2, H - 12.0*cm, "Muhammed Cakiagoz   .   Musa Bilal Yaz")
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#aaccee"))
        c.drawCentredString(W/2, H - 12.6*cm, "Gazi University  --  Computer Engineering  --  Submission 2")

        # github box
        c.setFillColor(colors.HexColor("#0d2244"))
        c.roundRect(1.2*cm, H - 16.2*cm, W - 2.4*cm, 2.4*cm, 6, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(W/2, H - 14.6*cm, "GitHub Repository (Public)")
        c.setFillColor(WHITE)
        c.setFont("Helvetica", 9)
        c.drawCentredString(W/2, H - 15.3*cm, GITHUB)
        c.setFillColor(colors.HexColor("#aaccee"))
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(W/2, H - 15.9*cm, "Source code, benchmarks, and all report assets are available at the link above")

        # bottom bar
        c.setFillColor(GOLD)
        c.roundRect(0, 0, W, 1.2*cm, 10, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(0, 1.2*cm - 0.6*cm, W, 0.6*cm, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(W/2, 0.35*cm, "June 2026  --  CENG 479 Parallel Computing")


# ---------------------------------------------------------------------------
# Divider / Section header flowable
# ---------------------------------------------------------------------------
def sec_header(title, s):
    return [
        Spacer(1, 0.3*cm),
        HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=3),
        Paragraph(title, s["RSec"]),
    ]

def subsec(title, s):
    return Paragraph(title, s["RSubSec"])

def body(text, s):
    return Paragraph(text, s["RBody"])

def bul(text, s):
    return Paragraph(f"&bull; &nbsp;{text}", s["RBullet"])


# ---------------------------------------------------------------------------
# Table helper
# ---------------------------------------------------------------------------
def make_table(data, col_widths, hdr_color=BLUE):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  hdr_color),
        ("TEXTCOLOR",     (0,0),(-1,0),  WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8.5),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, ACCENT_ROW]),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.35, colors.HexColor("#bbbbbb")),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
    ]))
    return t


# ---------------------------------------------------------------------------
# Report content
# ---------------------------------------------------------------------------
def report_content(s, rows):
    e = []

    # page title
    e.append(Spacer(1, 0.2*cm))
    e.append(Paragraph("CENG 479 — Parallel Image Processing Engine", s["RTitle"]))
    e.append(Paragraph("Implementation Report  |  Submission 2", s["RCaption"]))
    e.append(HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT, spaceAfter=4))

    # 1. Introduction
    e += sec_header("1. Introduction", s)
    e.append(body(
        "High-resolution image processing is computationally demanding. Sequential execution of "
        "kernel-based convolution filters creates significant bottlenecks at large image sizes (4K+). "
        "Because each output pixel depends solely on a fixed neighbourhood of the <i>input</i> image, "
        "the problem is <b>embarrassingly parallel</b>: the image can be divided across threads with "
        "zero inter-thread data dependencies during the compute phase.", s))
    e.append(body(
        "This report presents a parallel engine built in <b>Java</b> using two concurrency strategies: "
        "<b>ExecutorService</b> with horizontal strip decomposition and <b>ForkJoinPool</b> with "
        "divide-and-conquer work-stealing. Three filters — Grayscale, Gaussian Blur 5x5, Sobel 3x3 — "
        "were benchmarked with <b>JMH</b> across image sizes 512x512, 1024x1024, 2048x2048.", s))
    e.append(body(
        f'Source code (public): <font color="#2e6db4"><u>{GITHUB}</u></font>', s))

    # 2. Sequential Baseline
    e += sec_header("2. Sequential Baseline Implementation", s)
    e.append(body(
        "<b>SequentialProcessor</b> iterates row-by-row applying the given filter. "
        "The <b>Filter</b> interface exposes a single <i>apply(pixels[], width, height, x, y)</i> "
        "method. Edge handling uses <b>clamped coordinates</b>, ensuring identical boundary "
        "behaviour across all implementations.", s))
    fd = [
        ["Filter",           "Type",         "Kernel",    "Cost per pixel"],
        ["GrayscaleFilter",  "Point-wise",   "None (r=0)","Low — 3 reads, 1 write"],
        ["GaussianBlurFilter","Convolution",  "5x5",       "High — 25 weighted taps"],
        ["SobelFilter",      "Gradient",     "3x3 Gx+Gy", "Medium — 18 taps + sqrt"],
    ]
    e.append(make_table(fd, [4.2*cm, 2.8*cm, 2.6*cm, 5.9*cm]))

    # 3. Parallel Implementation
    e += sec_header("3. Parallel Implementation", s)
    e.append(subsec("3.1  ExecutorService — Horizontal Strip Decomposition", s))
    e.append(body(
        "<b>ExecutorParallelProcessor</b> divides the image into N equal horizontal strips "
        "(one per thread). Each <b>Callable</b> task processes rows [start, end) and writes "
        "into a pre-allocated output array at its assigned offset. Strips are disjoint and "
        "the source array is read-only, so <b>no locking is required</b>. "
        "The thread pool is created once and reused via try-with-resources.", s))
    e.append(subsec("3.2  ForkJoinPool — Divide-and-Conquer", s))
    e.append(body(
        "<b>ForkJoinParallelProcessor</b> uses a <b>RecursiveAction</b> that halves the row "
        "range until it falls below 64 rows (sequential threshold), then processes directly. "
        "The work-stealing scheduler rebalances load dynamically — advantageous for larger "
        "images where static strip imbalance would arise.", s))
    e.append(subsec("3.3  Correctness Verification", s))
    e.append(body(
        "<b>CorrectnessVerifier.firstDifference()</b> performs a pixel-for-pixel comparison "
        "between parallel output and sequential baseline. All 6 combinations "
        "(3 filters x 2 strategies) on a 2048x2048 synthetic image produce <b>bit-identical</b> "
        "output:", s))
    cv = [
        ["Filter",          "ExecutorService (12 threads)", "ForkJoinPool (12 threads)"],
        ["Grayscale",       "PASS",                         "PASS"],
        ["GaussianBlur5x5", "PASS",                         "PASS"],
        ["Sobel3x3",        "PASS",                         "PASS"],
    ]
    e.append(make_table(cv, [5.0*cm, 5.5*cm, 5.0*cm], hdr_color=GREEN_D))

    # 4. Performance
    e += sec_header("4. Performance Comparison", s)
    e.append(body(
        "All benchmarks use <b>JMH</b> (10 warm-up + 10 measurement iterations, "
        "AverageTime mode, ms/op) on a 12-logical-core machine. "
        "Speedup = T_sequential / T_parallel.", s))

    for fname, label in [("GaussianBlur5x5","4.1  GaussianBlur 5x5"),
                         ("Sobel3x3",       "4.2  Sobel 3x3"),
                         ("Grayscale",      "4.3  Grayscale")]:
        e.append(subsec(label, s))
        hdr = [["Size","Threads","Seq (ms)","Executor (ms)","ForkJoin (ms)","Exec x","FJ x"]]
        for r in rows:
            if r["filter"] == fname:
                hdr.append([f'{r["size"]}^2', r["threads"],
                    r["sequential_ms"], r["executor_ms"], r["forkjoin_ms"],
                    r["executor_speedup"]+"x", r["forkjoin_speedup"]+"x"])
        e.append(make_table(hdr, [2.0*cm,1.7*cm,2.3*cm,2.6*cm,2.6*cm,1.8*cm,1.8*cm]))
        e.append(Spacer(1, 0.2*cm))

    # charts — each full width with caption
    e.append(subsec("4.4  Speedup Charts", s))
    e.append(Spacer(1, 0.2*cm))

    chart_w = PAGE_W - 4.5*cm

    for fname, caption in [
        ("speedup_GaussianBlur5x5.png",
         "Figure 1 — GaussianBlur 5x5: Executor (left) vs ForkJoinPool (right) across image sizes"),
        ("speedup_Sobel3x3.png",
         "Figure 2 — Sobel 3x3: Executor (left) vs ForkJoinPool (right) across image sizes"),
        ("speedup_Grayscale.png",
         "Figure 3 — Grayscale: memory-bound filter — speedup plateaus ~1.5x regardless of threads"),
        ("speedup_combined.png",
         "Figure 4 — All filters combined (2048x2048, Executor) — compute-bound filters scale, memory-bound does not"),
    ]:
        chart = imgf(fname, chart_w)
        e.append(KeepTogether([chart, Paragraph(caption, s["RCaption"])]))
        e.append(Spacer(1, 0.3*cm))

    e.append(subsec("4.5  Analysis", s))
    e.append(body(
        "<b>Compute-bound filters (Gaussian Blur, Sobel)</b> scale well with thread count, "
        "reaching 4.3x–5.1x speedup at 8 threads. ForkJoinPool outperforms ExecutorService "
        "on larger images (2048x2048) due to dynamic work-stealing load balancing.", s))
    e.append(body(
        "<b>Memory-bound filter (Grayscale)</b> plateaus at ~1.5x regardless of thread count. "
        "The single-channel lookup saturates memory bandwidth before CPU utilisation can increase — "
        "consistent with the <b>Roofline Model</b>: low arithmetic intensity = bandwidth-limited.", s))
    e.append(body(
        "<b>Amdahl's Law</b>: empirical ceiling for Gaussian Blur aligns with p ~ 0.95 parallel "
        "fraction; sequential overhead (array allocation, thread setup) limits the theoretical max.", s))

    # 5. Academic Background
    e += sec_header("5. Academic Background", s)
    e.append(body(
        "<b>Seinstra et al. (2002)</b> showed convolution filters exhibit near-linear speedup "
        "when partitioning minimises inter-thread communication — consistent with our "
        "strip-decomposition results for compute-intensive kernels.", s))
    e.append(body(
        "<b>Amdahl (1967)</b>: S = 1/(1-p). For Gaussian Blur, p ~ 0.95 gives theoretical max "
        "~20x; our 4-5x at 8 threads is expected given practical overhead.", s))
    e.append(body(
        "<b>Williams et al. (2009)</b> — Roofline Model — explains divergent scalability via "
        "arithmetic intensity: memory-bound kernels saturate bandwidth before compute capacity. "
        "<b>Lea (2000)</b> provides the theoretical basis for ForkJoinPool's work-stealing "
        "scheduler, explaining its advantage for uneven workloads.", s))

    # 6. Challenges
    e += sec_header("6. Challenges and Solutions", s)
    chs = [
        ("JVM JIT Warm-up and GC Noise",
         "System.nanoTime() measurements were skewed by JIT and GC. "
         "<b>Solution:</b> Adopted JMH with warm-up iterations and fork-per-config."),
        ("Bit-Identical Correctness Across Implementations",
         "Strip boundaries required careful handling. "
         "<b>Solution:</b> CorrectnessVerifier with pixel-for-pixel scan; "
         "clamped-coordinate edge handling ensures identical border treatment."),
        ("Varying Scalability Between Filters",
         "Grayscale achieved only ~1.5x with 8 threads. "
         "<b>Solution:</b> Profiling confirmed memory bandwidth saturation (Roofline Model) "
         "as root cause — not thread management inefficiency."),
        ("ForkJoin Recursive Overhead on Small Images",
         "For 512x512, ForkJoin recursion overhead slightly exceeded Executor. "
         "<b>Solution:</b> Tuned SEQUENTIAL_THRESHOLD to 64 rows to prevent "
         "excessive task granularity."),
    ]
    for title, desc in chs:
        e.append(KeepTogether([bul(f"<b>{title}:</b>  {desc}", s)]))

    # 7. Conclusion
    e += sec_header("7. Conclusion and Future Improvements", s)
    e.append(body(
        "This project successfully demonstrated parallelisation of image convolution algorithms "
        "using Java concurrency. JMH benchmarks confirmed significant speedups for compute-bound "
        "operations: Gaussian Blur reached ~4.30x (Executor) and ~4.81x (ForkJoin) at 8 threads "
        "on 2048x2048; Sobel reached ~4.49x and ~5.10x. Grayscale was confirmed memory-bound "
        "at ~1.55x. ForkJoinPool's work-stealing advantage grew with image size.", s))
    fws = [
        "GPU/CUDA — exploit thousands of CUDA cores for pixel-independent kernels",
        "SIMD vectorisation (AVX2/AVX-512) — intra-core throughput gains",
        "4K and 8K benchmarks — evaluate boundary overhead at ultra-high resolution",
        "Adaptive thread pool — dynamic tuning based on image size and hardware profile",
        "Cache-blocking and prefetching — optimise memory-bound filters like Grayscale",
    ]
    for fw in fws:
        e.append(bul(fw, s))

    # 8. References
    e += sec_header("8. References", s)
    refs = [
        "Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale "
        "computing capabilities. <i>Proc. Spring Joint Computer Conf.</i>, 483-485. "
        "https://doi.org/10.1145/1465482.1465560",
        "Seinstra, F. J., Koelma, D., & Bagdanov, A. D. (2002). Finite state machine-based "
        "optimization of data parallel regular domain problems applied to low-level image "
        "processing. <i>IEEE Trans. Parallel Distrib. Syst.</i>, 15(10), 865-877. "
        "https://doi.org/10.1109/TPDS.2004.45",
        "Williams, S., Waterman, A., & Patterson, D. (2009). Roofline: An insightful visual "
        "performance model for multicore architectures. <i>Commun. ACM</i>, 52(4), 65-76. "
        "https://doi.org/10.1145/1498765.1498785",
        "Lea, D. (2000). A Java fork/join framework. <i>Proc. ACM Java Grande Conf.</i>, 36-43. "
        "https://doi.org/10.1145/337449.337465",
    ]
    for i, r in enumerate(refs, 1):
        e.append(Paragraph(f"[{i}]  {r}", s["RSmall"]))
        e.append(Spacer(1, 0.15*cm))

    return e


# ---------------------------------------------------------------------------
# Slide builder
# ---------------------------------------------------------------------------
class SlideFlowable(Flowable):
    """Draws a single presentation slide as a blue rounded rectangle."""

    SLIDE_W = PAGE_W - 4*cm
    SLIDE_H = 7.5*cm

    def __init__(self, number, title, items, note=None):
        Flowable.__init__(self)
        self.number = number
        self.title  = title
        self.items  = items   # list of (kind, text): kind in "bullet","body","sub"
        self.note   = note
        self.width  = self.SLIDE_W
        self.height = self.SLIDE_H + 0.1*cm

    def draw(self):
        c   = self.canv
        W   = self.SLIDE_W
        H   = self.SLIDE_H

        # background
        c.setFillColor(BLUE)
        c.roundRect(0, 0, W, H, 8, fill=1, stroke=0)

        # title bar
        c.setFillColor(colors.HexColor("#0d2244"))
        c.roundRect(0, H - 1.5*cm, W, 1.5*cm, 8, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(0, H - 1.5*cm, W, 0.5*cm, fill=1, stroke=0)

        # slide number badge
        c.setFillColor(GOLD)
        c.roundRect(0.3*cm, H - 1.3*cm, 1.0*cm, 0.8*cm, 4, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(0.3*cm + 0.5*cm, H - 0.95*cm, str(self.number))

        # title text
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.6*cm, H - 1.1*cm, self.title)

        # gold top border line
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.5)
        c.line(0.3*cm, H - 1.55*cm, W - 0.3*cm, H - 1.55*cm)

        # content items
        y = H - 2.2*cm
        for kind, text in self.items:
            if kind == "sub":
                c.setFillColor(GOLD)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(0.6*cm, y, text)
                y -= 0.5*cm
            elif kind == "bullet":
                c.setFillColor(GOLD)
                c.circle(0.75*cm, y + 0.12*cm, 0.055*cm, fill=1, stroke=0)
                c.setFillColor(WHITE)
                c.setFont("Helvetica", 9)
                self._wrapped(c, text, 0.95*cm, y, W - 1.2*cm, 9)
                lines = self._line_count(text, W - 1.2*cm, 9)
                y -= lines * 0.42*cm + 0.08*cm
            elif kind == "body":
                c.setFillColor(colors.HexColor("#aaccee"))
                c.setFont("Helvetica-Oblique", 8.5)
                c.drawCentredString(W/2, y, text)
                y -= 0.5*cm
            elif kind == "space":
                y -= 0.3*cm

        # note at bottom
        if self.note:
            c.setFillColor(colors.HexColor("#0d2244"))
            c.roundRect(0.3*cm, 0.2*cm, W - 0.6*cm, 0.65*cm, 4, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Oblique", 7.5)
            c.drawCentredString(W/2, 0.38*cm, self.note)

    def _wrapped(self, c, text, x, y, max_w, fs):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        line  = ""
        first = True
        for w in words:
            test = (line + " " + w).strip()
            if stringWidth(test, "Helvetica", fs) <= max_w:
                line = test
            else:
                c.drawString(x, y, line)
                y -= 0.38*cm
                line = w
                first = False
        if line:
            c.drawString(x, y, line)

    def _line_count(self, text, max_w, fs):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        line  = ""
        count = 1
        for w in words:
            test = (line + " " + w).strip()
            if stringWidth(test, "Helvetica", fs) <= max_w:
                line = test
            else:
                count += 1
                line = w
        return count


def presentation_content(s, rows):
    e = []
    e.append(PageBreak())
    e.append(Spacer(1, 0.3*cm))
    e.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=3))
    e.append(Paragraph("PRESENTATION SLIDES  (10 Slides)", s["RSec"]))
    e.append(HRFlowable(width="100%", thickness=0.5, color=BLUE_LIGHT, spaceAfter=8))

    slides = [
        SlideFlowable(1, "Parallel Image Processing Engine", [
            ("space",""),
            ("body",  "CENG 479 -- Parallel Computing  |  Gazi University  |  Spring 2026"),
            ("body",  "Muhammed Cakiagoz   .   Musa Bilal Yaz"),
            ("space",""),
            ("body",  GITHUB),
        ], note="Java Threads | ExecutorService | ForkJoinPool | JMH Benchmark"),

        SlideFlowable(2, "Problem & Motivation", [
            ("bullet","High-resolution image filtering (4K+) is slow on a single thread"),
            ("bullet","Convolution cost: O(W x H x K^2) per filter -- bottleneck at scale"),
            ("bullet","Each output pixel is INDEPENDENT of others -- embarrassingly parallel"),
            ("bullet","Goal: multi-threaded speedup with zero correctness compromise"),
            ("space",""),
            ("body",  "Amdahl's Law: S = 1/(1-p)  --  p ~ 0.95 for Gaussian Blur"),
        ], note="Theoretical max speedup ~20x at p=0.95; practical ceiling limited by memory and overhead"),

        SlideFlowable(3, "Architecture Overview", [
            ("sub",   "Filters:"),
            ("bullet","Grayscale (point-wise), Gaussian Blur 5x5, Sobel 3x3"),
            ("sub",   "Implementations:"),
            ("bullet","SequentialProcessor -- single-thread baseline"),
            ("bullet","ExecutorParallelProcessor -- fixed pool + horizontal strips"),
            ("bullet","ForkJoinParallelProcessor -- RecursiveAction + work-stealing"),
            ("sub",   "Tools:"),
            ("bullet","CorrectnessVerifier + JMH Benchmark"),
        ], note="All source code publicly available on GitHub"),

        SlideFlowable(4, "ExecutorService Design", [
            ("bullet","Image split into N equal horizontal strips (N = thread count)"),
            ("bullet","Each Callable processes rows [start, end) with no locking"),
            ("bullet","Source array is READ-ONLY during compute -- zero synchronisation overhead"),
            ("bullet","Thread pool created once, reused via try-with-resources"),
            ("space",""),
            ("body",  "Strip[i] covers rows:  i*(H/N)  to  (i+1)*(H/N)"),
        ], note="Static decomposition -- optimal for uniform workloads"),

        SlideFlowable(5, "ForkJoinPool Design", [
            ("bullet","RecursiveAction splits row range in half recursively"),
            ("bullet","Base case: range <= 64 rows -- process sequentially"),
            ("bullet","Work-stealing: idle threads steal tasks from busy queues"),
            ("bullet","Better dynamic load balance than static strips for large images"),
            ("space",""),
            ("bullet","ForkJoin outperforms Executor on 2048x2048 (Gaussian: 4.81x vs 4.30x)"),
        ], note="Dynamic decomposition -- adapts to runtime load imbalance"),

        SlideFlowable(6, "Correctness Verification", [
            ("body",  "CorrectnessVerifier.firstDifference() -- pixel-by-pixel scan"),
            ("space",""),
            ("body",  "Tested on 2048x2048 synthetic image -- ALL 6 combinations PASS"),
            ("space",""),
            ("bullet","Grayscale:       Executor PASS  |  ForkJoin PASS"),
            ("bullet","GaussianBlur5x5: Executor PASS  |  ForkJoin PASS"),
            ("bullet","Sobel3x3:        Executor PASS  |  ForkJoin PASS"),
        ], note="Bit-identical output to sequential baseline in all cases"),

        SlideFlowable(7, "Performance Results (8 threads, 2048x2048)", [
            ("sub",   "Compute-bound (scales well):"),
            ("bullet","Gaussian Blur:  Executor 4.30x  |  ForkJoin 4.81x"),
            ("bullet","Sobel 3x3:      Executor 4.49x  |  ForkJoin 5.10x"),
            ("space",""),
            ("sub",   "Memory-bound (bandwidth limited):"),
            ("bullet","Grayscale:      Executor 1.55x  |  ForkJoin 1.54x"),
        ], note="JMH benchmark | 10 warm-up + 10 measurement iterations | AverageTime ms/op"),

        SlideFlowable(8, "Speedup Charts", [
            ("space",""),
            ("body",  "GaussianBlur5x5 & Sobel -- near-linear scaling up to 4-5x at 8 threads"),
            ("body",  "Grayscale -- memory bandwidth saturation caps speedup at ~1.5x"),
            ("body",  "ForkJoin advantage grows with image size (work-stealing benefit)"),
            ("space",""),
            ("body",  "[See Figures 1-4 in the report section for full charts]"),
        ], note="Roofline Model: compute-bound = scales | memory-bound = does not"),

        SlideFlowable(9, "Challenges & Key Findings", [
            ("bullet","JIT warm-up noise -- solved with JMH (fork-per-config, 10 warm-up iters)"),
            ("bullet","Correctness -- clamped edges + pixel-for-pixel CorrectnessVerifier"),
            ("bullet","Grayscale bottleneck -- memory bandwidth saturated (Roofline Model)"),
            ("bullet","ForkJoin overhead on small images -- tuned threshold to 64 rows"),
            ("space",""),
            ("body",  "Key insight: speedup is FILTER-DEPENDENT -- arithmetic intensity determines scalability"),
        ], note="Benchmark environment: 12 logical cores, JDK 17, Maven 3.6"),

        SlideFlowable(10, "Conclusion & Future Work", [
            ("bullet","Parallelised 3 convolution filters with 2 Java concurrency strategies"),
            ("bullet","Up to 5.10x speedup (Sobel, ForkJoin, 8 threads, 2048x2048)"),
            ("bullet","Memory-bound filters need different strategy (not thread-level parallelism)"),
            ("sub",   "Future Work:"),
            ("bullet","GPU/CUDA -- thousands of concurrent cores for pixel-independent kernels"),
            ("bullet","SIMD vectorisation (AVX2/AVX-512) for intra-core throughput"),
            ("bullet","Adaptive thread pool -- dynamic tuning per image size and hardware"),
        ], note=GITHUB),
    ]

    for slide in slides:
        e.append(slide)
        e.append(Spacer(1, 0.45*cm))

    return e


# ---------------------------------------------------------------------------
# Page numbering callback
# ---------------------------------------------------------------------------
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRAY_D)
    page = canvas.getPageNumber()
    canvas.drawRightString(PAGE_W - 2*cm, 1.1*cm, f"Page {page}")
    canvas.drawString(2*cm, 1.1*cm, "CENG 479 — Parallel Image Processing  |  Submission 2")
    canvas.setStrokeColor(BLUE_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.35*cm, PAGE_W - 2*cm, 1.35*cm)
    canvas.restoreState()


def cover_page_cb(canvas, doc):
    """No footer on cover page."""
    pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out  = os.path.join(BASE, "CENG479_Sub2_Final_Report.pdf")
    rows = load_speedup()
    s    = make_styles()

    doc = SimpleDocTemplate(
        out,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
        title="CENG 479 Parallel Image Processing -- Final Report",
        author="Muhammed Cakiagoz, Musa Bilal Yaz",
    )

    story = []

    # --- Cover ---
    story.append(CoverPage())
    story.append(PageBreak())

    # --- Report ---
    story += report_content(s, rows)

    # --- Presentation ---
    story += presentation_content(s, rows)

    doc.build(story, onFirstPage=cover_page_cb, onLaterPages=add_page_number)
    size_kb = os.path.getsize(out) // 1024
    print(f"PDF written: {out}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
