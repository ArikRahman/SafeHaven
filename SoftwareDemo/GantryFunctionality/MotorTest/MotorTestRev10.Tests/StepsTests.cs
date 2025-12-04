using System;
using System.IO;
using System.Diagnostics;
using Xunit;
using MotorTestRev10;

namespace MotorTestRev10.Tests
{
    public class StepsTests
    {
        [Theory]
        [InlineData(1, 11)]
        [InlineData(2094, 22615)]
        [InlineData(100, 1080)]
        public void StepsNeeded_CalculatesCorrectly(int pixels, int expected)
        {
            var steps = Program.StepsNeeded(pixels);
            Assert.Equal(expected, steps);
        }

        [Fact]
        public void Program_CLI_Simulate_Next_UpdatesStateFile()
        {
            // Find the built assembly for Program via its loaded assembly location
            var dllPath = typeof(Program).Assembly.Location;
            Assert.True(File.Exists(dllPath), $"Could not find compiled dll: {dllPath}");

            // Use a temp file as state file
            var tmpState = Path.Combine(Path.GetTempPath(), $"mt_state_{Guid.NewGuid()}.txt");
            if (File.Exists(tmpState)) File.Delete(tmpState);

            // Run the binary with --simulate next and --state-file to our tmp state file
            var start = new ProcessStartInfo
            {
                FileName = "dotnet",
                Arguments = $"{dllPath} --simulate next --state-file=\"{tmpState}\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
            };

            using var proc = Process.Start(start);
            Assert.NotNull(proc);
            proc.WaitForExit(10000);
            Assert.True(File.Exists(tmpState), "State file should have been created by CLI run");

            // Check value is a number and within expected range
            var content = File.ReadAllText(tmpState).Trim();
            Assert.True(UInt64.TryParse(content, out var v));
            Assert.InRange(v, (ulong)1, (ulong)Program.vectorListDiscrete.Length);

            // Cleanup
            try { File.Delete(tmpState); } catch { }
        }
    }
}
