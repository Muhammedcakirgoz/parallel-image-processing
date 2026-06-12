package com.ceng479.imaging.parallel;

import com.ceng479.imaging.core.Filter;

import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

/**
 * Parallel processor using the {@link ForkJoinPool} work-stealing framework and
 * a divide-and-conquer ({@link RecursiveAction}) decomposition.
 *
 * <p>The image's row range is recursively split in half until a strip is small
 * enough (<= THRESHOLD rows), at which point it is processed directly. The
 * ForkJoinPool's work-stealing scheduler balances load automatically, which can
 * outperform a fixed strip layout when CPU availability varies (e.g. due to
 * background OS activity or uneven per-pixel cost).
 */
public final class ForkJoinParallelProcessor implements AutoCloseable {

    /** Strips of this many rows or fewer are processed without further splitting. */
    private static final int DEFAULT_THRESHOLD = 32;

    private final ForkJoinPool pool;
    private final int threshold;
    private final int parallelism;

    public ForkJoinParallelProcessor(int parallelism) {
        this(parallelism, DEFAULT_THRESHOLD);
    }

    public ForkJoinParallelProcessor(int parallelism, int threshold) {
        if (parallelism < 1) {
            throw new IllegalArgumentException("parallelism must be >= 1");
        }
        this.parallelism = parallelism;
        this.threshold = threshold;
        this.pool = new ForkJoinPool(parallelism);
    }

    public int[] process(int[] src, int width, int height, Filter filter) {
        int[] dst = new int[src.length];
        pool.invoke(new FilterTask(src, dst, width, height, filter, 0, height, threshold));
        return dst;
    }

    public int parallelism() { return parallelism; }

    @Override
    public void close() {
        pool.shutdown();
    }

    /**
     * A recursive task that filters rows [startRow, endRow). If the range is
     * larger than the threshold, it splits into two halves and forks them;
     * otherwise it computes the rows directly.
     */
    private static final class FilterTask extends RecursiveAction {
        private final int[] src;
        private final int[] dst;
        private final int width;
        private final int height;
        private final Filter filter;
        private final int startRow;
        private final int endRow;
        private final int threshold;

        FilterTask(int[] src, int[] dst, int width, int height, Filter filter,
                   int startRow, int endRow, int threshold) {
            this.src = src;
            this.dst = dst;
            this.width = width;
            this.height = height;
            this.filter = filter;
            this.startRow = startRow;
            this.endRow = endRow;
            this.threshold = threshold;
        }

        @Override
        protected void compute() {
            int rows = endRow - startRow;
            if (rows <= threshold) {
                computeDirectly();
            } else {
                int mid = startRow + rows / 2;
                FilterTask left = new FilterTask(src, dst, width, height, filter, startRow, mid, threshold);
                FilterTask right = new FilterTask(src, dst, width, height, filter, mid, endRow, threshold);
                invokeAll(left, right);
            }
        }

        private void computeDirectly() {
            for (int y = startRow; y < endRow; y++) {
                int rowBase = y * width;
                for (int x = 0; x < width; x++) {
                    dst[rowBase + x] = filter.applyPixel(src, width, height, x, y);
                }
            }
        }
    }
}
