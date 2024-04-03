"""
Provides functionality to create a dependency graph of a Python package.

The `pydepgraph` function can be used to create a dependency graph of a Python package.
The `main` function is the entry point of the script and handles command-line arguments.
"""

from argparse import ArgumentParser
from pydepgraph.get_dependencies import get_deptree_with_sizes
from pydepgraph.graph_dependencies import draw_graph


def pydepgraph(
    package,
    output_file,
    deps_cache_file=None,
    figsize=None,
    refresh=False,
    no_cache=False,
):
    """
    Create a dependency graph of a Python package.

    Parameters
    ----------
    package : str
        The name of the package to create the dependency graph for.
    output_file : str
        The name of the file to save the dependency graph to.
    deps_cache_file : str, optional
        The name of the file to cache the dependencies to. Defaults to None.
    figsize : tuple of int, optional
        Explicitly set the dimensions (width and height) of the graph in inches.
        If not provided, a reasonable figsize will be calculated based on the number of
        nodes in the graph.
    refresh : bool, optional
        Recompute the package's dependencies and replace in the cache file.
    no_cache : bool, optional
        Do not use the cache file for dependencies.
    """
    deptree = get_deptree_with_sizes(
        package, deps_cache_file=deps_cache_file, refresh=refresh, no_cache=no_cache
    )
    draw_graph(deptree, output_file, figsize=figsize)


def main():
    """Create a dependency graph of a Python package."""
    parser = ArgumentParser(
        description="Create a dependency graph of a Python package."
    )
    parser.add_argument(
        "package",
        type=str,
        help="The name of the package to create the dependency graph for.",
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="The name of the file to save the dependency graph to.",
    )
    parser.add_argument(
        "-c",
        "--cache-file",
        type=str,
        default="deps_cache.json",
        help=(
            "The name of the file to cache the dependencies to. "
            "All previous dependency trees will be cached to this file and reused when "
            "the same package is requested again. Defaults to 'deps_cache.json'."
        ),
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Recompute the package's dependencies and replace in the cache file.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not use the cache file for dependencies.",
    )
    parser.add_argument(
        "-f",
        "--figsize",
        type=int,
        nargs=2,
        help=(
            "Explicitly set the dimensions (width and height) of the graph in inches. "
            "If not provided, a reasonable figsize will be calculated based on the "
            "number of nodes in the graph."
        ),
    )

    args = parser.parse_args()
    vargs = vars(args)

    pydepgraph(**vargs)
