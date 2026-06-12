package com.ceng479.imaging.filters;

import com.ceng479.imaging.core.Filter;
import com.ceng479.imaging.core.PixelUtils;

/**
 * 5x5 Gaussian Blur. Each output pixel is the normalized weighted average of
 * its 5x5 neighborhood in the source image. This is the most compute-intensive
 * filter in the project: 25 multiply-accumulate operations per channel per
 * pixel.
 *
 * <p>The kernel is the standard separable 5x5 Gaussian approximation with
 * integer weights summing to 256 (so normalization is a cheap shift by 8).
 * Border pixels use edge-extend (clamped coordinate) handling.
 */
public final class GaussianBlurFilter implements Filter {

    private static final int RADIUS = 2; // 5x5 kernel

    // 5x5 Gaussian weights (sum = 256). Pascal-triangle [1 4 6 4 1] outer product.
    private static final int[][] KERNEL = {
        { 1,  4,  6,  4,  1},
        { 4, 16, 24, 16,  4},
        { 6, 24, 36, 24,  6},
        { 4, 16, 24, 16,  4},
        { 1,  4,  6,  4,  1}
    };
    private static final int KERNEL_SUM = 256; // shift by 8

    @Override
    public int applyPixel(int[] src, int width, int height, int x, int y) {
        int aAcc = 0, rAcc = 0, gAcc = 0, bAcc = 0;

        for (int ky = -RADIUS; ky <= RADIUS; ky++) {
            int sy = PixelUtils.clampCoord(y + ky, height);
            int rowBase = sy * width;
            for (int kx = -RADIUS; kx <= RADIUS; kx++) {
                int sx = PixelUtils.clampCoord(x + kx, width);
                int w = KERNEL[ky + RADIUS][kx + RADIUS];
                int argb = src[rowBase + sx];
                aAcc += w * PixelUtils.alpha(argb);
                rAcc += w * PixelUtils.red(argb);
                gAcc += w * PixelUtils.green(argb);
                bAcc += w * PixelUtils.blue(argb);
            }
        }

        int a = aAcc / KERNEL_SUM;
        int r = rAcc / KERNEL_SUM;
        int g = gAcc / KERNEL_SUM;
        int b = bAcc / KERNEL_SUM;

        return PixelUtils.argb(
            PixelUtils.clampChannel(a),
            PixelUtils.clampChannel(r),
            PixelUtils.clampChannel(g),
            PixelUtils.clampChannel(b)
        );
    }

    @Override
    public String name() { return "GaussianBlur5x5"; }

    @Override
    public int kernelRadius() { return RADIUS; }
}
