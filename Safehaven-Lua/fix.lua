-- 1. Configure Chirp 0 (Tx1 Only)
-- Syntax: ChirpConfig(StartIdx, EndIdx, ProfileId, StartFreqVar, FreqSlopeVar, IdleTimeVar, AdcStartTimeVar, TxEnable, ...)
-- TxEnable = 1 (Binary 001) enables Tx1
ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0)

-- 2. Configure Chirp 1 (Tx2 Only)
-- TxEnable = 2 (Binary 010) enables Tx2. Use 4 for Tx3.
ar1.ChirpConfig(1, 1, 0, 0, 0, 0, 0, 2, 0, 0)

-- 3. Update Frame Config to capture BOTH chirps
-- Syntax: FrameConfig(StartChirp, EndChirp, NumFrames, NumLoops, Periodicity, Trigger, Delay)
-- We change Start=0 and End=1
ar1.FrameConfig(0, 1, 400, 1, 8, 0, 512, 1)

-- 4. Re-select device and start sensor (Standard sequence)
ar1.SelectCaptureDevice("DCA1000")
ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098)
ar1.CaptureCardConfig_Mode(1, 2, 1, 2, 3, 30)
ar1.CaptureCardConfig_PacketDelay(25)
ar1.CaptureCardConfig_StartRecord("C:\\ti\\mmwave_studio_02_01_01_00\\mmWaveStudio\\PostProc\\craniattempt.bin", 1)

ar1.StartFrame()