import pandas as pd
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import math
import sys

def get_gdp_data():
    """Load and process GDP data from CSV."""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    if not DATA_FILENAME.exists():
        print(f"Error: Data file not found at {DATA_FILENAME}")
        sys.exit(1)

    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # Pivot year columns to long format
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

def main():
    parser = argparse.ArgumentParser(description=':earth_americas: GDP Dashboard CLI - Visualize World Bank GDP Data')
    parser.add_argument('--countries', type=str, default='DEU,FRA,GBR,BRA,MEX,JPN',
                        help='Comma-separated list of country codes (default: DEU,FRA,GBR,BRA,MEX,JPN)')
    parser.add_argument('--from-year', type=int, help='Start year (1960-2022)')
    parser.add_argument('--to-year', type=int, help='End year (1960-2022)')
    parser.add_argument('--list-countries', action='store_true', help='List all available country codes')

    args = parser.parse_args()
    console = Console()

    try:
        gdp_df = get_gdp_data()
    except Exception as e:
        console.print(f"[bold red]Error loading data:[/bold red] {e}")
        sys.exit(1)

    if args.list_countries:
        countries = sorted(gdp_df['Country Code'].unique())
        console.print(Panel(Text(", ".join(countries), style="cyan"), title="Available Country Codes"))
        return

    min_available_year = gdp_df['Year'].min()
    max_available_year = gdp_df['Year'].max()

    from_year = args.from_year if args.from_year is not None else min_available_year
    to_year = args.to_year if args.to_year is not None else max_available_year

    if from_year < min_available_year or to_year > max_available_year:
        console.print(f"[bold yellow]Warning:[/bold yellow] Requested years out of range ({min_available_year}-{max_available_year}). Clipping.")
        from_year = max(from_year, min_available_year)
        to_year = min(to_year, max_available_year)

    selected_countries = [c.strip().upper() for c in args.countries.split(',')]

    filtered_df = gdp_df[
        (gdp_df['Country Code'].isin(selected_countries))
        & (gdp_df['Year'] <= to_year)
        & (from_year <= gdp_df['Year'])
    ]

    if filtered_df.empty:
        console.print("[bold red]No data found[/bold red] for the selected countries and year range.")
        return

    # Header
    console.print(Panel.fit(
        f"[bold blue]GDP Dashboard[/bold blue]\n[italic]Showing data from {from_year} to {to_year}[/italic]",
        border_style="bright_blue"
    ))

    # Main Data Table
    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Country Code", style="cyan", no_wrap=True)
    table.add_column(f"GDP {from_year} (B$)", justify="right")
    table.add_column(f"GDP {to_year} (B$)", justify="right")
    table.add_column("Growth", justify="right")

    for country in selected_countries:
        country_data = filtered_df[filtered_df['Country Code'] == country]
        if country_data.empty:
            continue

        try:
            # First available year in range
            start_row = country_data[country_data['Year'] == from_year]
            end_row = country_data[country_data['Year'] == to_year]

            first_gdp = start_row['GDP'].iloc[0] / 1e9 if not start_row.empty else float('nan')
            last_gdp = end_row['GDP'].iloc[0] / 1e9 if not end_row.empty else float('nan')

            growth_text = Text("n/a", style="dim")
            if not math.isnan(first_gdp) and not math.isnan(last_gdp) and first_gdp != 0:
                growth_val = last_gdp / first_gdp
                color = "green" if growth_val >= 1 else "red"
                growth_text = Text(f"{growth_val:,.2f}x", style=color)

            table.add_row(
                country,
                f"{first_gdp:,.2f}" if not math.isnan(first_gdp) else "n/a",
                f"{last_gdp:,.2f}" if not math.isnan(last_gdp) else "n/a",
                growth_text
            )
        except Exception:
            continue

    console.print(table)
    console.print("\n[dim]Data source: World Bank Open Data[/dim]")

if __name__ == "__main__":
    main()
