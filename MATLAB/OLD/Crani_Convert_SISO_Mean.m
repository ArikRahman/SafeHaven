% Load rawData
clear;
clc;
fid = fopen('scan3_11-8.bin');  % Open the binary file
data_int = fread(fid, 'uint16'); % Read the binary file as unsigned 16-bit integers
fclose(fid);                     % Close the binary file
inputlength = length(data_int);  % Check length of data

% Configuration parameters
frames = 3060;       % Number of frames
chirps = 1;           % 1 chirp per frame
samples = 512;        % Number of samples per chirp (adjustable)
X = 201;              % Number of positions in X dimension (adjustable)
Y = 30;               % Number of positions in Y dimension (adjustable)
lanes = 4;            % Number of lanes
real_imag = 2;        % Real and imaginary parts

% Calculate the expected configuration length
configLength = frames * samples * chirps * lanes * real_imag;

% Convert data to signed format
data_int = data_int - (data_int >= 2^15) * 2^16;

% Convert data to complex numbers (I + jQ format)
%data = complex(data_int(1:8:end), data_int(5:8:end));
data = zeros(inputlength / 2, 1);
data(1:4:end) = data_int(1:8:end) + sqrt(-1) * data_int(5:8:end);
%data(2:4:end) = data_int(2:8:end) + sqrt(-1) * data_int(6:8:end);
%data(3:4:end) = data_int(3:8:end) + sqrt(-1) * data_int(7:8:end);
%data(4:4:end) = data_int(4:8:end) + sqrt(-1) * data_int(8:8:end);

% Ensure the data length is correct
if length(data) < samples * X * Y
    error('Insufficient data length for the specified configuration.');
end

% Initialize Data Cube with dimensions samples × X × Y
data_new = zeros(samples, X, Y);

% Rearrange data and apply mirroring effect on the X axis
for y = 1:Y
    for x = 1:X
        % Calculate the start and end indices for each block of samples
        startIdx = (y - 1) * samples * X + (x - 1) * samples + 1;
        endIdx = startIdx + samples - 1;

        % Check if endIdx exceeds the length of data
        if endIdx > length(data)
            disp(['Index out of bounds for y=', num2str(y), ' x=', num2str(x)]);
            continue;  % Skip this iteration if index is out of bounds
        end

        % Apply mirroring effect to the X axis
        if rem(y, 2) == 0
            data_new(:, X + 1 - x, y) = data(startIdx:endIdx);
        else
            data_new(:, x, y) = data(startIdx:endIdx);
        end
    end
end

% Save the processed data into rawData
rawData = data_new;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Custom Imaging Portion

% Initialize a new data array for reduced dimensionality
numSlices = ceil(X / 4);  % Calculate the number of slices to store
data_new2 = zeros(samples, numSlices, Y);  % Adjust the size of data_new2 accordingly

% Extract every 4th slice from data_new into data_new2
for y = 1:Y
    for x = 1:4:X
        if x <= X  % Ensure we do not exceed bounds
            data_new2(:, ceil(x / 4), y) = data_new(:, x, y);  % Store every 4th slice
        end
    end
end

% Calculate mean across the Y dimension for averaging
data_chat = mean(data_new2, 3);  % Average over the third dimension (Y)
data_chat = real(data_chat);      % Take the real part
data_chat = abs(data_chat);       % Take the absolute value
data_chat = squeeze(data_chat);   % Remove singleton dimensions

% Define the radius for local averaging
radius = 60; 
filterSize = 2 * radius + 1;

% Create an averaging filter using fspecial
avgFilter = fspecial('average', filterSize);

% Apply the filter to perform local averaging
smoothData = conv2(data_chat, avgFilter, 'same');  % Convolution with the filter
smoothData = rot90(smoothData, -1);                % Rotate the image for correct orientation

% Display the smoothed data
figure;  % Create a new figure window
imagesc(smoothData);  % Display the image
xlabel("X axis");
ylabel("Y axis");
title('Smoothed Image');
colormap('jet');  % Set the colormap to 'jet'
colorbar;        % Display colorbar

% Setting the ticks to go from -200 to 200
xticks(0:50:numSlices);  % Set X ticks based on number of slices
yticks(0:50:Y);          % Set Y ticks
xticklabels(linspace(-20, 20, numel(xticks)));  % Set X tick labels
yticklabels(linspace(-20, 20, numel(yticks)));  % Set Y tick labels

% Additional visualization options (optional)
axis image;  % Maintain aspect ratio
set(gca, 'FontSize', 12);  % Set font size for axes
