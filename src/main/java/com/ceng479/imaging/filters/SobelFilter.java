package com.ceng479.imaging.filters;

import com.ceng479.imaging.core.Filter;
import com.ceng479.imaging.core.PixelUtils;

/**
 * Sobel edge detection. Computes the gradient magnitude at each pixel using two
 * 3x3 convolution kernels (horizontal Gx and vertical Gy) applied to the
 * luminance of the neighborhood, then combines them as sqrt(Gx^2 + Gy^2).
 *
 * <p>The output is a grayscale edge-strength image where bright pixels mark
 * strong edges. Border pixels use edge-extend handling.
 */
public final class SobelFilter implements Filter {

    private static final int RADIUS = 1; // 3x3 kernel

    private static final int[][] GX = {
        {-1, 0, 1},
        {-2, 0, 2},
        {-1, 0, 1}
    };
    private static final int[][] GY = {
        {-1, -2, -1},
        { 0,  0,  0},
        { 1,  2,  1}
    };

    @Override
    public int applyPixel(int[] src, int width, int height, int x, int y) {
        int sumX = 0, sumY = 0;

        for (int ky = -RADIUS; ky <= RADIUS; ky++) {
            int sy = PixelUtils.clampCoord(y + ky, height);
            int rowBase = sy * width;
            for (int kx = -RADIUS; kx <= RADIUS; kx++) {
                int sx = PixelUtils.clampCoord(x + kx, width);
                int argb = src[rowBase + sx];
                // Use luminance as the scalar intensity for gradient computation.
                int lum = (299 * PixelUtils.red(argb)
                         + 587 * PixelUtils.green(argb)
                         + 114 * PixelUtils.blue(argb)) / 1000;
                sumX += GX[ky + RADIUS][kx + RADIUS] * lum;
                sumY += GY[ky + RADIUS][kx + RADIUS] * lum;
            }
        }

        int magnitude = (int) Math.sqrt((double) sumX * sumX + (double) sumY * sumY);
        magnitude = PixelUtils.clampChannel(magnitude);

        int a = PixelUtils.alpha(src[y * width + x]);
        return PixelUtils.argb(a, magnitude, magnitude, magnitude);
    }

    @Override
    public String name() { return "Sobel3x3"; }

    @Override
    public int kernelRadius() { return RADIUS; }
}
