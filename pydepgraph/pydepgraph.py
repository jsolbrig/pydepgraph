"""
Provides functionality to create a dependency graph of a Python package.

The `pydepgraph` function can be used to create a dependency graph of a Python package.
The `main` function is the entry point of the script and handles command-line arguments.
"""

from argparse import ArgumentParser
from pydepgraph.get_dependencies import get_deptree_with_sizes
from pydepgraph.graph_dependencies import draw_graph


def pydepgraph(package, output_file, deps_cache_file=None):
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
    """
    deptree = get_deptree_with_sizes(package, deps_cache_file=deps_cache_file)
    draw_graph(deptree, output_file)


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
        "--deps_cache_file",
        type=str,
        default="deps_cache.json",
        help="The name of the file to cache the dependencies to.",
    )

    args = parser.parse_args()
    vargs = vars(args)

    pydepgraph(**vargs)
