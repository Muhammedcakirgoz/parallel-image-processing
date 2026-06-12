package com.ceng479.imaging.parallel;

import com.ceng479.imaging.core.Filter;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/**
 * Parallel processor using a fixed-size thread pool ({@link ExecutorService})
 * and horizontal strip decomposition.
 *
 * <p>The image is split into N horizontal strips, where N is the configured
 * thread count. Each strip is handed to a {@link Callable} task that filters
 * its own rows into a shared, pre-allocated output array. Because every task
 * writes to a disjoint set of rows and only ever reads (never writes) the
 * source array, no locking or synchronization is needed during processing.
 *
 * <p>The halo (overlap) needed for convolution kernels is handled implicitly:
 * each task reads from the full shared source array using clamped coordinates,
 * so it can freely read neighboring rows that belong to adjacent strips.
 */
public final class ExecutorParallelProcessor implements AutoCloseable {

    private final int threadCount;
    private final ExecutorService pool;

    public ExecutorParallelProcessor(int threadCount) {
        if (threadCount < 1) {
            throw new IllegalArgumentException("threadCount must be >= 1");
        }
        this.threadCount = threadCount;
        this.pool = Executors.newFixedThreadPool(threadCount);
    }

    public int[] process(int[] src, int width, int height, Filter filter) {
        final int[] dst = new int[src.length];

        // Divide rows as evenly as possible across the worker tasks.
        int rowsPerStrip = (height + threadCount - 1) / threadCount; // ceil
        List<Callable<Void>> tasks = new ArrayList<>(threadCount);

        for (int t = 0; t < threadCount; t++) {
            final int startRow = t * rowsPerStrip;
            if (startRow >= height) break; // more threads than rows
            final int endRow = Math.min(startRow + rowsPerStrip, height);

            tasks.add(() -> {
                for (int y = startRow; y < endRow; y++) {
                    int rowBase = y * width;
                    for (int x = 0; x < width; x++) {
                        dst[rowBase + x] = filter.applyPixel(src, width, height, x, y);
                    }
                }
                return null;
            });
        }

        try {
            List<Future<Void>> futures = pool.invokeAll(tasks);
            // Propagate any exception thrown inside a worker.
            for (Future<Void> f : futures) {
                f.get();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Parallel processing interrupted", e);
        } catch (ExecutionException e) {
            throw new RuntimeException("Worker task failed", e.getCause());
        }

        return dst;
    }

    public int threadCount() { return threadCount; }

    /** Shuts down the underlying thread pool. */
    @Override
    public void close() {
        pool.shutdown();
    }
}
