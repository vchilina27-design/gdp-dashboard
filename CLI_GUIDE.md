# :earth_americas: GDP Dashboard MASSIVE CLI Guide

This guide provides instructions on how to install and run the ultimate, multi-command CLI version of the GDP Dashboard on Windows and macOS.

## :gear: Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
  - **Check version:** Run `python --version` (Windows) or `python3 --version` (macOS).

---

## :rocket: Installation

### 1. Prepare Environment
It is highly recommended to use a virtual environment.

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
```bash
pip install -r requirements.txt
```

---

## :terminal: Commands Overview

The massive CLI supports several subcommands for different types of analysis.

### **1. `view` - Detailed Country Data**
Displays a formatted table of GDP values and growth for specific countries.
```bash
python3 gdp_cli.py view --countries USA,CHN,IND --from-year 2010 --to-year 2022
```

### **2. `rank` - Global Economy Rankings**
Ranks countries globally by GDP or growth rate.
```bash
# Rank by GDP (Top 20 in 2021)
python3 gdp_cli.py rank --metric gdp --limit 20 --year 2021

# Rank by Growth (Top 10)
python3 gdp_cli.py rank --metric growth --limit 10
```

### **3. `stats` - Aggregate Statistics**
Calculates Mean, Median, Total GDP, and more for a selection of countries.
```bash
python3 gdp_cli.py stats --countries DEU,FRA,GBR --year 2020
```

### **4. `search` - Find Country Codes**
Search for the 3-letter ISO code using a country name.
```bash
python3 gdp_cli.py search "United"
```

### **5. `export` - Data Extraction**
Save filtered data to external files for further use.
```bash
python3 gdp_cli.py export --countries USA,CHN --output my_data.json --format json
```

---

## :bulb: Argument Reference

| Command | Argument | Description |
| :--- | :--- | :--- |
| `view` | `--countries` | Comma-separated ISO codes (e.g. `USA,GBR`) |
| `view` | `--from-year` | Start year for comparison (1960-2022) |
| `rank` | `--metric` | Choose between `gdp` and `growth` |
| `rank` | `--limit` | Number of results to display |
| `stats` | `--year` | The year to analyze |
| `export`| `--format` | Output file format: `csv` or `json` |

---

## :stars: Why this CLI is Awesome
- **Beautiful UI**: Uses `rich` for tables, panels, and colors.
- **Fast**: Leverages `pandas` for high-speed data processing.
- **Comprehensive**: Covers every year from 1960 to 2022 for hundreds of countries and regions.
