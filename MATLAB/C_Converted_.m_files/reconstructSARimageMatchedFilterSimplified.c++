// 2D SAR Image Reconstruction .m to C conversion

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <fftw3.h>

// Helper function to pad a 2D array with zeros
double complex** padarray(double complex** input, int rows, int cols, int padTop, int padBottom, int padLeft, int padRight) {
    int newRows = rows + padTop + padBottom;
    int newCols = cols + padLeft + padRight;

    double complex** output = (double complex**)malloc(newRows * sizeof(double complex*));
    for (int i = 0; i < newRows; i++) {
        output[i] = (double complex*)calloc(newCols, sizeof(double complex));
    }

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            output[i + padTop][j + padLeft] = input[i][j];
        }
    }

    return output;
}

// Helper function to free 2D complex array
void free_2d_complex(double complex** arr, int rows) {
    for (int i = 0; i < rows; i++) {
        free(arr[i]);
    }
    free(arr);
}

// Helper function to create 2D complex array
double complex** create_2d_complex(int rows, int cols) {
    double complex** arr = (double complex**)malloc(rows * sizeof(double complex*));
    for (int i = 0; i < rows; i++) {
        arr[i] = (double complex*)calloc(cols, sizeof(double complex));
    }
    return arr;
}

// Helper function to copy 2D complex array
double complex** copy_2d_complex(double complex** src, int rows, int cols) {
    double complex** dest = create_2d_complex(rows, cols);
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            dest[i][j] = src[i][j];
    return dest;
}

// Helper function to multiply element-wise two 2D complex arrays
void multiply_2d_complex(double complex** a, double complex** b, double complex** result, int rows, int cols) {
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            result[i][j] = a[i][j] * b[i][j];
}

// Helper function to fftshift a 2D complex array
void fftshift_2d(double complex** data, int rows, int cols) {
    int halfRows = rows / 2;
    int halfCols = cols / 2;

    // Swap quadrants
    for (int i = 0; i < halfRows; i++) {
        for (int j = 0; j < halfCols; j++) {
            // Top-left <-> Bottom-right
            double complex temp = data[i][j];
            data[i][j] = data[i + halfRows + (rows % 2)][j + halfCols + (cols % 2)];
            data[i + halfRows + (rows % 2)][j + halfCols + (cols % 2)] = temp;

            // Top-right <-> Bottom-left
            temp = data[i][j + halfCols + (cols % 2)];
            data[i][j + halfCols + (cols % 2)] = data[i + halfRows + (rows % 2)][j];
            data[i + halfRows + (rows % 2)][j] = temp;
        }
    }
}

// Main function to reconstruct SAR image
double complex** reconstructSARimageMatchedFilterSimplified(
    double complex** sarData, int sarRows, int sarCols,
    double complex** matchedFilter, int mfRows, int mfCols,
    double xStepM, double yStepM, double xySizeT,
    int* outRows, int* outCols)
{
    // Equalize Dimensions of sarData and Matched Filter with Zero Padding
    int padLeft, padRight, padTop, padBottom;
    double complex** sarDataPadded = NULL;
    double complex** matchedFilterPadded = NULL;

    // Pad horizontally
    if (mfCols > sarCols) {
        int diff = mfCols - sarCols;
        padLeft = diff / 2;
        padRight = diff - padLeft;
        sarDataPadded = padarray(sarData, sarRows, sarCols, 0, 0, padLeft, padRight);
        matchedFilterPadded = copy_2d_complex(matchedFilter, mfRows, mfCols);
    } else {
        int diff = sarCols - mfCols;
        padLeft = diff / 2;
        padRight = diff - padLeft;
        matchedFilterPadded = padarray(matchedFilter, mfRows, mfCols, 0, 0, padLeft, padRight);
        sarDataPadded = copy_2d_complex(sarData, sarRows, sarCols);
    }

    int paddedCols = (mfCols > sarCols) ? mfCols : sarCols;
    int paddedRows;

    // Pad vertically
    if (mfRows > sarRows) {
        int diff = mfRows - sarRows;
        padTop = diff / 2;
        padBottom = diff - padTop;
        double complex** sarDataPaddedVert = padarray(sarDataPadded, sarRows, paddedCols, padTop, padBottom, 0, 0);
        free_2d_complex(sarDataPadded, sarRows + 0); // free old sarDataPadded
        sarDataPadded = sarDataPaddedVert;
        paddedRows = mfRows;

        matchedFilterPadded = copy_2d_complex(matchedFilterPadded, mfRows, paddedCols);
    } else {
        int diff = sarRows - mfRows;
        padTop = diff / 2;
        padBottom = diff - padTop;
        double complex** matchedFilterPaddedVert = padarray(matchedFilterPadded, mfRows, paddedCols, padTop, padBottom, 0, 0);
        free_2d_complex(matchedFilterPadded, mfRows);
        matchedFilterPadded = matchedFilterPaddedVert;
        paddedRows = sarRows;

        sarDataPadded = copy_2d_complex(sarDataPadded, paddedRows, paddedCols);
    }

    // Now paddedRows and paddedCols are the dimensions of both arrays
    // Prepare FFTW arrays
    fftw_complex *in1 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * paddedRows * paddedCols);
    fftw_complex *in2 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * paddedRows * paddedCols);
    fftw_complex *out1 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * paddedRows * paddedCols);
    fftw_complex *out2 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * paddedRows * paddedCols);
    fftw_complex *product = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * paddedRows * paddedCols);
    fftw_complex *ifft_out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * paddedRows * paddedCols);

    // Copy data to fftw input arrays
    for (int i = 0; i < paddedRows; i++) {
        for (int j = 0; j < paddedCols; j++) {
            int idx = i * paddedCols + j;
            in1[idx][0] = creal(sarDataPadded[i][j]);
            in1[idx][1] = cimag(sarDataPadded[i][j]);
            in2[idx][0] = creal(matchedFilterPadded[i][j]);
            in2[idx][1] = cimag(matchedFilterPadded[i][j]);
        }
    }

    // Create FFT plans
    fftw_plan plan_forward1 = fftw_plan_dft_2d(paddedRows, paddedCols, in1, out1, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_plan plan_forward2 = fftw_plan_dft_2d(paddedRows, paddedCols, in2, out2, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_plan plan_backward = fftw_plan_dft_2d(paddedRows, paddedCols, product, ifft_out, FFTW_BACKWARD, FFTW_ESTIMATE);

    // Execute FFTs
    fftw_execute(plan_forward1);
    fftw_execute(plan_forward2);

    // Multiply element-wise in frequency domain
    for (int i = 0; i < paddedRows * paddedCols; i++) {
        double a_real = out1[i][0];
        double a_imag = out1[i][1];
        double b_real = out2[i][0];
        double b_imag = out2[i][1];
        // (a_real + i a_imag) * (b_real + i b_imag)
        product[i][0] = a_real * b_real - a_imag * b_imag;
        product[i][1] = a_real * b_imag + a_imag * b_real;
    }

    // Inverse FFT
    fftw_execute(plan_backward