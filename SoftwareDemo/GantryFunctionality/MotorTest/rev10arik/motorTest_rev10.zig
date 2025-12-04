const std = @import("std");
//Dear AI, always make code for each edit you do
// This Zig version of the motor control script has been adapted from the Python version.
// Changes made for Zig compatibility:
// - Type conversions use @as instead of @intToFloat/@floatFromInt/@floatToInt
// - Sleep uses std.time.sleep
// - File opening uses .mode = .write_only
// - GPIO functions are placeholders using sysfs; implement proper PWM for hardware control
// - Args changed to const

const fs = std.fs;
const mem = std.mem;
const fmt = std.fmt;

const PUL_PIN_X = 13;
const DIR_PIN_X = 6;
const PUL_PIN_Y = 12;
const DIR_PIN_Y = 16;

const duty_cycle = 0.5;
const f_x = 6400;
const f_y = 6400;
const steps_per_rev = 1600;
const length_per_rev = 10;
const total_distance = 675;
const total_pixels = 10000;

// Using @as for type conversion instead of @intToFloat/@floatFromInt for compatibility with the installed Zig version
const speedX_rev_per_s = @as(f64, f_x) / @as(f64, steps_per_rev);
const speedX_mm_per_s = speedX_rev_per_s * @as(f64, length_per_rev);
const speedX_pixels_per_s = speedX_mm_per_s / @as(f64, total_distance) * @as(f64, total_pixels);

// Using @as for type conversion instead of @intToFloat/@floatFromInt for compatibility with the installed Zig version
const speedY_rev_per_s = @as(f64, f_y) / @as(f64, steps_per_rev);
const speedY_mm_per_s = speedY_rev_per_s * @as(f64, length_per_rev);
const speedY_pixels_per_s = speedY_mm_per_s / @as(f64, total_distance) * @as(f64, total_pixels);

const Point = struct {
    x: i32,
    y: i32,
};

const vectorListDiscrete = [_]Point{
    .{ .x = 0, .y = 10000 },
    .{ .x = 0, .y = 9900 },
    .{ .x = 2094, .y = 9900 },
    .{ .x = 2094, .y = 7940 },
    .{ .x = 2094, .y = 5980 },
    .{ .x = 2094, .y = 4020 },
    .{ .x = 2094, .y = 2060 },
    .{ .x = 2094, .y = 100 },
    .{ .x = 2844, .y = 100 },
    .{ .x = 2844, .y = 2060 },
    .{ .x = 2844, .y = 4020 },
    .{ .x = 2844, .y = 5980 },
    .{ .x = 2844, .y = 7940 },
    .{ .x = 2844, .y = 9900 },
    .{ .x = 3594, .y = 9900 },
    .{ .x = 3594, .y = 7940 },
    .{ .x = 3594, .y = 5980 },
    .{ .x = 3594, .y = 4020 },
    .{ .x = 3594, .y = 2060 },
    .{ .x = 3594, .y = 100 },
    .{ .x = 4344, .y = 100 },
    .{ .x = 4344, .y = 2060 },
    .{ .x = 4344, .y = 4020 },
    .{ .x = 4344, .y = 5980 },
    .{ .x = 4344, .y = 7940 },
    .{ .x = 4344, .y = 9900 },
    .{ .x = 5094, .y = 9900 },
    .{ .x = 5094, .y = 7940 },
    .{ .x = 5094, .y = 5980 },
    .{ .x = 5094, .y = 4020 },
    .{ .x = 5094, .y = 2060 },
    .{ .x = 5094, .y = 100 },
    .{ .x = 5844, .y = 100 },
    .{ .x = 5844, .y = 2060 },
    .{ .x = 5844, .y = 4020 },
    .{ .x = 5844, .y = 5980 },
    .{ .x = 5844, .y = 7940 },
    .{ .x = 5844, .y = 9900 },
    .{ .x = 6594, .y = 9900 },
    .{ .x = 6594, .y = 7940 },
    .{ .x = 6594, .y = 5980 },
    .{ .x = 6594, .y = 4020 },
    .{ .x = 6594, .y = 2060 },
    .{ .x = 6594, .y = 100 },
    .{ .x = 7156, .y = 100 },
    .{ .x = 7156, .y = 2060 },
    .{ .x = 7156, .y = 4020 },
    .{ .x = 7156, .y = 5980 },
    .{ .x = 7156, .y = 7940 },
    .{ .x = 7156, .y = 9900 },
    .{ .x = 7156, .y = 10000 },
    .{ .x = 0, .y = 10000 },
};

