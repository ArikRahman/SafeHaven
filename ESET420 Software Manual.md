hostname -I
```
Open a command terminal window on your interfacing computer type the following:
```bash
ssh <IP address>
```
In order to avoid being prompted for password each ssh, which disrupts some of the software workflows, create your own key and share it with the Raspberry Pi 5, until it stops prompting for password.

**To remote access via VNC**, download RealVNC.
Download here: [RealVNC® - Remote access software for desktop and mobile | RealVNC](https://www.realvnc.com/en/connect/download/viewer/)
Ensure that your interfacing computer and the RP5 are on the same network. With RealVNC opened on your computer, type the IP address of the RP5 into the top search bar, and click enter. You will then be prompted to enter the password of the RP5 to gain remote access.

#### Download VSCode and Github on RP5 via Pi-Apps.io
Execute the following command on terminal:
```bash
wget -q0- https://raw.githubusercontent.com/Botspot/pi-apps/master/install | bash
```
On the top left, click on the Raspberry Pi logo. Navigate to Preferences > Pi-Apps. Download VSCode and Github Desktop.

#### Raspberry Pi Github Setup
Run the following commands on terminal:
```bash
git clone https://github.com/ArikRahman/SafeHaven.git
```

#### Uniflash
Download TI’s Uniflash to flash the latest firmware version to the IWR1443 and the DCA1000.
Download here: [UNIFLASH Software programming tool | TI.com](https://www.ti.com/tool/UNIFLASH)
Once each board is flashed, there is no need to flash again in the future unless the firmware stops functioning properly or a new one is required. On first time setup, it may be necessary to format the board. To do so, put jumpers (the little black boxes) on SOP 0 and SOP 2. Once using mmWave studio, switch them to SOP 1 and SOP2.

#### mmWave Studio
Download TI’s mmWave Studio to interface with the IWR1443 and the DCA1000.
Download here: [MMWAVE-STUDIO IDE, configuration, compiler or debugger | TI.com](https://www.ti.com/tool/MMWAVE-STUDIO)
Make sure that only one transmitter is used for our SAR generation methodology as we are using SISO, not MIMO. It is recommended to enable TX0 and disable TX1, and not vice versa.

#### Recommended Installations
*   **Z Shell terminal manager**
    *   Oh-my-zsh
    *   Zoxide (cd alternative)
    *   Atuin (Shell history)
    *   Experimental: nushell
*   **VS Code**
    *   SSH extension (Highly Recommended)
    *   Allows for fast development on the RP5 without slow VNC overhead
*   **Nix and flakes**
*   **uv Python manager (highly recommended)**
    *   Our repository was built around a uv framework, and it would be challenging to operate without installing this plugin.
    *   Makes handling virtual environments and dependency management straightforward.
*   **Just**
    *   Use justfiles to make commands straightforward and concise
*   **Experimental**
    *   Flask for web frontend
        *   Dangerous due to injecting live commands, would avoid or remove from repository
        *   Ideally transition to Elixir/Gleam Phoenix Framework
*   **Miscellaneous dev tools**
    *   fzf
    *   yazi
    *   Fd
    *   Ripgrep
    *   Github Desktop
    *   Lazygit
    *   Jq
    *   Fswatch
    *   Basedpyright — good Python LSP
    *   AGENTS.md

### Step 2: Lua Script
Within mmWave studio, run the lua script by pressing the button on the bottom left, and running the script in `SoftwareDemo/GantryFunctionality/MotorTest/` named `motorTest_rev13.py`. Run it by using:
```bash
uv run
```

### Step 3 — Bin Dumps Pre-processing:
Use batchprocessing python file to transfer dumps into the classification folder. This will grayscale and normalize the resolution for the ML model to work with.

### Step 4 — Object Classification:
Separate the images dumped into Safehaven-Classification and move them into a folder called train. Run:
```bash
uv run weapon_classifier.py train --data_dir <path_to_dataset aka train> epochs = (number e.g. 10)
```

To subsequently predict the item, run:
```bash
uv run weapon_classifier.py predict --image <path_to_image> [options]
```

More arguments or options can be found in the `Safehaven-Classification` directory `readme.md`.

---

## Appendix

### Oh-my-zsh one liner:
```bash
git clone https://github.com/zsh-users/zsh-autosuggestions.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions && \
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting && \
sed -i 's/^plugins=(/plugins=(zsh-autosuggestions zsh-syntax-highlighting /' ~/.zshrc && \
exec zsh
```
