package com.ceng479.imaging.core;

/**
 * Common contract for all image filters.
 *
 * <p>Every filter computes the output value of a single pixel (x, y) given the
 * source pixel data. Because each pixel's output depends only on a fixed
 * neighborhood of the <em>input</em> image (never on the output of other
 * pixels), filters are stateless and thread-safe: many threads may call
 * {@link #applyPixel} concurrently on the same source array as long as each
 * writes to a distinct output location.
 *
 * <p>This pixel-independence is the theoretical basis for the parallelization
 * strategy used throughout this project.
 */
public interface Filter {

    /**
     * Computes the filtered ARGB value for a single output pixel.
     *
     * @param src    source pixels in row-major ARGB int format (length = width*height)
     * @param width  image width in pixels
     * @param height image height in pixels
     * @param x      column of the pixel to compute (0 <= x < width)
     * @param y      row of the pixel to compute (0 <= y < height)
     * @return the packed ARGB value for the output pixel
     */
    int applyPixel(int[] src, int width, int height, int x, int y);

    /** Human-readable filter name, used in benchmark labels and logs. */
    String name();

    /**
     * Radius of the convolution kernel in pixels. Used to size the "halo"
     * (overlap) region when an image is split into strips for parallel
     * processing. A value of 0 means the filter is purely point-wise
     * (e.g. grayscale) and needs no halo.
     */
    int kernelRadius();
}
