# :earth_americas: GDP Dashboard CLI Guide

This guide provides instructions on how to install and run the optimized CLI version of the GDP Dashboard on Windows and macOS.

## :gear: Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
  - **Check version:** Run `python --version` (Windows) or `python3 --version` (macOS).

---

## :rocket: Installation

### 1. Prepare Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.

#### **Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### **macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
Install `pandas` and `rich` (used for the beautiful terminal UI).
```bash
pip install -r requirements.txt
```

---

## :terminal: Running the CLI

### **Basic Run**
Displays GDP growth for default countries (Germany, France, UK, Brazil, Mexico, Japan).
```bash
# Windows
python gdp_cli.py

# macOS / Linux
python3 gdp_cli.py
```

### **Advanced Options**

| Argument | Description | Example |
| :--- | :--- | :--- |
| `--countries` | Comma-separated ISO country codes | `--countries USA,CHN,CAN` |
| `--from-year` | Start year for comparison (1960+) | `--from-year 2000` |
| `--to-year` | End year for comparison (up to 2022) | `--to-year 2015` |
| `--list-countries` | Show all available country codes | `--list-countries` |

**Example of a custom query:**
```bash
python3 gdp_cli.py --countries USA,GBR,FRA --from-year 2010 --to-year 2022
```

---

## :bulb: Pro Tips
- Use the `--list-countries` flag to find the exact 3-letter code for any country you're interested in.
- The growth metric (`x`) shows how many times the GDP has increased from the start year to the end year.
- If a year is missing in the data, it will display as `n/a`.
