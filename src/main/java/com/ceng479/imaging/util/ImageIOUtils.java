package com.ceng479.imaging.util;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.Random;

/**
 * Helpers for loading/saving images and for generating reproducible synthetic
 * test images when no real input file is available.
 */
public final class ImageIOUtils {

    private ImageIOUtils() { }

    /** Loads an image file into a row-major ARGB int array. */
    public static ImageData load(String path) throws IOException {
        BufferedImage img = ImageIO.read(new File(path));
        if (img == null) {
            throw new IOException("Unsupported or unreadable image: " + path);
        }
        int w = img.getWidth();
        int h = img.getHeight();
        int[] pixels = img.getRGB(0, 0, w, h, null, 0, w);
        return new ImageData(pixels, w, h);
    }

    /** Saves a row-major ARGB int array as a PNG file. */
    public static void savePng(int[] pixels, int width, int height, String path) throws IOException {
        BufferedImage img = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
        img.setRGB(0, 0, width, height, pixels, 0, width);
        File out = new File(path);
        if (out.getParentFile() != null) {
            out.getParentFile().mkdirs();
        }
        ImageIO.write(img, "png", out);
    }

    /**
     * Generates a deterministic synthetic image with smooth gradients plus
     * pseudo-random noise. Useful as a stand-in benchmark input that exercises
     * every pixel without requiring an external file. The fixed seed makes runs
     * reproducible.
     */
    public static ImageData generateSynthetic(int width, int height, long seed) {
        int[] pixels = new int[width * height];
        Random rng = new Random(seed);
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int r = (x * 255) / width;
                int g = (y * 255) / height;
                int b = ((x + y) * 255) / (width + height);
                // add a little noise so edge filters have something to detect
                int noise = rng.nextInt(32) - 16;
                r = clamp(r + noise);
                g = clamp(g + noise);
                b = clamp(b + noise);
                pixels[y * width + x] = (0xFF << 24) | (r << 16) | (g << 8) | b;
            }
        }
        return new ImageData(pixels, width, height);
    }

    private static int clamp(int v) {
        if (v < 0) return 0;
        if (v > 255) return 255;
        return v;
    }

    /** Simple value holder for pixel data plus dimensions. */
    public static final class ImageData {
        public final int[] pixels;
        public final int width;
        public final int height;

        public ImageData(int[] pixels, int width, int height) {
            this.pixels = pixels;
            this.width = width;
            this.height = height;
        }
    }
}