// A small sysfs GPIO helper. Uses /sys/class/gpio to export pins and write values.
fn gpioPath(pin: u8, filename: []const u8) ![]u8 {
    return try fmt.allocPrint(std.heap.page_allocator, "/sys/class/gpio/gpio{d}/{s}", .{pin, filename});
}

fn exportPin(pin: u8) !void {
    const gpio_dir = try fmt.allocPrint(std.heap.page_allocator, "/sys/class/gpio/gpio{d}", .{pin});
    defer std.heap.page_allocator.free(gpio_dir);
    if (fs.cwd().openFile(gpio_dir, .{})) |file| {
        file.close();
        return; // already exported
    } else |_| {
        const export_file = try fs.cwd().openFile("/sys/class/gpio/export", .{ .mode = .write_only });
        defer export_file.close();
        var tmp: [8]u8 = undefined;
        const s = try std.fmt.bufPrint(&tmp, "{}", .{pin});
        try export_file.writeAll(s);
        // wait for gpio folder to appear (short timeout)
        var i: u32 = 0;
        while (i < 50) {
            if (fs.cwd().openFile(gpio_dir, .{})) |f| { f.close(); break; } else |_| {}
            std.time.sleep(10 * std.time.ms_per_ms);
            i += 1;
        }
    }
}

fn setDirectionSys(pin: u8, dir_out: bool) !void {
    try exportPin(pin);
    const path = try fmt.allocPrint(std.heap.page_allocator, "/sys/class/gpio/gpio{d}/direction", .{pin});
    defer std.heap.page_allocator.free(path);
    const f = try fs.cwd().openFile(path, .{ .mode = .write_only });
    defer f.close();
    try f.writeAll(if (dir_out) "out\n" else "in\n");
}

fn setGpio(pin: u8, value: u8) !void {
    // Write to /sys/class/gpio/gpio{pin}/value. If sysfs not available, print the action.
    const gpio_dir = try fmt.allocPrint(std.heap.page_allocator, "/sys/class/gpio/gpio{d}", .{pin});
    defer std.heap.page_allocator.free(gpio_dir);
    if (fs.cwd().openFile(gpio_dir, .{})) |_| {
        const path = try fmt.allocPrint(std.heap.page_allocator, "/sys/class/gpio/gpio{d}/value", .{pin});
        defer std.heap.page_allocator.free(path);
        const file = try fs.cwd().openFile(path, .{ .mode = .write_only });
        defer file.close();
        try file.writeAll(if (value == 1) "1\n" else "0\n");
    } else |_| {
        std.debug.print("[Sim] Setting GPIO {} to {}\n", .{pin, value});
    }
}

fn setPwm(pin: u8, value: f64) !void {
    // Placeholder for PWM - implement with /sys/class/pwm
    std.debug.print("Setting PWM {} to {}\n", .{pin, value});
    // For now, just set GPIO high/low for square wave simulation
    // For compatibility, don't write direct set here; use pulse() for timed pulses.
}

// Pulse a GPIO pin at a given frequency for a given duration (nanoseconds)
// This is a fallback software PWM implementation.
// Pulse a GPIO pin for a given number of steps at a given frequency. This generates
// 'steps' full pulses (a HIGH-LOW cycle equals one step).
fn pulseSteps(pin: u8, freq_hz: u64, steps: u64) !void {
    if (freq_hz == 0) return;
    const period_ns = std.time.ns_per_s / freq_hz; // integer nanoseconds
    const half_ns = if (period_ns >= 2) period_ns / 2 else 0;
    var i: u64 = 0;
    while (i < steps) : (i += 1) {
        setGpio(pin, 1) catch |e| std.debug.print("setGpio high failed: {}\n", .{e});
        if (half_ns > 0) std.Thread.sleep(half_ns);
        setGpio(pin, 0) catch |e| std.debug.print("setGpio low failed: {}\n", .{e});
        if (half_ns > 0) std.Thread.sleep(half_ns);
    }
}

