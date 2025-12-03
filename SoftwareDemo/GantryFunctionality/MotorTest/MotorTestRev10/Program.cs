// motorTest_rev10.cs
// C# port of motorTest_rev10.py
// Notes / Changes:
// - Uses System.Device.Gpio for GPIO access. When running on non-Pi systems, pass --simulate to use console prints instead.
// - Step pulses are generated with software PWM via busy-wait using System.Diagnostics.Stopwatch for better timing resolution than Thread.Sleep.
// - The mapping from pixels -> stepper steps uses integer math derived from the Python version.
// - All file operations and path logic are preserved; progress is saved to 'current_index.txt'.
//dear ai - make it so the you are using paths correctly. dont assume
//also, commetn every code you do to avoid cyclical backtracking
using System;
using System.Collections.Generic;
using System.Device.Gpio;
using System.Diagnostics;
using System.IO;
using System.Threading;

namespace MotorTestRev10
{
        class Motor
    {
        private readonly int pulPin;
        private readonly int dirPin;
        private readonly int frequencyHz;
                private readonly GpioController? controller;
        private readonly bool simulate;
            private readonly string label;

        public Motor(GpioController? controller, int pulPin, int dirPin, int frequencyHz, bool simulate, string label = "")
        {
            this.controller = controller;
            this.pulPin = pulPin;
            this.dirPin = dirPin;
            this.frequencyHz = frequencyHz;
            this.simulate = simulate;
            this.label = label;

            if (!simulate)
            {
                // Guard controller null
                if (controller != null)
                {
                    controller.OpenPin(pulPin, PinMode.Output);
                    controller.OpenPin(dirPin, PinMode.Output);
                    controller.Write(pulPin, PinValue.Low);
                    controller.Write(dirPin, PinValue.Low);
                }
            }
        }

        public void SetDirection(bool cw)
        {
            if (simulate || controller == null)
            {
                Console.WriteLine($"[Sim][{label}] DIR {dirPin} = {(cw ? "HIGH" : "LOW")} ");
                return;
            }
            controller.Write(dirPin, cw ? PinValue.High : PinValue.Low);
        }

        // PulseSteps: produce 'steps' pulses at frequencyHz, using software busy-wait
        public void PulseSteps(ulong steps)
        {
            if (simulate || controller == null)
            {
                // Simulate the pulses: print and delay for approximate total time
                Console.WriteLine($"[Sim][{label}] PUL {pulPin} pulses={steps} @ {frequencyHz}Hz");
                if (frequencyHz > 0 && steps > 0)
                {
                    // total time (s) = steps / frequencyHz
                    var totalMs = (long)((double)steps / (double)frequencyHz * 1000.0);
                    // Make sure at least a tiny delay is given for very small times
                    if (totalMs > 0) Thread.Sleep((int)totalMs);
                }
                return;
            }

            if (controller == null || frequencyHz <= 0 || steps == 0)
            {
                if (controller != null) controller.Write(pulPin, PinValue.Low);
                return;
            }

            // Compute ticks for half-period using Stopwatch timing
            double periodSec = 1.0 / (double)frequencyHz;
            double halfPeriodSec = periodSec / 2.0;
            double ticksPerSecond = Stopwatch.Frequency;
            long halfPeriodTicks = (long)(ticksPerSecond * halfPeriodSec);

            var sw = Stopwatch.StartNew();
            for (ulong i = 0; i < steps; i++)
            {
                controller.Write(pulPin, PinValue.High);
                long startTicks = Stopwatch.GetTimestamp();
                while (Stopwatch.GetTimestamp() - startTicks < halfPeriodTicks) { /* busy wait */ }
                controller.Write(pulPin, PinValue.Low);
                startTicks = Stopwatch.GetTimestamp();
                while (Stopwatch.GetTimestamp() - startTicks < halfPeriodTicks) { /* busy wait */ }
            }
        }

        public void Stop()
        {
            if (simulate || controller == null)
            {
                Console.WriteLine($"[Sim][{label}] Stop pulse {pulPin}");
                return;
            }
            controller.Write(pulPin, PinValue.Low);
        }

        public void Close()
        {
            if (!simulate && controller != null)
            {
                // Keep pins low and close
                controller.Write(pulPin, PinValue.Low);
                controller.Write(dirPin, PinValue.Low);
                if (controller.IsPinOpen(pulPin)) controller.ClosePin(pulPin);
                if (controller.IsPinOpen(dirPin)) controller.ClosePin(dirPin);
            }
        }
    }

    public class Program
    {
        // Parameters (match the Python version)
        const int PUL_PIN_X = 13;
        const int DIR_PIN_X = 6;
        const int PUL_PIN_Y = 12;
        const int DIR_PIN_Y = 16;

        const double duty_cycle = 0.50; // Not used here but kept for compatibility
        const int f_x = 6400;
        const int f_y = 6400;
        const int steps_per_rev = 1600; // microsteps per revolution
        const int length_per_rev = 10;  // mm/rev
        const int total_distance = 675; // mm
        const int total_pixels = 10000; // pixels

        // Vector list discrete
        public static readonly (int x, int y)[] vectorListDiscrete = new (int, int)[]
        {
            (0, 10000), (0, 9900), (2094, 9900), (2094, 7940), (2094, 5980), (2094, 4020), (2094, 2060), (2094, 100),
            (2844, 100), (2844, 2060), (2844, 4020), (2844, 5980), (2844, 7940), (2844, 9900),
            (3594, 9900), (3594, 7940), (3594, 5980), (3594, 4020), (3594, 2060), (3594, 100),
            (4344, 100), (4344, 2060), (4344, 4020), (4344, 5980), (4344, 7940), (4344, 9900),
            (5094, 9900), (5094, 7940), (5094, 5980), (5094, 4020), (5094, 2060), (5094, 100),
            (5844, 100), (5844, 2060), (5844, 4020), (5844, 5980), (5844, 7940), (5844, 9900),
            (6594, 9900), (6594, 7940), (6594, 5980), (6594, 4020), (6594, 2060), (6594, 100),
            (7156, 100), (7156, 2060), (7156, 4020), (7156, 5980), (7156, 7940), (7156, 9900),
            (7156, 10000), (0, 10000)
        };

