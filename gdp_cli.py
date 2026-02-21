import pandas as pd
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich import box
import math
import sys
import json

# --- Data Logic ---

def get_gdp_data():
    """Load and process GDP data from CSV."""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    if not DATA_FILENAME.exists():
        raise FileNotFoundError(f"Data file not found at {DATA_FILENAME}")

    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    # The columns are Country Name, Country Code, Indicator Name, Indicator Code, and then years.
    # We want to keep Country Name as well for searching.
    MIN_YEAR = 1960
    MAX_YEAR = 2022

    years = [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)]
    gdp_df = raw_gdp_df.melt(
        ['Country Name', 'Country Code'],
        years,
        'Year',
        'GDP',
    )
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

# --- UI Helpers ---

console = Console()

def print_header(title, subtitle=None):
    text = Text(title, style="bold cyan")
    if subtitle:
        text.append(f"\n{subtitle}", style="italic white")
    console.print(Panel.fit(text, border_style="blue", box=box.DOUBLE))

def format_gdp(val):
    if math.isnan(val):
        return "[dim]n/a[/dim]"
    if val >= 1e12:
        return f"{val/1e12:>6.2f} T"
    if val >= 1e9:
        return f"{val/1e9:>6.2f} B"
    if val >= 1e6:
        return f"{val/1e6:>6.2f} M"
    return f"{val:>6.2f}"

# --- Command Implementations ---

def do_view(args, df):
    countries = [c.strip().upper() for c in args.countries.split(',')]
    from_year = args.from_year or df['Year'].min()
    to_year = args.to_year or df['Year'].max()

    filtered = df[
        (df['Country Code'].isin(countries)) &
        (df['Year'] >= from_year) &
        (df['Year'] <= to_year)
    ]

    if filtered.empty:
        console.print("[bold red]No data found for selected criteria.[/bold red]")
        return

    print_header("GDP Detailed View", f"Range: {from_year} - {to_year}")

    table = Table(box=box.ROUNDED)
    table.add_column("Country", style="bold cyan")
    table.add_column("Code", style="dim")
    table.add_column(f"GDP {from_year}", justify="right")
    table.add_column(f"GDP {to_year}", justify="right")
    table.add_column("Growth", justify="right")
    table.add_column("Trend", justify="center")

    for code in countries:
        c_df = filtered[filtered['Country Code'] == code].sort_values('Year')
        if c_df.empty: continue

        name = c_df['Country Name'].iloc[0]
        v_start = c_df[c_df['Year'] == from_year]['GDP'].values
        v_end = c_df[c_df['Year'] == to_year]['GDP'].values

        g1 = v_start[0] if len(v_start) > 0 else float('nan')
        g2 = v_end[0] if len(v_end) > 0 else float('nan')

        growth_str = "[dim]-[/dim]"
        trend_str = "[dim]-[/dim]"
        if not math.isnan(g1) and not math.isnan(g2) and g1 > 0:
            ratio = g2 / g1
            color = "green" if ratio >= 1 else "red"
            growth_str = f"[{color}]{ratio:.2f}x[/{color}]"
            trend_str = "[green]↗[/green]" if ratio > 1.05 else ("[red]↘[/red]" if ratio < 0.95 else "[yellow]→[/yellow]")

        table.add_row(name, code, format_gdp(g1), format_gdp(g2), growth_str, trend_str)

    console.print(table)

def do_rank(args, df):
    year = args.year or df['Year'].max()
    metric = args.metric # 'gdp' or 'growth'

    print_header(f"Global Rankings ({year})", f"Metric: {metric.upper()}")

    if metric == 'gdp':
        rank_df = df[df['Year'] == year].dropna(subset=['GDP']).sort_values('GDP', ascending=False)
        top_df = rank_df.head(args.limit)

        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Rank", justify="right", style="dim")
        table.add_column("Country", style="bold")
        table.add_column("Code", style="cyan")
        table.add_column("GDP", justify="right", style="green")

        for i, (_, row) in enumerate(top_df.iterrows(), 1):
            table.add_row(str(i), row['Country Name'], row['Country Code'], format_gdp(row['GDP']))

    else: # growth
        prev_year = year - 1
        y_df = df[df['Year'] == year][['Country Code', 'Country Name', 'GDP']]
        py_df = df[df['Year'] == prev_year][['Country Code', 'GDP']]
        merged = pd.merge(y_df, py_df, on='Country Code', suffixes=('', '_prev')).dropna()
        merged['Growth'] = (merged['GDP'] / merged['GDP_prev']) - 1
        top_df = merged.sort_values('Growth', ascending=False).head(args.limit)

        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Rank", justify="right", style="dim")
        table.add_column("Country", style="bold")
        table.add_column("Growth Rate", justify="right", style="green")

        for i, (_, row) in enumerate(top_df.iterrows(), 1):
            table.add_row(str(i), row['Country Name'], f"{row['Growth']*100:+.2f}%")

    console.print(table)

