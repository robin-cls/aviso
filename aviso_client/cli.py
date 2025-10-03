import logging
from dataclasses import asdict
from pathlib import Path

import numpy as np
import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

import aviso_client.core as ac_core
from aviso_client import InvalidProductError

app = typer.Typer()
console = Console()

logging.basicConfig(level=logging.WARNING, handlers=[RichHandler()])
logger = logging.getLogger('aviso_client')


@app.command()
def summary():
    """Summarizes CDS-AVISO and SWOT products from Aviso's catalog."""
    catalog = ac_core.summary()
    table = Table(title='Aviso Catalog')

    table.add_column('Id')
    table.add_column('Short Name')
    table.add_column('Title')

    for product in catalog.products:
        table.add_row(product.id, product.short_name or '', product.title
                      or '')

    console.print(table)


@app.command()
def details(product: str = typer.Option(...,
                                        '--product',
                                        '-p',
                                        help="Product's short name")):
    """Details a product information from Aviso's catalog."""
    try:

        product_info = ac_core.details(product)
        console.print(f"[bold underline]Product's details: {product}[/]\n")

        for key, value in asdict(product_info).items():
            console.print(f'[bold]{key}:[/] {value}')

    except InvalidProductError:
        raise typer.BadParameter(
            f"'{product}' doesn't exist in Aviso catalog. Please use 'summary' command to list available products."
        )


def _parse_value(value: str):
    """Tries to parse value to int or float."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


@app.command()
def get(product: str = typer.Option(...,
                                    '--product',
                                    '-p',
                                    help="Product's short name"),
        output: Path = typer.Option(...,
                                    '--output',
                                    '-o',
                                    help='Output directory'),
        filter: list[str] = typer.Option(
            [], '--filter', '-f', help='Dynamic filters as key=value.')):
    """Downloads a product from Aviso's Thredds Data Server..

    Example : get --product a_prod_short_name --output tmp_dir --filter cycle_number=7 --filter pass_number=12 --filter version=1.0
    """

    if not output.exists():
        raise typer.BadParameter(f"Directory '{output}' doesn't exist.")
    if not output.is_dir():
        raise typer.BadParameter(f"'{output}' is not a valid directory.")

    filters = {}
    for item in filter:
        if '=' not in item:
            raise typer.BadParameter(f"'{item}' filter is not key=value.")
        key, value = item.split('=', 1)
        filters[key] = _parse_value(value)

    start = filters.pop('start', None)
    end = filters.pop('end', None)

    if start or end:
        if not start:
            start = end
        if not end:
            end = start
        try:
            filters['time'] = (
                np.datetime64(start),
                np.datetime64(end),
            )
        except ValueError as e:
            raise typer.BadParameter(
                f"Invalid date format for 'start' or 'end': {e}")

    try:

        downloaded_files = ac_core.get(product_short_name=product,
                                       output_dir=output,
                                       **filters)

        console.print(
            f'[green]Downloaded files ({len(downloaded_files)}) :[/]')

        for file in downloaded_files:
            console.print(f'- {file}')

    except InvalidProductError:
        raise typer.BadParameter(
            f"'{product}' doesn't exist in Aviso catalog. Please use 'summary' command to list available products."
        )
