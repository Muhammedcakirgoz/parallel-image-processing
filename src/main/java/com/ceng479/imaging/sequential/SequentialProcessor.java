package com.ceng479.imaging.sequential;

import com.ceng479.imaging.core.Filter;

/**
 * Sequential baseline. Applies a filter to every pixel using a single thread,
 * iterating row by row. This is the reference implementation against which all
 * parallel speedups are measured.
 */
public final class SequentialProcessor {

    /**
     * Applies the given filter to the whole image on the calling thread.
     *
     * @param src    source pixels (row-major ARGB, length = width*height)
     * @param width  image width
     * @param height image height
     * @param filter the filter to apply
     * @return a new array holding the filtered image
     */
    public int[] process(int[] src, int width, int height, Filter filter) {
        int[] dst = new int[src.length];
        for (int y = 0; y < height; y++) {
            int rowBase = y * width;
            for (int x = 0; x < width; x++) {
                dst[rowBase + x] = filter.applyPixel(src, width, height, x, y);
            }
        }
        return dst;
    }
}