fn up(pixels: i32) !void {
    try setDirectionSys(DIR_PIN_Y, true);
    // Compute steps needed to move 'pixels'
    const pixels_u128 = @as(u128, pixels);
    const numerator = pixels_u128 * @as(u128, steps_per_rev) * @as(u128, total_distance);
    const denom = @as(u128, length_per_rev) * @as(u128, total_pixels);
    const steps_needed = @as(u64, (numerator + denom / 2) / denom);
    try pulseSteps(PUL_PIN_Y, @as(u64, f_y), steps_needed);
}

fn right(pixels: i32) !void {
    try setDirectionSys(DIR_PIN_X, true);
    const pixels_u128 = @as(u128, pixels);
    const numerator = pixels_u128 * @as(u128, steps_per_rev) * @as(u128, total_distance);
    const denom = @as(u128, length_per_rev) * @as(u128, total_pixels);
    const steps_needed = @as(u64, (numerator + denom / 2) / denom);
    try pulseSteps(PUL_PIN_X, @as(u64, f_x), steps_needed);
}

fn down(pixels: i32) !void {
    try setDirectionSys(DIR_PIN_Y, false);
    const pixels_u128 = @as(u128, pixels);
    const numerator = pixels_u128 * @as(u128, steps_per_rev) * @as(u128, total_distance);
    const denom = @as(u128, length_per_rev) * @as(u128, total_pixels);
    const steps_needed = @as(u64, (numerator + denom / 2) / denom);
    try pulseSteps(PUL_PIN_Y, @as(u64, f_y), steps_needed);
}

fn left(pixels: i32) !void {
    try setDirectionSys(DIR_PIN_X, false);
    const pixels_u128 = @as(u128, pixels);
    const numerator = pixels_u128 * @as(u128, steps_per_rev) * @as(u128, total_distance);
    const denom = @as(u128, length_per_rev) * @as(u128, total_pixels);
    const steps_needed = @as(u64, (numerator + denom / 2) / denom);
    try pulseSteps(PUL_PIN_X, @as(u64, f_x), steps_needed);
}

fn stopX_Motor() !void {
    try setGpio(PUL_PIN_X, 0);
}

fn stopY_Motor() !void {
    try setGpio(PUL_PIN_Y, 0);
}

fn stopAllMotor() !void {
    try stopX_Motor();
    try stopY_Motor();
}

pub fn main() !void {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    // Changed to const as args is not mutated, per Zig compiler suggestion
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len > 1 and mem.eql(u8, args[1], "next")) {
        var current_index: usize = 0;
        if (fs.cwd().openFile("current_index.txt", .{})) |file| {
            var buf: [10]u8 = undefined;
            const len = try file.read(&buf);
            current_index = try fmt.parseInt(usize, buf[0..len], 10);
            file.close();
        } else |_| {}
        std.debug.print("Current index: {}\n", .{current_index});

        if (current_index >= vectorListDiscrete.len - 1) {
            return;
        }

        var currentX = vectorListDiscrete[current_index].x;
        var currentY = vectorListDiscrete[current_index].y;
        std.debug.print("Current position: ({}, {})\n", .{currentX, currentY});

        var next_index = current_index + 1;
        while (next_index < vectorListDiscrete.len) {
            const nextX = vectorListDiscrete[next_index].x;
            const nextY = vectorListDiscrete[next_index].y;
            const dx = nextX - currentX;
            const dy = nextY - currentY;
            std.debug.print("Next index: {}, Next position: ({}, {}), dx: {}, dy: {}\n", .{next_index, nextX, nextY, dx, dy});
            if (dx != 0) {
                if (dx > 0) {
                    try right(dx);
                } else {
                    try left(-dx);
                }
            }
            if (dy != 0) {
                if (dy > 0) {
                    try up(dy);
                } else {
                    try down(-dy);
                }
                break;
            }
            currentX = nextX;
            currentY = nextY;
            next_index += 1;
        }

        try stopAllMotor();

        const file = try fs.cwd().createFile("current_index.txt", .{});
        defer file.close();
        var buf: [20]u8 = undefined;
        const slice = try std.fmt.bufPrint(&buf, "{}", .{next_index});
        try file.writeAll(slice);

        if (next_index >= vectorListDiscrete.len - 1) {
            try fs.cwd().deleteFile("current_index.txt");
        }
    }
}