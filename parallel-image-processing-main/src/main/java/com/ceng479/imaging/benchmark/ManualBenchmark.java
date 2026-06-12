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

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.Locale;

/**
 * Manual benchmark replacing JMH when offline.
 * Warm-up: 5 iterations (discarded). Measurement: 10 iterations (averaged).
 */
public class ManualBenchmark {

    private static final int WARMUP = 5;
    private static final int MEASURE = 10;

    private static final int[] SIZES   = {512, 1024, 2048};
    private static final int[] THREADS = {1, 2, 4, 8};

    private static final List<Filter> FILTERS = List.of(
        new GrayscaleFilter(),
        new GaussianBlurFilter(),
        new SobelFilter()
    );

    public static void main(String[] args) throws IOException {
        Locale.setDefault(Locale.US);
        String csvPath = args.length > 0 ? args[0] : "jmh-results.csv";

        System.out.printf("%-12s %-18s %7s %12s %12s %12s %10s %10s%n",
            "size", "filter", "threads",
            "seq_ms", "exec_ms", "fj_ms",
            "exec_su", "fj_su");
        System.out.println("-".repeat(100));

        try (PrintWriter csv = new PrintWriter(new FileWriter(csvPath))) {
            csv.println("size,filter,threads,sequential_ms,executor_ms,forkjoin_ms,executor_speedup,forkjoin_speedup");

            for (int size : SIZES) {
                ImageData img = ImageIOUtils.generateSynthetic(size, size, 42L);
                SequentialProcessor seq = new SequentialProcessor();

                for (Filter filter : FILTERS) {

                    // --- sequential baseline (measure once per size+filter) ---
                    for (int i = 0; i < WARMUP; i++)
                        seq.process(img.pixels, size, size, filter);
                    long seqTotal = 0;
                    for (int i = 0; i < MEASURE; i++) {
                        long t = System.nanoTime();
                        seq.process(img.pixels, size, size, filter);
                        seqTotal += System.nanoTime() - t;
                    }
                    double seqMs = seqTotal / 1e6 / MEASURE;

                    for (int threads : THREADS) {
                        // --- executor ---
                        double execMs;
                        try (ExecutorParallelProcessor exec = new ExecutorParallelProcessor(threads)) {
                            for (int i = 0; i < WARMUP; i++)
                                exec.process(img.pixels, size, size, filter);
                            long total = 0;
                            for (int i = 0; i < MEASURE; i++) {
                                long t = System.nanoTime();
                                exec.process(img.pixels, size, size, filter);
                                total += System.nanoTime() - t;
                            }
                            execMs = total / 1e6 / MEASURE;
                        }

                        // --- forkjoin ---
                        double fjMs;
                        try (ForkJoinParallelProcessor fj = new ForkJoinParallelProcessor(threads)) {
                            for (int i = 0; i < WARMUP; i++)
                                fj.process(img.pixels, size, size, filter);
                            long total = 0;
                            for (int i = 0; i < MEASURE; i++) {
                                long t = System.nanoTime();
                                fj.process(img.pixels, size, size, filter);
                                total += System.nanoTime() - t;
                            }
                            fjMs = total / 1e6 / MEASURE;
                        }

                        double execSpeedup = seqMs / execMs;
                        double fjSpeedup   = seqMs / fjMs;

                        System.out.printf("%-12d %-18s %7d %12.2f %12.2f %12.2f %10.2f %10.2f%n",
                            size, filter.name(), threads,
                            seqMs, execMs, fjMs,
                            execSpeedup, fjSpeedup);

                        csv.printf("%d,%s,%d,%.2f,%.2f,%.2f,%.2f,%.2f%n",
                            size, filter.name(), threads,
                            seqMs, execMs, fjMs,
                            execSpeedup, fjSpeedup);
                        csv.flush();
                    }
                }
                System.out.println();
            }
        }
        System.out.println("\nResults saved to " + csvPath);
    }
}
