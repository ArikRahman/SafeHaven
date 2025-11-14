// 2D SAR Image Reconstruction .m to C conversion

// Converted with CodeConvert.AI
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI 3.14159265358979323846

// Constants
const double c = 299792458.0; // speed of light (m/s)
const double fS = 9121e3;     // Sampling rate (sps)
const double Ts = 1.0 / fS;   // Sampling period
const double K = 63.343e12;   // Slope const (Hz/sec)

// Function prototypes
void stack(int nsamples, int nX, int nY, int dummy, double ***rawData);
void fft(double complex *in, double complex *out, int n);
void createMatchedFilterSimplified(int nFFTspaceX, double dx, int nFFTspaceY, double dy, double z0_mm, double complex **matchedFilter);
void reconstructSARimageMatchedFilterSimplified(double complex **sarData, double complex **matchedFilter, double dx, double dy, int imSize, double **sarImage);

int main() {
    // Parameters
    int nsamples = 512;
    int nX = 400;
    int nY = 40;
    int nFFTtime = 1024;
    double z0 = 323e-3; // meters
    double dx = 290.0 / 400.0 * 1e-3; // convert mm to meters
    double dy = 205.0 / 100.0 * 1e-3; // convert mm to meters
    int nFFTspace = 1024;
    double tI = 4.5225e-10; // Instrument delay for range calibration

    // Allocate rawData 3D array: rawData[nsamples][nX][nY]
    double ***rawData = (double ***)malloc(nsamples * sizeof(double **));
    for (int i = 0; i < nsamples; i++) {
        rawData[i] = (double **)malloc(nX * sizeof(double *));
        for (int j = 0; j < nX; j++) {
            rawData[i][j] = (double *)malloc(nY * sizeof(double));
        }
    }

    // Load or generate rawData using stack function (dummy here)
    stack(nsamples, nX, nY, 1, rawData);

    // Perform FFT along the first dimension (nsamples) for each (x,y)
    // rawDataFFT will be complex: [nFFTtime][nX][nY]
    double complex ***rawDataFFT = (double complex ***)malloc(nFFTtime * sizeof(double complex **));
    for (int k = 0; k < nFFTtime; k++) {
        rawDataFFT[k] = (double complex **)malloc(nX * sizeof(double complex *));
        for (int i = 0; i < nX; i++) {
            rawDataFFT[k][i] = (double complex *)malloc(nY * sizeof(double complex));
        }
    }

    // Temporary arrays for FFT input and output
    double complex *fft_in = (double complex *)malloc(nFFTtime * sizeof(double complex));
    double complex *fft_out = (double complex *)malloc(nFFTtime * sizeof(double complex));

    for (int x = 0; x < nX; x++) {
        for (int y = 0; y < nY; y++) {
            // Prepare input for FFT (zero-pad if nsamples < nFFTtime)
            for (int t = 0; t < nsamples; t++) {
                fft_in[t] = rawData[t][x][y] + 0.0 * I;
            }
            for (int t = nsamples; t < nFFTtime; t++) {
                fft_in[t] = 0.0 + 0.0 * I;
            }
            fft(fft_in, fft_out, nFFTtime);
            for (int k = 0; k < nFFTtime; k++) {
                rawDataFFT[k][x][y] = fft_out[k];
            }
        }
    }

    // Calculate range bin k
    int k = (int)round(K * Ts * (2.0 * z0 / c + tI) * nFFTtime);

    // Extract sarData slice at range bin k: sarData[nX][nY]
    double complex **sarData = (double complex **)malloc(nX * sizeof(double complex *));
    for (int i = 0; i < nX; i++) {
        sarData[i] = (double complex *)malloc(nY * sizeof(double complex));
        for (int j = 0; j < nY; j++) {
            sarData[i][j] = rawDataFFT[k][i][j];
        }
    }

    // Create matched filter
    double complex **matchedFilter = (double complex **)malloc(nFFTspace * sizeof(double complex *));
    for (int i = 0; i < nFFTspace; i++) {
        matchedFilter[i] = (double complex *)malloc(nFFTspace * sizeof(double complex));
    }
    createMatchedFilterSimplified(nFFTspace, dx, nFFTspace, dy, z0 * 1e3, matchedFilter);

    // Create SAR image
    int imSize = 200; // mm
    double **sarImage = (double **)malloc(imSize * sizeof(double *));
    for (int i = 0; i < imSize; i++) {
        sarImage[i] = (double *)malloc(imSize * sizeof(double));
    }
    reconstructSARimageMatchedFilterSimplified(sarData, matchedFilter, dx, dy, imSize, sarImage);

    // Free allocated memory (not shown for brevity)

    free(fft_in);
    free(fft_out);

    // Free rawData
    for (int i = 0; i < nsamples; i++) {
        for (int j = 0; j < nX; j++) {
            free(rawData[i][j]);
        }
        free(rawData[i]);
    }
    free(rawData);

    // Free rawDataFFT
    for (int k = 0; k < nFFTtime; k++) {
        for (int i = 0; i < nX; i++) {
            free(rawDataFFT[k][i]);
        }
        free(rawDataFFT[k]);
    }
    free(rawDataFFT);

    // Free sarData
    for (int i = 0; i < nX; i++) {
        free(sarData[i]);
    }
    free(sarData);

    // Free matchedFilter
    for (int i = 0; i < nFFTspace; i++) {
        free(matchedFilter[i]);
    }
    free(matchedFilter);

    // Free sarImage
    for (int i = 0; i < imSize; i++) {
        free(sarImage[i]);
    }
    free(sarImage);

    return 0;
}

// Dummy stack function to fill rawData with some values
void stack(int nsamples, int nX, int nY, int dummy, double ***rawData) {
    for (int t = 0; t < nsamples; t++) {
        for (int x = 0; x < nX; x++) {
            for (int y = 0; y < nY; y++) {
                rawData[t][x][y] = sin(2 * PI * t / nsamples) * cos(2 * PI * x / nX) * cos(2 * PI * y / nY);
            }
        }
    }
}

// Simple FFT implementation (Cooley-Tukey radix-2)
// Assumes n is a power of 2
void fft(double complex *in, double complex *out, int n) {
    if (n == 1) {
        out[0] = in[0];
        return;
    }

    int half = n / 2;
    double complex *even = (double complex *)malloc(half * sizeof(double complex));
    double complex *odd = (double complex *)malloc(half * sizeof(double complex));
    double complex *even_fft = (double complex *)malloc(half * sizeof(double complex));
    double complex *odd_fft = (double complex *)malloc(half * sizeof(double complex));

    for (int i = 0; i < half; i++) {
        even[i] = in[2 * i];
        odd[i] = in[2 * i + 1];
    }

    fft(even, even_fft, half);
    fft(odd, odd_fft, half);

    for (int k = 0; k < half; k++) {
        double complex t = cexp(-I * 2.0 * PI * k / n) * odd_fft[k];
        out[k] = even_fft[k] + t;
        out[k + half] = even_fft[k] - t;
    }

    free(even);
    free(odd);
    free(even_fft);
    free(odd_fft);
}

// Placeholder for matched filter creation
void createMatchedFilterSimplified(int nFFTspaceX, double dx, int nFFTspaceY, double dy, double z0_mm, double complex **matchedFilter) {
    // This function should create a matched filter based on parameters.
    // Here we fill with dummy values for demonstration.

// Converted manually
/*

*/