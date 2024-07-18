# App is almost production ready, readme will be updated on August 2024

### PoC Setup (Under 1 min)
1. Clone this project
   ``` bash
   git clone https://github.com/Zimzozaur/FocusKeeper-TUI
   ```
2. Move to project
    ```
    cd FocusKeeper-TUI
    ```
3. Create virtual env in project directory 
   ```
   python -m venv venv
   ```
4. Activate virtual env:
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
5. Install dependencies
   ```
   pip install -e .
   ```
6. Run app in terminal
   ```
    python focuskeeper
   ```