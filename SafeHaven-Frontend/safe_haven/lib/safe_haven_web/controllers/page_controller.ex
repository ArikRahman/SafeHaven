defmodule SafeHavenWeb.PageController do
  use SafeHavenWeb, :controller

  def home(conn, _params) do
    redirect(conn, to: ~p"/motor")
  end

  def motor(conn, _params) do
    commands = :safe_haven.get_motor_commands()

    render(conn, :index,
      page_title: "Motor Control",
      commands: commands,
      selected_command: nil,
      output: nil,
      error: nil,
      returncode: nil,
      run_endpoint: ~p"/motor/run",
      active_page: "motor"
    )
  end

  def run_motor(conn, %{"command" => cmd_key}) do
    commands = :safe_haven.get_motor_commands()

    # Call Gleam function
    result = :safe_haven.run_command(cmd_key, commands)

    # Destructure Gleam record (compiled to tuple)
    # type CommandResult { CommandResult(output: String, error: String, exit_code: Int) }
    {_, output, error, exit_code} = result

    render(conn, :index,
      page_title: "Motor Control",
      commands: commands,
      selected_command: cmd_key,
      output: output,
      error: error,
      returncode: exit_code,
      run_endpoint: ~p"/motor/run",
      active_page: "motor"
    )
  end

  def run_motor(conn, _params) do
    put_flash(conn, :error, "Invalid motor command selected.")
    |> redirect(to: ~p"/motor")
  end

  def heatmaps(conn, _params) do
    commands = :safe_haven.get_heatmap_commands()

    render(conn, :index,
      page_title: "Heatmaps",
      commands: commands,
      selected_command: nil,
      output: nil,
      error: nil,
      returncode: nil,
      run_endpoint: ~p"/heatmaps/run",
      active_page: "heatmaps"
    )
  end

  def run_heatmaps(conn, %{"command" => cmd_key}) do
    commands = :safe_haven.get_heatmap_commands()
    result = :safe_haven.run_command(cmd_key, commands)
    {_, output, error, exit_code} = result

    render(conn, :index,
      page_title: "Heatmaps",
      commands: commands,
      selected_command: cmd_key,
      output: output,
      error: error,
      returncode: exit_code,
      run_endpoint: ~p"/heatmaps/run",
      active_page: "heatmaps"
    )
  end

  def run_heatmaps(conn, _params) do
    put_flash(conn, :error, "Invalid heatmap command selected.")
    |> redirect(to: ~p"/heatmaps")
  end

  def terminal(conn, params) do
    history = params["history"] || ""

    render(conn, :terminal,
      page_title: "Terminal",
      history: history,
      active_page: "terminal"
    )
  end

  def run_terminal(conn, %{"command" => cmd_text} = params) do
    history = params["history"] || ""
    cmd_text = String.trim(cmd_text)

    if cmd_text != "" do
      result = :safe_haven.run_terminal_command(cmd_text)
      {_, output, error, _exit_code} = result

      output_str = output || ""
      error_str = error || ""

      new_block = "> #{cmd_text}\n#{output_str}#{error_str}\n"
      new_history = history <> new_block

      render(conn, :terminal,
        page_title: "Terminal",
        history: new_history,
        active_page: "terminal"
      )
    else
      render(conn, :terminal,
        page_title: "Terminal",
        history: history,
        active_page: "terminal"
      )
    end
  end
end
