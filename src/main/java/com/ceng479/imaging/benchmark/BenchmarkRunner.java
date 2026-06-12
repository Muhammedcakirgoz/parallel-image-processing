package com.ceng479.imaging.benchmark;

import org.openjdk.jmh.results.format.ResultFormatType;
import org.openjdk.jmh.runner.Runner;
import org.openjdk.jmh.runner.RunnerException;
import org.openjdk.jmh.runner.options.Options;
import org.openjdk.jmh.runner.options.OptionsBuilder;

/**
 * Programmatic JMH launcher. Runs {@link FilterBenchmark} and writes results to
 * both the console and a CSV file ({@code jmh-results.csv}) that can be loaded
 * directly into the report's speedup tables and plotted with Python/matplotlib
 * or any spreadsheet tool.
 *
 * <p>Run with:
 * <pre>
 *   mvn clean package
 *   java -cp target/image-processing.jar com.ceng479.imaging.benchmark.BenchmarkRunner
 * </pre>
 * or
 * <pre>
 *   mvn exec:java -Dexec.mainClass=com.ceng479.imaging.benchmark.BenchmarkRunner
 * </pre>
 */
public final class BenchmarkRunner {

    public static void main(String[] args) throws RunnerException {
        Options opt = new OptionsBuilder()
                .include(FilterBenchmark.class.getSimpleName())
                .resultFormat(ResultFormatType.CSV)
                .result("jmh-results.csv")
                .build();

        System.out.println("Running JMH benchmarks. This will take several minutes...");
        System.out.println("Results will be written to jmh-results.csv\n");

        new Runner(opt).run();

        System.out.println("\nDone. See jmh-results.csv for the raw data.");
        System.out.println("Compute speedup as: speedup = sequential_time / parallel_time");
        System.out.println("(comparing rows with the same size + filter; use threads=1 sequential as baseline).");
    }
}
