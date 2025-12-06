-- SAR Data Capture Script for IWR1443
-- Matching Python Params: 512 samples, 400 chirps, 9.121 Msps, 63.343 MHz/us

-- 1. Reset and Select Device
ar1.FullReset()
ar1.SOPControl(2)
ar1.Connect(1,921600,1000)

-- 2. Basic Device Config (Standard IWR1443 boilerplate)
ar1.Calling_IsConnected()
ar1.SelectCaptureDevice("DCA1000")
ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098)
ar1.CaptureCardConfig_Mode(1, 1, 1, 2, 3, 30)
ar1.CaptureCardConfig_PacketDelay(25)

-- 3. Master/Channel Config
ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 1, 0)
ar1.LPModConfig(0, 0)
ar1.RfInit()

-- 4. Data Format Config
--    adcBits=2 (16-bit), adcFormat=1 (Complex), lanes=2 (2 Lanes)
ar1.DataFmtConfig_Multimode(0, 1, 2, 1, 2)
ar1.DataPathConfig(513, 121, 0)
ar1.LvdsClkConfig(1, 1)
ar1.LvdsLaneConfig(0, 1, 1, 0, 0, 1, 0, 0)

-- 5. Profile Config (CRITICAL SECTION)
--    ProfileId = 0
--    StartFreq = 77.0 GHz
--    IdleTime = 7 us
--    AdcStartTime = 6 us
--    RampEndTime = 65 us (Must be > 56.13us calculated from 512/9121)
--    TxPower = 0, 0, 0
--    Slope = 63.343 MHz/us
--    TxStartTime = 1 us
--    AdcSamples = 512
--    SampleRate = 9121 ksps
--    HpfCornerFreq1 = 0, HpfCornerFreq2 = 0, RxGain = 30
ar1.ProfileConfig(0, 77, 7, 6, 65, 0, 0, 0, 0, 0, 0, 63.343, 0, 512, 9121, 0, 0, 30)

-- 6. Chirp Config
--    Start/End Index = 0. Use Profile 0. Enable Tx1 (1).
ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0)

-- 7. Frame Config
--    Chirps 0 to 0.
--    NumFrames = 1
--    NumChirps (Loops) = 400 (This matches X in your Python)
--    Periodicity = 40 ms (Adjust as needed for duty cycle)
--    Trigger = 1 (Software Trigger)
ar1.FrameConfig(0, 0, 1, 400, 40, 1, 0, 1)

-- 8. Start Record
--    CHANGE THE FILENAME BELOW FOR EACH GANTRY POSITION (scan0, scan1, etc.)
ar1.CaptureCardConfig_StartRecord("C:\\ti\\mmwave_studio_02_01_01_00\\mmWaveStudio\\PostProc\\scan0_Raw_0.bin", 1)
ar1.StartFrame()

-- 9. Wait and Stop (Optional, mainly for automation)
-- RSTD.Sleep(2000)
-- ar1.CaptureCardConfig_StopRecord()
