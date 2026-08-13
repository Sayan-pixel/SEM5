package LAB2;

import org.knowm.xchart.*;
import org.knowm.xchart.style.lines.SeriesLines;
import java.awt.Color;
import java.io.IOException;

public class Lab2 {

    private static final double C_LIGHT = 3e8; // Speed of Light
    private static final double TX_DBM = 0.0; // Transmitter Power in dBm
    private static final double RX_SENS_DBM = -40.0; // Receiver Sensitivity in dBm
    private static final int SNR_DB = 25; // Signal-to-Noise Ratio in dB
    private static final double CU_ALPHA = 8.0; // Long-haul copper α
    private static final double FI_ALPHA = 0.3; // Fibre α
    private static final double CAT5E_ALPHA_100MHZ = 220.0; // A Cat5e cable operating at 100 MHz has a much higher attenuation, α
    private static final double LAN_BUDGET_DB = 22.0; // link budget

    static class Cable {
        String name;
        double bandwidth;

        Cable(String name, double bandwidth) {
            this.name = name;
            this.bandwidth = bandwidth;
        }
    }

    private static final Cable[] CABLES = {
            new Cable("Cat5e", 100e6),
            new Cable("Cat6", 250e6),
            new Cable("Cat6a", 500e6)
    };

    private static final double[] BANDS = {900e6, 2400e6, 5000e6};

    public static double snrDbToLinear(double snrDb) {
        return Math.pow(10, snrDb / 10.0);
    }

    public static double levelsForRate(double B, double targetRate) {
        return Math.pow(2, targetRate / (2 * B));
    }

    public static double shannonCapacityDb(double B, double snrDb) {
        double snrLinear = snrDbToLinear(snrDb);
        return B * (Math.log(1 + snrLinear) / Math.log(2));
    }

    public static double maxSpanKm(double txDbm, double rxSensDbm, double alphaDbKm) {
        return (txDbm - rxSensDbm) / alphaDbKm;
    }

    public static double fsplDb(double dM, double fHz) {
        return 20 * Math.log10(dM) + 20 * Math.log10(fHz) + 20 * Math.log10(4 * Math.PI / C_LIGHT);
    }

    public static double erfc(double x) {
        double p = 0.3275911;
        double a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741, a4 = -1.453152027, a5 = 1.061405429;
        int sign = 1;
        if (x < 0) { sign = -1; }
        x = Math.abs(x);
        double t = 1.0 / (1.0 + p * x);
        double y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
        return (sign < 0) ? 1.0 + y : 1.0 - y;
    }

    public static double berBpsk(double ebn0Db) {
        double ebn0Linear = Math.pow(10, ebn0Db / 10.0);
        return 0.5 * erfc(Math.sqrt(ebn0Linear));
    }

