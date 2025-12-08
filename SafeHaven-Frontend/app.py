from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess

app = Flask(__name__)
app.secret_key = "change-me"  # needed for flash messages

# Commands to run this file
    # cd C:\GitHub\SafeHaven\SafeHave-Frontend
    # python app.py

# Go to web browser and enter this in the url
    # http://localhost:5000/

# 1) Define a SAFE whitelist of commands
# Keys = IDs used in the UI, values = actual command + args as a list
ALLOWED_COMMANDS = {
    # List files in the current folder (Windows)
    "list_dir": ["cmd", "/c", "dir"],

    # Show disk usage (rough equivalent of df -h)
    "show_disk": ["cmd", "/c", "wmic logicaldisk get size,freespace,caption"],

    # Show processes
    "show_processes": ["cmd", "/c", "tasklist"],

    # Our own scripts:
    "kirkinator": [],

    "george droyd AI": [],

    "we are charlie kirk": [],
}

# Reuse  existing command list for the motor page
MOTOR_COMMANDS = ALLOWED_COMMANDS

# Separate commands for the heatmaps page
HEATMAP_COMMANDS = {
    "heatmap example": [],
    # "generate_heatmap": ["python", r"C:\path\to\heatmap_script.py"],
    # "open_heatmap_folder": ["cmd", "/c", "start", r"C:\path\to\heatmaps"],
}

@app.route("/")
def home():
    # Default landing page goes to motor control
    return redirect(url_for("motor_page"))


# ===== MOTOR PAGE & RUN =====

@app.route("/motor")
def motor_page():
    return render_template(
        "index.html",
        page_title="Motor Control",
        commands=MOTOR_COMMANDS,
        selected_command=None,
        output=None,
        error=None,
        returncode=None,
        run_endpoint="run_motor",
        active_page="motor",
    )

# Support BOTH /motor/run and old /run URL
@app.route("/motor/run", methods=["POST"])
@app.route("/run", methods=["POST"])
def run_motor():
    cmd_key = request.form.get("command")

    if cmd_key not in MOTOR_COMMANDS:
        flash("Invalid motor command selected.")
        return redirect(url_for("motor_page"))

    cmd = MOTOR_COMMANDS[cmd_key]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # don't raise exception on nonzero exit code
        )

        return render_template(
            "index.html",
            page_title="Motor Control",
            commands=MOTOR_COMMANDS,
            selected_command=cmd_key,
            output=result.stdout,
            error=result.stderr,
            returncode=result.returncode,
            run_endpoint="run_motor",
            active_page="motor",
        )

    except Exception as e:
        flash(f"Error running motor command: {e}")
        return redirect(url_for("motor_page"))


# ===== HEATMAPS PAGE & RUN =====

@app.route("/heatmaps")
def heatmaps_page():
    return render_template(
        "index.html",
        page_title="Heatmaps",
        commands=HEATMAP_COMMANDS,
        selected_command=None,
        output=None,
        error=None,
        returncode=None,
        run_endpoint="run_heatmaps",
        active_page="heatmaps",
    )


@app.route("/heatmaps/run", methods=["POST"])
def run_heatmaps():
    cmd_key = request.form.get("command")

    if cmd_key not in HEATMAP_COMMANDS:
        flash("Invalid heatmap command selected.")
        return redirect(url_for("heatmaps_page"))

    cmd = HEATMAP_COMMANDS[cmd_key]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        return render_template(
            "index.html",
            page_title="Heatmaps",
            commands=HEATMAP_COMMANDS,
            selected_command=cmd_key,
            output=result.stdout,
            error=result.stderr,
            returncode=result.returncode,
            run_endpoint="run_heatmaps",
            active_page="heatmaps",
        )

    except Exception as e:
        flash(f"Error running heatmap command: {e}")
        return redirect(url_for("heatmaps_page"))

@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    # History of commands & output (sent back and forth in a hidden field)
    history = request.form.get("history", "")

    if request.method == "POST":
        cmd_text = request.form.get("command", "").strip()

        if cmd_text:
            try:
                # On Windows: run through cmd
                result = subprocess.run(
                    ["cmd", "/c", cmd_text],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                stdout = result.stdout or ""
                stderr = result.stderr or ""

                new_block = f"> {cmd_text}\n{stdout}{stderr}\n"
                history = history + new_block

            except Exception as e:
                history = history + f"> {cmd_text}\n[ERROR] {e}\n"

    return render_template(
        "terminal.html",
        page_title="Terminal",
        history=history,
        active_page="terminal",
    )

# ===== MAIN =====

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)