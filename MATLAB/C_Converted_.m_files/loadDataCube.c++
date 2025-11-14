// 2D SAR Image Reconstruction .m to C conversion

#include <stdio.h>
#include <stdlib.h>
#include <complex.h>

complex double*** loadDataCube(const char* filename, int samples, int X, int Y, int option) {
    // Open file
    FILE* fid = fopen(filename, "rb");
    if (!fid) {
        perror("Failed to open file");
        return NULL;
    }

    // Get file size
    fseek(fid, 0, SEEK_END);
    long file_size = ftell(fid);
    fseek(fid, 0, SEEK_SET);

    // Number of int16 elements
    long num_int16 = file_size / sizeof(short);

    // Read data_int
    short* data_int = (short*)malloc(file_size);
    if (!data_int) {
        perror("Memory allocation failed");
        fclose(fid);
        return NULL;
    }
    fread(data_int, sizeof(short), num_int16, fid);
    fclose(fid);

    // Parameters
    int chunk_size = samples * 4;
    long inputlength = num_int16;

    // Allocate bindata (complex double array)
    long bindata_len = inputlength / 2;
    complex double* bindata = (complex double*)calloc(bindata_len, sizeof(complex double));
    if (!bindata) {
        perror("Memory allocation failed");
        free(data_int);
        return NULL;
    }

    // Format data as I1+Q1, I2+Q2, etc.
    // bindata(1:4:end) = data_int(1:8:end) + 1i * data_int(5:8:end);
    // bindata(2:4:end) = data_int(2:8:end) + 1i * data_int(6:8:end);
    // bindata(3:4:end) = data_int(3:8:end) + 1i * data_int(7:8:end);
    // bindata(4:4:end) = data_int(4:8:end) + 1i * data_int(8:8:end);

    for (long i = 0; i < bindata_len / 4; i++) {
        bindata[4*i + 0] = (complex double)(data_int[8*i + 0]) + (complex double)(data_int[8*i + 4]) * I;
        bindata[4*i + 1] = (complex double)(data_int[8*i + 1]) + (complex double)(data_int[8*i + 5]) * I;
        bindata[4*i + 2] = (complex double)(data_int[8*i + 2]) + (complex double)(data_int[8*i + 6]) * I;
        bindata[4*i + 3] = (complex double)(data_int[8*i + 3]) + (complex double)(data_int[8*i + 7]) * I;
    }

    free(data_int);

    // Allocate data_cube: samples x Y x X
    // data_cube[samples][Y][X]
    complex double*** data_cube = (complex double***)malloc(samples * sizeof(complex double**));
    if (!data_cube) {
        perror("Memory allocation failed");
        free(bindata);
        return NULL;
    }
    for (int s = 0; s < samples; s++) {
        data_cube[s] = (complex double**)malloc(Y * sizeof(complex double*));
        if (!data_cube[s]) {
            perror("Memory allocation failed");
            for (int k = 0; k < s; k++) free(data_cube[k]);
            free(data_cube);
            free(bindata);
            return NULL;
        }
        for (int y = 0; y < Y; y++) {
            data_cube[s][y] = (complex double*)calloc(X, sizeof(complex double));
            if (!data_cube[s][y]) {
                perror("Memory allocation failed");
                for (int m = 0; m <= y; m++) free(data_cube[s][m]);
                for (int k = 0; k < s; k++) {
                    for (int m = 0; m < Y; m++) free(data_cube[k][m]);
                    free(data_cube[k]);
                }
                free(data_cube);
                free(bindata);
                return NULL;
            }
        }
    }

    // w is not defined in Matlab code, assuming w = 1.0
    complex double w = 1.0 + 0.0 * I;

    // Populate data_cube based on option
    for (int y = 0; y < Y; y++) {
        for (int x = 0; x < X; x++) {
            int start_idx = x * chunk_size;
            int end_idx = start_idx + chunk_size - 1;

            // slice length = samples
            complex double* slice = (complex double*)malloc(samples * sizeof(complex double));
            if (!slice) {
                perror("Memory allocation failed");
                // Free data_cube and bindata before return
                for (int s = 0; s < samples; s++) {
                    for (int yy = 0; yy < Y; yy++) free(data_cube[s][yy]);
                    free(data_cube[s]);
                }
                free(data_cube);
                free(bindata);
                return NULL;
            }

            switch (option) {
                case 1:
                    for (int i = 0; i < samples; i++) {
                        slice[i] = bindata[start_idx + 4*i];
                    }
                    break;
                case 2:
                    for (int i = 0; i < samples; i++) {
                        slice[i] = bindata[start_idx + 1 + 4*i];
                    }
                    break;
                case 3:
                    for (int i = 0; i < samples; i++) {
                        slice[i] = bindata[start_idx + 2 + 4*i];
                    }
                    break;
                case 4:
                    for (int i = 0; i < samples; i++) {
                        slice[i] = bindata[start_idx + 3 + 4*i];
                    }
                    break;
                case 5:
                    for (int i = 0; i < samples; i++) {
                        slice[i] = (bindata[start_idx + 4*i] +
                                    bindata[start_idx + 1 + 4*i] +
                                    bindata[start_idx + 2 + 4*i] +
                                    bindata[start_idx + 3 + 4*i]) / 4.0;
                    }
                    break;
                default:
                    fprintf(stderr, "Invalid option: %d\n", option);
                    free(slice);
                    for (int s = 0; s < samples; s++) {
                        for (int yy = 0; yy < Y; yy++) free(data_cube[s][yy]);
                        free(data_cube[s]);
                    }
                    free(data_cube);
                    free(bindata);
                    return NULL;
            }

            // Assign to data_cube with even/odd y handling
            if ((y + 1) % 2 == 1) { // odd y in Matlab (1-based)
                for (int s = 0; s < samples; s++) {
                    data_cube[s][y][x] = slice[s] * w;
                }
            } else { // even y
                for (int s = 0; s < samples; s++) {
                    data_cube[s][y][X - 1 - x] = slice[s] * w;
                }
            }

            free(slice);
        }
    }

    free(bindata);

    return data_cube;
}