    public static void generatePlots() throws IOException {
        // Part A plot
        XYChart chartA = new XYChartBuilder().width(800).height(600).title("A").xAxisTitle("SNR (dB)").yAxisTitle("Capacity (Mb/s)").build();
        chartA.getStyler().setDefaultSeriesRenderStyle(XYSeries.XYSeriesRenderStyle.Line);
        chartA.getStyler().setMarkerSize(0);
        
        for (Cable cable : CABLES) {
            double[] xData = new double[200];
            double[] yData = new double[200];
            for(int i=0; i<200; i++) {
                xData[i] = i * 40.0 / 199.0;
                yData[i] = shannonCapacityDb(cable.bandwidth, xData[i]) / 1e6;
            }
            chartA.addSeries(cable.name, xData, yData);
        }
        XYSeries vLineA = chartA.addSeries("SNR_DB", new double[]{25, 25}, new double[]{0, 5000});
        vLineA.setLineColor(Color.GRAY);
        vLineA.setLineStyle(SeriesLines.DASH_DASH);
        BitmapEncoder.saveBitmap(chartA, "partA_java", BitmapEncoder.BitmapFormat.PNG);

        // Part B plot
        XYChart chartB = new XYChartBuilder().width(800).height(600).title("B").xAxisTitle("distance (km)").yAxisTitle("dBm").build();
        chartB.getStyler().setDefaultSeriesRenderStyle(XYSeries.XYSeriesRenderStyle.Line);
        chartB.getStyler().setMarkerSize(0);
        
        double[] xDataB = new double[400];
        double[] yDataBCu = new double[400];
        double[] yDataBFi = new double[400];
        for(int i=0; i<400; i++) {
            double d = 0.01 + i * (60.0 - 0.01) / 399.0;
            xDataB[i] = d;
            yDataBCu[i] = TX_DBM - CU_ALPHA * d;
            yDataBFi[i] = TX_DBM - FI_ALPHA * d;
        }
        chartB.addSeries("copper", xDataB, yDataBCu);
        chartB.addSeries("fibre", xDataB, yDataBFi);
        
        XYSeries hLineB = chartB.addSeries("RX_SENS_DBM", new double[]{0, 60}, new double[]{-40, -40});
        hLineB.setLineColor(Color.GRAY);
        hLineB.setLineStyle(SeriesLines.DASH_DASH);
        BitmapEncoder.saveBitmap(chartB, "partB_java", BitmapEncoder.BitmapFormat.PNG);

        // Part C plot
        XYChart chartC = new XYChartBuilder().width(800).height(600).title("C").xAxisTitle("distance (km)").yAxisTitle("dBm").build();
        chartC.getStyler().setDefaultSeriesRenderStyle(XYSeries.XYSeriesRenderStyle.Line);
        chartC.getStyler().setMarkerSize(0);
        
        double[] xDataC = new double[400];
        for(int i=0; i<400; i++) {
            xDataC[i] = 10 + i * (20000.0 - 10.0) / 399.0;
        }
        for (double f : BANDS) {
            double[] yDataC = new double[400];
            for(int i=0; i<400; i++) {
                yDataC[i] = TX_DBM - fsplDb(xDataC[i], f);
            }
            double[] xDataCKm = new double[400];
            for(int i=0; i<400; i++) xDataCKm[i] = xDataC[i]/1000.0;
            chartC.addSeries(String.format("%.0f MHz", f/1e6), xDataCKm, yDataC);
        }
        BitmapEncoder.saveBitmap(chartC, "partC_java", BitmapEncoder.BitmapFormat.PNG);

        // Part D plot
        XYChart chartD = new XYChartBuilder().width(800).height(600).title("D").xAxisTitle("Eb/N0 (dB)").yAxisTitle("BER").build();
        chartD.getStyler().setDefaultSeriesRenderStyle(XYSeries.XYSeriesRenderStyle.Line);
        chartD.getStyler().setMarkerSize(0);
        chartD.getStyler().setYAxisLogarithmic(true);
        chartD.getStyler().setYAxisMin(1e-10);
        
        double[] xDataD = new double[400];
        double[] yDataD = new double[400];
        for(int i=0; i<400; i++) {
            xDataD[i] = i * 12.0 / 399.0;
            double ber = berBpsk(xDataD[i]);
            yDataD[i] = ber > 0 ? ber : 1e-15; // prevent zero in log plot
        }
        chartD.addSeries("BER", xDataD, yDataD);
        XYSeries hLineD = chartD.addSeries("Target BER", new double[]{0, 12}, new double[]{1e-3, 1e-3});
        hLineD.setLineColor(Color.RED);
        hLineD.setLineStyle(SeriesLines.DASH_DASH);
        BitmapEncoder.saveBitmap(chartD, "partD_java", BitmapEncoder.BitmapFormat.PNG);
        
        System.out.println("Plots successfully generated and saved as PNG files!");
    }

    public static void main(String[] args) throws IOException {
        System.out.println("Part A Bandwidth -> bit rate (SNR = " + SNR_DB + " dB)");
        for (Cable cable : CABLES) {
            System.out.printf("   %s %.1f %f\n", cable.name, levelsForRate(cable.bandwidth, 1e9),
                    shannonCapacityDb(cable.bandwidth, SNR_DB));
        }

        System.out.println("Part B copper/fibre span, Cat5e@100MHz reach:");
        System.out.printf("   %f %f %f\n",
                maxSpanKm(TX_DBM, RX_SENS_DBM, CU_ALPHA),
                maxSpanKm(TX_DBM, RX_SENS_DBM, FI_ALPHA),
                LAN_BUDGET_DB / CAT5E_ALPHA_100MHZ * 1000);

        System.out.println("Part C received power at 5 km per band:");
        for (double f : BANDS) {
            System.out.printf("   %.1f MHz: %f\n", f / 1e6, TX_DBM - fsplDb(5000, f));
        }
        
        System.out.println("Part D BER at 7 dB:");
        System.out.printf("   %f\n", berBpsk(7.0));

        generatePlots();
    }
}