def do_stats(args, df):
    countries = [c.strip().upper() for c in args.countries.split(',')]
    year = args.year or df['Year'].max()

    filtered = df[(df['Country Code'].isin(countries)) & (df['Year'] == year)].dropna(subset=['GDP'])

    if filtered.empty:
        console.print("[red]No data for statistics.[/red]")
        return

    stats = filtered['GDP'].describe()

    print_header("Aggregated Statistics", f"Year: {year} | Selection: {args.countries}")

    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")

    grid.add_row("Count:", f"{int(stats['count'])}")
    grid.add_row("Total GDP:", format_gdp(filtered['GDP'].sum()))
    grid.add_row("Mean GDP:", format_gdp(stats['mean']))
    grid.add_row("Median GDP:", format_gdp(stats['50%']))
    grid.add_row("Std Dev:", format_gdp(stats['std']))
    grid.add_row("Max:", f"{filtered.loc[filtered['GDP'].idxmax(), 'Country Name']} ({format_gdp(stats['max'])})")
    grid.add_row("Min:", f"{filtered.loc[filtered['GDP'].idxmin(), 'Country Name']} ({format_gdp(stats['min'])})")

    console.print(Panel(grid, border_style="magenta", title="Statistical Summary", title_align="left"))

def do_search(args, df):
    query = args.query.lower()
    unique_countries = df[['Country Name', 'Country Code']].drop_duplicates()
    results = unique_countries[unique_countries['Country Name'].str.lower().str.contains(query, na=False)]

    print_header(f"Search Results for '{args.query}'")

    if results.empty:
        console.print("[yellow]No countries found matching your query.[/yellow]")
        return

    table = Table(box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Country Name", style="bold cyan")
    table.add_column("Code", style="bold magenta")

    for _, row in results.iterrows():
        table.add_row(row['Country Name'], row['Country Code'])

    console.print(table)

def do_export(args, df):
    countries = [c.strip().upper() for c in args.countries.split(',')]
    filtered = df[df['Country Code'].isin(countries)]

    path = Path(args.output)
    if args.format == 'csv':
        filtered.to_csv(path, index=False)
    else:
        # Simplified JSON export - replace NaN with None for valid JSON
        data = filtered.replace({float('nan'): None}).to_dict(orient='records')
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    console.print(f"[bold green]Successfully exported data to {path}[/bold green]")

# --- Main Entry ---

def main():
    try:
        df = get_gdp_data()
    except Exception as e:
        console.print(f"[bold red]Critical Error:[/bold red] {e}")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description=":earth_americas: GDP Massive CLI - Ultimate World Economy Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # View Command
    view_parser = subparsers.add_parser('view', help='Detailed GDP view for countries')
    view_parser.add_argument('--countries', default='USA,CHN,JPN,DEU,IND,GBR', help='Comma separated country codes')
    view_parser.add_argument('--from-year', type=int, help='Start year')
    view_parser.add_argument('--to-year', type=int, help='End year')

    # Rank Command
    rank_parser = subparsers.add_parser('rank', help='Global rankings')
    rank_parser.add_argument('--year', type=int, help='Year to rank')
    rank_parser.add_argument('--metric', choices=['gdp', 'growth'], default='gdp', help='Metric to rank by')
    rank_parser.add_argument('--limit', type=int, default=10, help='Number of results')

    # Stats Command
    stats_parser = subparsers.add_parser('stats', help='Aggregated statistics')
    stats_parser.add_argument('--countries', default='WLD', help='Codes (WLD for world)')
    stats_parser.add_argument('--year', type=int, help='Year')

    # Search Command
    search_parser = subparsers.add_parser('search', help='Search for country codes')
    search_parser.add_argument('query', help='Search term for country name')

    # Export Command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument('--countries', required=True, help='Codes to export')
    export_parser.add_argument('--output', required=True, help='Output filename')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='File format')

    args = parser.parse_args()

    if args.command == 'view':
        do_view(args, df)
    elif args.command == 'rank':
        do_rank(args, df)
    elif args.command == 'stats':
        do_stats(args, df)
    elif args.command == 'search':
        do_search(args, df)
    elif args.command == 'export':
        do_export(args, df)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
