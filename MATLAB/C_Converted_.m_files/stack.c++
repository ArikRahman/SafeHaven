// Converted with CodeConvert.AI

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Assuming loadDataCube is defined elsewhere with this signature:
// void loadDataCube(const char* filename, int samples, int X, int flag, float* buffer);

void stack(int samples, int X, int Y, float* rawData) {
    // Allocate memory for dataStack: samples * Y * X
    // rawData is expected to be pre-allocated with size samples * Y * X
    float* dataStack = rawData;

    for (int y = 0; y < Y; y++) {
        char filename[256];
        snprintf(filename, sizeof(filename), "scan%d_Raw_0.bin", y + 1);

        // Temporary buffer to hold one slice of size samples * X
        float* tempBuffer = (float*)malloc(samples * X * sizeof(float));
        if (!tempBuffer) {
            fprintf(stderr, "Memory allocation failed\n");
            exit(EXIT_FAILURE);
        }

        // Load data cube slice
        loadDataCube(filename, samples, X, 1, tempBuffer);

        // Copy tempBuffer into dataStack at position y (second dimension)
        // dataStack is stored in row-major order: samples x Y x X
        // Indexing: dataStack[sample * (Y*X) + y * X + x]
        for (int sample = 0; sample < samples; sample++) {
            for (int x = 0; x < X; x++) {
                dataStack[sample * (Y * X) + y * X + x] = tempBuffer[sample * X + x];
            }
        }

        free(tempBuffer);
    }
}