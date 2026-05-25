package com.ceng479.imaging.core;

/**
 * Small static helpers shared by all filters. Kept dependency-free and
 * branch-light so the JIT can inline these into the hot per-pixel loops.
 */
public final class PixelUtils {

    private PixelUtils() { } // no instances

    /** Clamp an integer into the inclusive range [min, max]. */
    public static int clamp(int value, int min, int max) {
        if (value < min) return min;
        if (value > max) return max;
        return value;
    }

    /** Clamp a coordinate into [0, limit-1] (edge-extend border handling). */
    public static int clampCoord(int coord, int limit) {
        if (coord < 0) return 0;
        if (coord >= limit) return limit - 1;
        return coord;
    }

    public static int alpha(int argb) { return (argb >>> 24) & 0xFF; }
    public static int red(int argb)   { return (argb >>> 16) & 0xFF; }
    public static int green(int argb) { return (argb >>> 8)  & 0xFF; }
    public static int blue(int argb)  { return argb & 0xFF; }

    /** Pack four 8-bit channels into a single ARGB int. */
    public static int argb(int a, int r, int g, int b) {
        return (a << 24) | (r << 16) | (g << 8) | b;
    }

    /** Clamp a channel value to a valid 0..255 byte before packing. */
    public static int clampChannel(int v) {
        if (v < 0) return 0;
        if (v > 255) return 255;
        return v;
    }
}
