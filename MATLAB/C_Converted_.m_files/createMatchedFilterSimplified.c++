// 2D SAR Image Reconstruction .m to C conversion

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define LIGHT_SPEED 299792458.0 // speed of light in m/s

// Function to create matched filter
// Inputs:
//   xPointM: number of measurement points at x (horizontal) axis
//   xStepM: Sampling distance at x (horizontal) axis in mm
//   yPointM: number of measurement points at y (vertical) axis
//   yStepM: Sampling distance at y (vertical) axis in mm
//   zTarget: z distance of target in mm
// Outputs:
//   matchedFilter: pointer to array of complex double of size xPointM * yPointM
//                 representing the matched filter values
// Note: The caller is responsible for freeing the returned array.
complex double* createMatchedFilterSimplified(int xPointM, double xStepM, int yPointM, double yStepM, double zTarget) {
    const double f0 = 77e9; // start frequency in Hz
    const double c = LIGHT_SPEED; // speed of light in m/s

    // Allocate memory for matched filter
    complex double* matchedFilter = (complex double*)malloc(xPointM * yPointM * sizeof(complex double));
    if (matchedFilter == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    // Create x and y coordinate arrays (in meters)
    double* x = (double*)malloc(xPointM * sizeof(double));
    double* y = (double*)malloc(yPointM * sizeof(double));
    if (x == NULL || y == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        free(matchedFilter);
        free(x);
        free(y);
        return NULL;
    }

    // Fill x coordinates: xStepM is in mm, convert to meters
    for (int i = 0; i < xPointM; i++) {
        x[i] = xStepM * ( (double)i - (double)(xPointM - 1) / 2.0 ) * 1e-3;
    }

    // Fill y coordinates: yStepM is in mm, convert to meters
    for (int j = 0; j < yPointM; j++) {
        y[j] = yStepM * ( (double)j - (double)(yPointM - 1) / 2.0 ) * 1e-3;
    }

    // Target location in meters
    double z0 = zTarget * 1e-3;

    // Wave number k
    double k = 2.0 * M_PI * f0 / c;

    // Compute matched filter values
    // matchedFilter is stored in row-major order: y index changes faster
    for (int ix = 0; ix < xPointM; ix++) {
        for (int iy = 0; iy < yPointM; iy++) {
            double r = sqrt(x[ix]*x[ix] + y[iy]*y[iy] + z0*z0);
            double phase = -2.0 * k * r;
            matchedFilter[ix * yPointM + iy] = cexp(I * phase);
        }
    }

    free(x);
    free(y);

    return matchedFilter;
}