function rawData = loadDataCube(filename, samples, X, Y, option)
    % loadDataCube Function to load binary data and format into a 3D data cube.
    %
    % Inputs:
    %   filename - Name of the binary file
    %   samples  - Number of samples per chirp (changeable)
    %   X        - Number of X positions (changeable)
    %   Y        - Number of Y positions (changeable)
    %   option   - Option for choosing radar reciever 1-4
    %
    % Output:
    %   rawData  - Formatted 3D data cube

    % Load raw data from the binary file
    fid = fopen(filename, 'r');
    data_int = fread(fid, 'int16');
    fclose(fid);

    % Define parameters
    chunk_size = samples * 4;
    inputlength = length(data_int);

    % Format data as I1+Q1, I2+Q2, etc.
    bindata = zeros(inputlength / 2, 1);
    bindata(1:4:end) = data_int(1:8:end) + 1i * data_int(5:8:end);
    bindata(2:4:end) = data_int(2:8:end) + 1i * data_int(6:8:end);
    bindata(3:4:end) = data_int(3:8:end) + 1i * data_int(7:8:end);
    bindata(4:4:end) = data_int(4:8:end) + 1i * data_int(8:8:end);

    % Initialize the data_cube array
    data_cube = zeros(samples, Y, X);

    % Populate data_cube based on the selected option
    for y = 1:Y
        for x = 1:X
            start_idx = ((x - 1) * chunk_size) + 1;
            end_idx = start_idx + chunk_size - 1;
            
            switch option
                case 1
                    slice = bindata(start_idx:4:end_idx);
                case 2
                    slice = bindata(start_idx+1:4:end_idx);
                case 3
                    slice = bindata(start_idx+2:4:end_idx);
                case 4
                    slice = bindata(start_idx+3:4:end_idx);
                case 5
                    avg_slice = (bindata(start_idx:4:end_idx) + ...
                                 bindata(start_idx+1:4:end_idx) + ...
                                 bindata(start_idx+2:4:end_idx) + ...
                                 bindata(start_idx+3:4:end_idx)) / 4;
                    slice = avg_slice;
                otherwise
                    error('Invalid option: %d', option)
            end
            
            % Assign to data_cube with even/odd y handling
            if rem(y, 2) == 1
                data_cube(:, y, x) = slice * w;
            else
                data_cube(:, y, X + 1 - x) = slice * w;
            end
        end
    end

    % Output the final formatted data
    rawData = data_cube;
end