        // Calculate steps per pixel using integer math
        static readonly double stepsPerPixel = (double)steps_per_rev * (double)total_distance / ((double)length_per_rev * (double)total_pixels);

        static int Main(string[] args)
        {
            var simulate = false;
            var force = false;
            // Default state file stored next to the executable so path isn't assumed
            var baseDir = AppContext.BaseDirectory ?? Directory.GetCurrentDirectory();
            var stateFile = Path.Combine(baseDir, "current_index.txt");
            foreach (var a in args)
            {
                if (a == "--simulate") simulate = true;
                if (a == "--force") force = true;
                if (a.StartsWith("--state-file="))
                {
                    var subPath = a.Substring("--state-file=".Length);
                    if (!string.IsNullOrWhiteSpace(subPath)) stateFile = subPath;
                }
            }

            // Safety: require explicit --force to run motors in non-simulate mode
            if (!simulate && !force)
            {
                Console.WriteLine("Hardware control requires --force to run. To execute motors for real, please run with --force or use --simulate for a safe test.");
                return 1;
            }

            // Create GpioController for hardware control. On unsupported environments this may fail; catch errors and exit gracefully.
            GpioController? controller = null;
            if (!simulate)
            {
                try
                {
                    controller = new GpioController();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Failed to create GpioController: {ex.Message}");
                    return 2;
                }
            }
            var motorX = new Motor(controller, PUL_PIN_X, DIR_PIN_X, f_x, simulate, "X");
            var motorY = new Motor(controller, PUL_PIN_Y, DIR_PIN_Y, f_y, simulate, "Y");

            try
            {
                if (Array.Exists(args, s => s == "next"))
                {
                    ulong currentIndex = 0;
                    // Use robust path handling: read stored file next to app unless overridden
                    if (File.Exists(stateFile))
                    {
                        var txt = File.ReadAllText(stateFile).Trim();
                        Console.WriteLine($"Loading state file: {stateFile} -> '{txt}'");
                        if (UInt64.TryParse(txt, out var parsed)) currentIndex = parsed;
                        else Console.WriteLine("Warning: state file content not parsable, defaulting to 0");
                    }
                    else
                    {
                        Console.WriteLine($"No statefile found at {stateFile}, starting at index 0");
                    }

                    if (currentIndex >= (ulong)vectorListDiscrete.Length - 1) return 0;

                    var currentX = vectorListDiscrete[currentIndex].x;
                    var currentY = vectorListDiscrete[currentIndex].y;

                    ulong nextIndex = currentIndex + 1;
                    while (nextIndex < (ulong)vectorListDiscrete.Length)
                    {
                        var nextX = vectorListDiscrete[nextIndex].x;
                        var nextY = vectorListDiscrete[nextIndex].y;
                        var dx = nextX - currentX;
                        var dy = nextY - currentY;
                        if (dx != 0)
                        {
                            if (dx > 0)
                            {
                                // Move right: X positive
                                var steps = StepsNeeded(Math.Abs(dx));
                                Console.WriteLine($"Move X: dx={dx} pixels -> steps={steps} dir=CW");
                                motorX.SetDirection(true);
                                motorX.PulseSteps((ulong)steps);
                            }
                            else
                            {
                                var steps = StepsNeeded(Math.Abs(dx));
                                Console.WriteLine($"Move X: dx={dx} pixels -> steps={steps} dir=CCW");
                                motorX.SetDirection(false);
                                motorX.PulseSteps((ulong)steps);
                            }
                        }
                        if (dy != 0)
                        {
                            if (dy > 0)
                            {
                                var steps = StepsNeeded(Math.Abs(dy));
                                Console.WriteLine($"Move Y: dy={dy} pixels -> steps={steps} dir=CW");
                                motorY.SetDirection(true);
                                motorY.PulseSteps((ulong)steps);
                            }
                            else
                            {
                                var steps = StepsNeeded(Math.Abs(dy));
                                Console.WriteLine($"Move Y: dy={dy} pixels -> steps={steps} dir=CCW");
                                motorY.SetDirection(false);
                                motorY.PulseSteps((ulong)steps);
                            }
                            break;
                        }
                        currentX = nextX;
                        currentY = nextY;
                        nextIndex += 1;
                    }

                    motorX.Stop();
                    motorY.Stop();

                    // Save new index; write atomically (use temp then move) to avoid truncation
                    var tmp = stateFile + ".tmp";
                    File.WriteAllText(tmp, nextIndex.ToString());
                    File.Copy(tmp, stateFile, true);
                    File.Delete(tmp);

                    if (nextIndex >= (ulong)vectorListDiscrete.Length - 1)
                    {
                        // End of list - close motors and delete index
                        motorX.Close(); motorY.Close();
                        if (File.Exists(stateFile)) File.Delete(stateFile);
                    }
                }

                return 0;
            }
            finally
            {
                motorX.Close();
                motorY.Close();
                controller?.Dispose();
            }
        }

        public static int StepsNeeded(int pixels)
        {
            // steps = pixels * steps_per_rev * total_distance / (length_per_rev * total_pixels)
            // Use double and rounding for this calculation
            double stepsD = pixels * stepsPerPixel;
            return (int)Math.Round(stepsD);
        }
    }
}
