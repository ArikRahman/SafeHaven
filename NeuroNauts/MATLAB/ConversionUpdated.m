%% Load rawData3D
fid=fopen('background.bin');    %open the bin file
data_int=fread(fid, 'uint16');  %read the bin file
fclose(fid);                    %close bin file
inputlength=length(data_int);   %check length of data
configLength=2*4*256*1*20000;   %calculate predicted length, 2*#RX*samplesperchirp*chirps*frames
%data_int=data_int(1:4:end); %Parse the data for every 4th value. 
data_int = data_int - (data_int >= 2^15) * 2^16;


%Format data so that I1+Q1 then I2+Q2 etc...
data=zeros(inputlength/2,1);
data(1:4:end) = data_int(1:8:end) + sqrt(-1)*data_int(5:8:end);
data(2:4:end) = data_int(2:8:end) + sqrt(-1)*data_int(6:8:end);
data(3:4:end) = data_int(3:8:end) + sqrt(-1)*data_int(7:8:end);
data(4:4:end) = data_int(4:8:end) + sqrt(-1)*data_int(8:8:end);

%rearange according to the antenna spacing being 1mm
data_new=zeros(256,400,400);
%data=adcData;
for x=1:400
    for y=1:400
        if rem(y,2)==0
            data_new(:,x,y)=data(((401-x)*1024-1023)+mod(y-1,4):4:((401-x)*1024-1023)+mod(y-1,4)+1023);
        else
            data_new(:,x,y)=data((x*1024-1023)+mod(y-1,4):4:(x*1024-1023)+mod(y-1,4)+1023);
        end
    end
end


rawData=data_new;