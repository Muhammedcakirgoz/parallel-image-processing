package com.ceng479.imaging.benchmark;

import com.ceng479.imaging.core.Filter;
import com.ceng479.imaging.filters.GaussianBlurFilter;
import com.ceng479.imaging.filters.GrayscaleFilter;
import com.ceng479.imaging.filters.SobelFilter;
import com.ceng479.imaging.parallel.ExecutorParallelProcessor;
import com.ceng479.imaging.parallel.ForkJoinParallelProcessor;
import com.ceng479.imaging.sequential.SequentialProcessor;
import com.ceng479.imaging.util.ImageIOUtils;
import com.ceng479.imaging.util.ImageIOUtils.ImageData;
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

import java.util.concurrent.TimeUnit;

/**
 * JMH microbenchmark comparing the sequential baseline against the two parallel
 * implementations (ExecutorService and ForkJoinPool) across image sizes, thread
 * counts, and filters.
 *
 * <p>Why JMH instead of System.nanoTime()? JMH runs dedicated warm-up
 * iterations so the JVM fully JIT-compiles the hot loops before measurement,
 * uses {@link Blackhole} to prevent dead-code elimination of the filter output,
 * and forks a fresh JVM per configuration to avoid profile pollution. This
 * yields reproducible, defensible speedup numbers.
 *
 * <p>Measurement mode is average time per operation (lower is better).
 */
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
@State(Scope.Benchmark)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Fork(value = 1)
public class FilterBenchmark {

    /** Image edge length; produces a square image of size x size pixels. */
    @Param({"512", "1024", "2048"})
    public int size;

    /** Worker thread count for the parallel implementations. */
    @Param({"1", "2", "4", "8"})
    public int threads;

    /** Which filter to apply. */
    @Param({"Grayscale", "GaussianBlur5x5", "Sobel3x3"})
    public String filterName;

    private int[] src;
    private int width;
    private int height;
    private Filter filter;

    private SequentialProcessor sequential;
    private ExecutorParallelProcessor executor;
    private ForkJoinParallelProcessor forkJoin;

    @Setup(Level.Trial)
    public void setup() {
        width = size;
        height = size;
        ImageData img = ImageIOUtils.generateSynthetic(width, height, 42L);
        src = img.pixels;
        filter = resolveFilter(filterName);

        sequential = new SequentialProcessor();
        executor = new ExecutorParallelProcessor(threads);
        forkJoin = new ForkJoinParallelProcessor(threads);
    }

    @TearDown(Level.Trial)
    public void tearDown() {
        executor.close();
        forkJoin.close();
    }

    private static Filter resolveFilter(String name) {
        switch (name) {
            case "Grayscale":       return new GrayscaleFilter();
            case "GaussianBlur5x5": return new GaussianBlurFilter();
            case "Sobel3x3":        return new SobelFilter();
            default: throw new IllegalArgumentException("Unknown filter: " + name);
        }
    }

    // ----- Benchmarks -------------------------------------------------------

    /**
     * Sequential baseline. Note: this ignores the {@code threads} param, so JMH
     * will report identical sequential times across thread counts (expected).
     * The baseline at threads=1 is the reference for speedup computation.
     */
    @Benchmark
    public void sequential(Blackhole bh) {
        bh.consume(sequential.process(src, width, height, filter));
    }

    /** Parallel via fixed thread pool + strip decomposition. */
    @Benchmark
    public void executorParallel(Blackhole bh) {
        bh.consume(executor.process(src, width, height, filter));
    }

    /** Parallel via ForkJoinPool work-stealing + divide-and-conquer. */
    @Benchmark
    public void forkJoinParallel(Blackhole bh) {
        bh.consume(forkJoin.process(src, width, height, filter));
    }
}
