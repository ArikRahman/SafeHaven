function rawData = stack(samples, X, Y)
    % Initialize a 3D array to store the stacked data cubes
    dataStack = zeros(samples, Y, X);
    
    % Load data cubes and stack them along the Y dimension
    for y = 1:Y
        filename = "scan" + y + "_Raw_0.bin";
        dataStack(:, y, :) = loadDataCube(filename, samples, X, 1);
    end
    
    % `dataStack` now contains the Y slices stacked along the second dimension (Y)
    rawData = dataStack;
end