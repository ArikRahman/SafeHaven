# SafeHaven (Phoenix + Gleam)

This project is a port of the SafeHaven Frontend to the Phoenix Framework, utilizing Gleam for core logic.

## Prerequisites

*   **Elixir**: ~> 1.15
*   **Erlang/OTP**: 27
*   **Gleam**: ~> 1.0
*   **Bun** (for asset management)

## Setup

To start your Phoenix server:

1.  **Install dependencies:**
    ```bash
    mix deps.get
    ```

2.  **Install Asset dependencies:**
    ```bash
    cd assets && bun install && cd ..
    ```

3.  **Install Gleam dependencies:**
    Since this project mixes Elixir and Gleam, you need to ensure Gleam packages are downloaded.
    ```bash
    gleam deps download
    ```

4.  **Start the server:**
    ```bash
    mix phx.server
    ```

Now you can visit [`localhost:4000`](http://localhost:4000) from your browser.

## Project Structure

*   `lib/safe_haven_web`: Contains the Phoenix web layer (Controllers, Views, Templates).
*   `src/safe_haven.gleam`: Contains the core application logic written in Gleam.
*   `mix.exs`: Elixir project configuration, including the `mix_gleam` compiler.
*   `gleam.toml`: Gleam project configuration.

## Features

*   **Motor Control**: Execute predefined motor commands.
*   **Heatmaps**: Run heatmap generation scripts.
*   **Terminal**: A web-based terminal interface to run system commands.

## Development

*   **Gleam Compilation**: The `mix_gleam` plugin automatically compiles Gleam code when you run `mix compile` or start the server.
*   **FFI**: The Gleam code uses Foreign Function Interface (FFI) to call Erlang/Elixir standard library functions (like `System.cmd` via `os:cmd` or similar wrappers) to execute shell commands.

## Learn more

*   [Phoenix Framework](https://www.phoenixframework.org/)
*   [Gleam Language](https://gleam.run/)
*   [MixGleam](https://github.com/gleam-lang/mix_gleam)