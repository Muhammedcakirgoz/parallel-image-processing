package com.ceng479.imaging.util;

/**
 * Verifies that two filtered images are pixel-for-pixel identical. Used to
 * prove that the parallel implementations produce exactly the same result as
 * the sequential baseline (correctness is graded at 30%).
 */
public final class CorrectnessVerifier {

    private CorrectnessVerifier() { }

    /**
     * @return the index of the first differing pixel, or -1 if the arrays are
     *         identical in length and content.
     */
    public static int firstDifference(int[] a, int[] b) {
        if (a.length != b.length) {
            return Math.min(a.length, b.length);
        }
        for (int i = 0; i < a.length; i++) {
            if (a[i] != b[i]) return i;
        }
        return -1;
    }

    public static boolean identical(int[] a, int[] b) {
        return firstDifference(a, b) == -1;
    }
}
