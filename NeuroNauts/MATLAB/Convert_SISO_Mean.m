%% Load rawData
clear;
clc;
fid=fopen('FinalDemo.bin');    %open the bin file
data_int=fread(fid, 'uint16');  %read the bin file
fclose(fid);                    %close bin file
inputlength=length(data_int);   %check length of data
frames=40000;
chirps=1;
samples=256;
lanes=4;
real_imag=2;
configLength=frames*samples*chirps*lanes*real_imag;   %calculate predicted length, 2*#RX*samplesperchirp*chirps*frames
%data_int=data_int(1:4:end); %Parse the data for every 4th value. 
data_int = data_int - (data_int >= 2^15) * 2^16;


%Format data so that I1+Q1 then I2+Q2 etc...
data=zeros(inputlength/8,1);
data(1:1:end) = data_int(1:8:end) + sqrt(-1)*data_int(5:8:end);


%Initialize Data Cube
data_new = zeros(256, 100, 400);
for x = 1:100
    for y = 1:400
        startIdx = (x-1)*102400 + (y-1)*256 + 1;
        endIdx = startIdx + 255;  % 256 elements from startIdx

        % Check if endIdx exceeds the length of data
        if endIdx > length(data)
            disp(['Index out of bounds for x=', num2str(x), ' y=', num2str(y)]);
            continue;  % Skip this iteration if index is out of bounds
        end

        if rem(x, 2) == 0
            data_new(:, x, 401-y) = data(startIdx:endIdx);
        else
            data_new(:, x, y) = data(startIdx:endIdx);
        end
    end
end

rawData=data_new;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Custom Imaging portion

data_new2=zeros(256,100,400);
data_new2(:,1:4:400,:)=data_new(:,:,:);


data_chat = mean(data_new2);
data_chat=real(data_chat);
data_chat=abs(data_chat);
data_chat=squeeze(data_chat);
% Define the radius for local averaging
radius = 60; 


filterSize = 2 * radius + 1;
avgFilter = fspecial('average', filterSize);

% Apply the filter to perform local averaging
smoothData = conv2(data_chat, avgFilter, 'same');
smoothData=rot90(smoothData,-1);

imagesc(smoothData);
xlabel("X axis")
colormap('jet'); 
colorbar;
axis image;

% Setting the ticks to go from -200 to 200
xticks(0:50:400);
yticks(0:50:400);
xticklabels(-200:50:200);
yticklabels(-200:50:200);

% Adding labels (optional)
xlabel('X Axis');
ylabel('Y Axis');
title('Image');

