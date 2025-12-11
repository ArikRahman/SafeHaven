import gleam/dict.{type Dict}
import gleam/string

pub type CommandResult {
  CommandResult(output: String, error: String, exit_code: Int)
}

@external(erlang, "Elixir.System", "shell")
fn system_shell(command: String) -> #(String, Int)

pub fn get_motor_commands() -> Dict(String, List(String)) {
  dict.from_list([
    #("list_dir", ["cmd", "/c", "dir"]),
    #("show_disk", ["cmd", "/c", "wmic", "logicaldisk", "get", "size,freespace,caption"]),
    #("show_processes", ["cmd", "/c", "tasklist"]),
    #("kirkinator", []),
    #("george droyd AI", []),
    #("we are charlie kirk", []),
  ])
}

pub fn get_heatmap_commands() -> Dict(String, List(String)) {
  dict.from_list([
    #("heatmap example", []),
  ])
}

pub fn run_command(command_key: String, command_map: Dict(String, List(String))) -> CommandResult {
  case dict.get(command_map, command_key) {
    Ok(args) -> {
      case args {
        [] -> CommandResult(output: "Dummy command executed: " <> command_key, error: "", exit_code: 0)
        _ -> {
          let full_cmd = string.join(args, " ")
          let #(output, exit_code) = system_shell(full_cmd)
          CommandResult(output: output, error: "", exit_code: exit_code)
        }
      }
    }
    Error(_) -> CommandResult(output: "", error: "Invalid command selected", exit_code: 1)
  }
}

pub fn run_terminal_command(cmd_text: String) -> CommandResult {
  let full_cmd = "cmd /c " <> cmd_text
  let #(output, exit_code) = system_shell(full_cmd)
  CommandResult(output: output, error: "", exit_code: exit_code)
}
