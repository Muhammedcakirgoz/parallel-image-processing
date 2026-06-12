# Parallel Image Processing Engine (Java Threads)

**CENG479 — Parallel Computing — Submission 2**
Gazi University, Department of Computer Engineering — Spring 2026

**Team:**
-  Muhammed Çakırgöz
-  Musa Bilal Yaz

---

## Overview

This project applies three convolution-based image filters to large images and
compares a **sequential baseline** against two **parallel implementations** built
with Java's concurrency framework.

| Implementation | Strategy |
|---|---|
| `SequentialProcessor` | Single-threaded, row-by-row (baseline) |
| `ExecutorParallelProcessor` | Fixed thread pool + horizontal strip decomposition |
| `ForkJoinParallelProcessor` | `ForkJoinPool` work-stealing + divide-and-conquer |

**Filters:**
- **Grayscale** — point-wise luminance conversion (kernel radius 0)
- **Gaussian Blur 5×5** — most compute-intensive (25 weighted taps per pixel)
- **Sobel 3×3** — edge detection (Gx, Gy gradient magnitude)

The core idea is **pixel independence**: each output pixel depends only on a
fixed neighborhood of the *input* image, so the image can be split across
threads with no locking during the compute phase.

---

## Benchmark Results (Highlights)

Measured with JMH on a 6-core / 12-thread machine (2048×2048 image, 8 threads):

| Filter | Executor Speedup | ForkJoin Speedup |
|---|---|---|
| Grayscale (memory-bound) | 1.53× | 1.52× |
| Gaussian Blur 5×5 (compute-bound) | 4.31× | 4.82× |
| Sobel 3×3 (compute-bound) | 4.57× | 5.19× |

Compute-bound filters scale well (4–5×); the memory-bandwidth-bound grayscale
filter plateaus near 1.5×, illustrating that speedup depends on the arithmetic
intensity of the workload.

---

## Requirements

- JDK 17 or newer
- Maven 3.6+

## Build

```bash
mvn clean package
```

This produces `target/image-processing.jar` (an executable fat-jar).

## Run the correctness demo

Verifies that both parallel implementations produce **pixel-identical** output
to the sequential baseline, for all three filters:

```bash
java -jar target/image-processing.jar
```

## Filter a real image

```bash
java -jar target/image-processing.jar demo path/to/photo.png
```

This writes `photo_Grayscale.png`, `photo_GaussianBlur5x5.png`, and
`photo_Sobel3x3.png`.

## Quick (rough) timing

```bash
java -jar target/image-processing.jar time 2048 2048 4
```

> This mode uses `System.nanoTime()` and is affected by JIT warm-up.
> For grade-quality numbers, use the JMH benchmark below.

---

## Benchmarking with JMH

The JMH harness runs warm-up iterations, prevents dead-code elimination, and
forks a clean JVM per configuration, producing reproducible speedup numbers.

```bash
mvn clean package
java -cp target/image-processing.jar com.ceng479.imaging.benchmark.BenchmarkRunner
```

Results are written to `jmh-results.csv`. The benchmark sweeps:

- **size** ∈ {512, 1024, 2048}
- **threads** ∈ {1, 2, 4, 8}
- **filter** ∈ {Grayscale, GaussianBlur5x5, Sobel3x3}

### Computing speedup

```
speedup = sequential_time(size, filter) / parallel_time(size, threads, filter)
```

Turn the raw CSV into a tidy speedup table and charts:

```bash
python3 scripts/process_results.py jmh-results.csv
```

---

## Project Layout

```
src/main/java/com/ceng479/imaging/
├── App.java                       # CLI entry point (demo / time modes)
├── core/
│   ├── Filter.java                # filter contract
│   └── PixelUtils.java            # channel + clamp helpers
├── filters/
│   ├── GrayscaleFilter.java
│   ├── GaussianBlurFilter.java
│   └── SobelFilter.java
├── sequential/
│   └── SequentialProcessor.java   # baseline
├── parallel/
│   ├── ExecutorParallelProcessor.java
│   └── ForkJoinParallelProcessor.java
├── util/
│   ├── ImageIOUtils.java          # load/save + synthetic generator
│   └── CorrectnessVerifier.java
└── benchmark/
    ├── FilterBenchmark.java        # JMH benchmark
    └── BenchmarkRunner.java        # programmatic launcher → CSV
```

---

## Notes on Correctness

All parallel implementations are verified against the sequential baseline using
`CorrectnessVerifier.firstDifference()`, a pixel-for-pixel comparison. The
parallel and sequential outputs are **bit-identical** because:

1. Strip/row partitions are disjoint (no overlapping writes).
2. The source array is read-only during processing (no data races).
3. Edge handling (clamped coordinates) is identical across implementations.
