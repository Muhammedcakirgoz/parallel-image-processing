package com.ceng479.imaging.filters;

import com.ceng479.imaging.core.Filter;
import com.ceng479.imaging.core.PixelUtils;

/**
 * Converts each pixel to grayscale using the ITU-R BT.601 luma formula:
 * Y = 0.299*R + 0.587*G + 0.114*B.
 *
 * <p>This is a purely point-wise operation: the output of a pixel depends only
 * on that same pixel's input, with no neighborhood. It therefore has
 * kernelRadius 0 and is the cleanest example of "embarrassing parallelism".
 */
public final class GrayscaleFilter implements Filter {

    @Override
    public int applyPixel(int[] src, int width, int height, int x, int y) {
        int argb = src[y * width + x];
        int a = PixelUtils.alpha(argb);
        int r = PixelUtils.red(argb);
        int g = PixelUtils.green(argb);
        int b = PixelUtils.blue(argb);

        // Integer approximation of the BT.601 luma weights (scaled by 1000).
        int luma = (299 * r + 587 * g + 114 * b) / 1000;
        luma = PixelUtils.clampChannel(luma);

        return PixelUtils.argb(a, luma, luma, luma);
    }

    @Override
    public String name() { return "Grayscale"; }

    @Override
    public int kernelRadius() { return 0; }
}
