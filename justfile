set shell := ["pwsh.exe", "-c"]

motor-arcade:
    ssh -t corban@10.244.182.88 "zsh -l -i -c 'cd /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/MotorTest; uv run motorTest_rev13.py arcade 40mms'"

sar-viz folder="dumps18":
    uv run Safehaven-Lua/mainSARneuronauts2py_rev3_2.py --z_start=320 --z_end=340 --zstep=2 --mat_plot_lib --xyonly --folder="{{folder}}"
