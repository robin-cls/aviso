import logging
from dataclasses import asdict
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

import aviso_client.core as ac_core
from aviso_client import InvalidProductError

app = typer.Typer()
console = Console()

logging.basicConfig(level=logging.WARNING, handlers=[RichHandler()])
logger = logging.getLogger('aviso_client')


@app.command()
def summary():
    """Lists available products in Aviso's catalog."""
    catalog = ac_core.summary()
    table = Table(show_header=True,
                  header_style='bold magenta',
                  title='Aviso Catalog')

    table.add_column('Short Name', style='cyan')
    table.add_column('Title')

    products_sorted = sorted(catalog.products, key=lambda p: p.short_name)

    for product in products_sorted:
        table.add_row(product.short_name or '', product.title or '')

    console.print(table)


@app.command()
def details(product: str = typer.Argument(..., help="Product's short name")):
    """Details a product information from Aviso's catalog."""
    try:
        product_info = ac_core.details(product)

        table = Table(show_header=True, header_style='bold magenta')
        table.add_column('Field', style='cyan', width=25)
        table.add_column('Value', style='white')

        for key, value in asdict(product_info).items():
            table.add_row(key, str(value))

        console.print(
            Panel(table, title=f'[green]Product: {product}[/]', expand=False))

    except InvalidProductError:
        msg = (f"'{product}' doesn't exist in Aviso catalog. "
               "Please use 'summary' command to list available products.")
        raise typer.BadParameter(msg)


@app.command()
def get(
    product: str = typer.Argument(..., help="Product's short name"),
    output: Path = typer.Option(..., '--output', '-o',
                                help='Output directory'),
    cycle_number: list[int] = typer.Option(
        None, '--cycle', '-c', help='Cycle number (option can be repeated)'),
    pass_number: list[int] = typer.Option(
        None, '--pass', '-p', help='Pass number (option can be repeated)'),
    start: str = typer.Option(None, '--start', help='Start date (YYYY-MM-DD)'),
    end: str = typer.Option(None, '--end', help='End date (YYYY-MM-DD)'),
    version: str = typer.Option(
        None,
        '--version',
        '-v',
        help="Product's version. By default, last version is selected",
    ),
):
    """Downloads a product from Aviso's Thredds Data Server.

    Example : get a_prod_short_name --output tmp_dir
    --cycle 7 --pass 12 --pass 13 --pass 14 --version 1.0
    """
    if not output.exists():
        msg = f"Directory '{output}' doesn't exist."
        raise typer.BadParameter(msg)
    if not output.is_dir():
        msg = f"'{output}' is not a valid directory."
        raise typer.BadParameter(msg)

    try:
        downloaded_files = ac_core.get(
            product_short_name=product,
            output_dir=output,
            cycle_number=cycle_number if cycle_number else None,
            pass_number=pass_number if pass_number else None,
            time=(start, end),
            version=version,
        )

        console.print(
            f'[green]Downloaded files ({len(downloaded_files)}) :[/]')

        for file in downloaded_files:
            console.print(f'- {file}')

    except InvalidProductError:
        msg = (f"'{product}' doesn't exist in Aviso catalog."
               "Please use 'summary' command to list available products.")
        raise typer.BadParameter(msg)
