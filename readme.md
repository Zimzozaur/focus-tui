<!-- Icons -->
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI-Server](https://img.shields.io/pypi/v/focustui.svg)](https://pypi.org/project/focustui/)
[![Pyversions](https://img.shields.io/pypi/pyversions/focustui.svg)](https://pypi.python.org/pypi/focustui)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/focustui)](https://pepy.tech/project/focustui)

# FocusTUI: Your Deep Focus Session Buddy. (WIP)
## Are you struggling to maintain focus in a world full of distractions?

Say hello to FocusTUI - the minimalist, distraction-free focus session tracker that works straight from your terminal, no internet required. FocusTUI empowers you to create and track customized focus sessions with a highly personalized touch, ensuring you stay on track with your work, studies, or creative projects.

Disclaimer: The image displayed represents a potential appearance and features of FocusTUI. Actual app appearance and functionality may vary.
![board_image](https://raw.githubusercontent.com/Zimzozaur/focus-tui/refs/heads/master/app_preview.png)

### Key Features:

1.	**Cross-Platform:** Works seamlessly on every operating system and in any terminal. No matter where you are,
	  FocusTUI is there to support your focus.
2. **Statistics from Historical Data (coming soon):** Gain insights into your productivity with comprehensive
   statistics generated from
      your past focus sessions. Understand your patterns and optimize your workflow.
3.	**Custom Focus Queues (coming soon):** Create and manage your own focus queues, with sessions categorized and tailored to
	  your needs. Whether it’s deep work, light tasks, or breaks, FocusTUI adjusts to you.
4.	**Custom Themes (coming soon):** Personalize your experience with custom themes. Choose the colors that help you stay focused,
	  or design your own.
5.	**Custom Sounds:** Import your own alarms, ambient sounds, and other audio cues to create the perfect atmosphere for your focus sessions.

### Needed Tools
#### For Windows:

1. **Python Installation:**
   -  If you don’t have it installed, download Python from the official [website](https://www.python.org/downloads/).
   - During installation, make sure to check the checkbox that says **“Add Python to PATH”**.
2. **Install `Scoop`:**
   - Scoop is a command-line installer for Windows. If you don’t have it installed, follow the instructions on the
     Scoop official [website](https://scoop.sh).
3. **Install `pipx`:**
```bash
scoop install pipx
pipx ensurepath
```

#### For macOS:

1. **Install `Homebrew`:**
	- Homebrew is a package manager for macOS. If you don’t have it installed, follow the instructions on the
     Homebrew official [website](https://brew.sh/).
2. **Install `pipx`:**
```bash
brew install pipx
pipx ensurepath
```

#### For Linux:
1. **Install `pipx`:**
   - Install pipx using your package [manager](https://github.com/pypa/pipx?tab=readme-ov-file#on-linux).

### FocusTUI Installation (every OS)
Once you have `pipx` installed, you can easily install `FocusTUI`:

1. **Install `FocusTUI`:**
```bash
pipx install focustui
```

### Run the App
After installation, you can start `FocusTUI` by typing:
```bash
focustui
```

Note for macOS users: The first time you open the app, it may take up to 1 minute.
I’m not sure why, but during this initial launch, the app creates
folders, files, a database, and moves sounds to the app folder. This delay only
happens on the first launch. Apologies for the inconvenience.
