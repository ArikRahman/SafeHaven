-module(safe_haven).
-compile([no_auto_import, nowarn_unused_vars, nowarn_unused_function, nowarn_nomatch, inline]).
-define(FILEPATH, "src/safe_haven.gleam").
-export([get_motor_commands/0, get_heatmap_commands/0, run_command/2, run_terminal_command/1]).
-export_type([command_result/0]).

-type command_result() :: {command_result, binary(), binary(), integer()}.

-file("src/safe_haven.gleam", 11).
-spec get_motor_commands() -> gleam@dict:dict(binary(), list(binary())).
get_motor_commands() ->
    maps:from_list(
        [{<<"list_dir"/utf8>>, [<<"cmd"/utf8>>, <<"/c"/utf8>>, <<"dir"/utf8>>]},
            {<<"show_disk"/utf8>>,
                [<<"cmd"/utf8>>,
                    <<"/c"/utf8>>,
                    <<"wmic"/utf8>>,
                    <<"logicaldisk"/utf8>>,
                    <<"get"/utf8>>,
                    <<"size,freespace,caption"/utf8>>]},
            {<<"show_processes"/utf8>>,
                [<<"cmd"/utf8>>, <<"/c"/utf8>>, <<"tasklist"/utf8>>]},
            {<<"kirkinator"/utf8>>, []},
            {<<"george droyd AI"/utf8>>, []},
            {<<"we are charlie kirk"/utf8>>, []}]
    ).

-file("src/safe_haven.gleam", 22).
-spec get_heatmap_commands() -> gleam@dict:dict(binary(), list(binary())).
get_heatmap_commands() ->
    maps:from_list([{<<"heatmap example"/utf8>>, []}]).

-file("src/safe_haven.gleam", 28).
-spec run_command(binary(), gleam@dict:dict(binary(), list(binary()))) -> command_result().
run_command(Command_key, Command_map) ->
    case gleam_stdlib:map_get(Command_map, Command_key) of
        {ok, Args} ->
            case Args of
                [] ->
                    {command_result,
                        <<"Dummy command executed: "/utf8, Command_key/binary>>,
                        <<""/utf8>>,
                        0};

                _ ->
                    Full_cmd = gleam@string:join(Args, <<" "/utf8>>),
                    {Output, Exit_code} = 'Elixir.System':shell(Full_cmd),
                    {command_result, Output, <<""/utf8>>, Exit_code}
            end;

        {error, _} ->
            {command_result,
                <<""/utf8>>,
                <<"Invalid command selected"/utf8>>,
                1}
    end.

-file("src/safe_haven.gleam", 44).
-spec run_terminal_command(binary()) -> command_result().
run_terminal_command(Cmd_text) ->
    Full_cmd = <<"cmd /c "/utf8, Cmd_text/binary>>,
    {Output, Exit_code} = 'Elixir.System':shell(Full_cmd),
    {command_result, Output, <<""/utf8>>, Exit_code}.
