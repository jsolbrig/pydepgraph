"""
This module contains functions for creating and visualizing dependency graphs.
"""

import math
import json
import networkx as nx
import matplotlib.pyplot as plt


def get_color(package):
    """
    Returns the color based on the size of the package.

    Parameters
    ----------
    package : dict
        The package information.

    Returns
    -------
    str
        The color corresponding to the package size.

    Notes
    -----
    The color is determined based on the size of the package. If the size is in KB,
    the color is determined as follows:
        - If the size is less than 10 KB, the color is "azure".
        - If the size is between 10 KB and 100 KB, the color is "lightcyan".
        - If the size is greater than or equal to 100 KB, the color is "paleturquoise".

    If the size is in MB, the color is determined as follows:
        - If the size is less than 10 MB, the color is "yellow".
        - If the size is between 10 MB and 100 MB, the color is "orange".
        - If the size is greater than or equal to 100 MB, the color is "hotpink".
    """
    num, order = package["size"][0:-2], package["size"][-2:]
    num = int(num)
    if order == "KB":
        if num < 10:
            return "azure"
        if num < 100:
            return "lightcyan"
        else:
            return "paleturquoise"
    if order == "MB":
        if num < 10:
            return "yellow"
        if num < 100:
            return "orange"
        else:
            return "hotpink"


def create_graph(dependencies, graph=None, parent_name=None, depth=-1):
    """
    Create a graph representation of package dependencies.

    Parameters
    ----------
    dependencies : list
        A list of dictionaries representing package dependencies.
    graph : nx.Graph, optional
        The graph object to add nodes and edges to. If not provided, a new graph will be created.
    parent_name : str, optional
        The name of the parent package. Used to create unique node names.
    depth : int, optional
        The depth of the current recursion. Used for indentation in print statements.

    Returns
    -------
    graph : nx.Graph
        The graph object with nodes and edges representing the package dependencies.
    """
    if graph is None:
        graph = nx.Graph()

    cur_depth = depth + 1

    for package in dependencies:
        print("| " * cur_depth + package["key"])

        if not parent_name:
            parent_name = ""
        name = f"{parent_name}-{package['key']}"
        graph.add_node(
            name,
            label=f"{package['key']}\n{package['size']}",
            size=package["size"],
            color=get_color(package),
        )
        if parent_name:
            graph.add_edge(parent_name, name)

        if "dependencies" in package:
            graph = create_graph(
                package["dependencies"],
                graph=graph,
                parent_name=name,
                depth=cur_depth,
            )
    return graph


def calculate_figure_size(graph):
    """
    Calculate the figure size based on the number of nodes in the graph.

    Parameters
    ----------
    graph : NetworkX graph
        The graph for which to calculate the figure size.

    Returns
    -------
    tuple
        A tuple containing the width and height of the figure.

    Notes
    -----
    The figure size is calculated based on the number of nodes in the graph.
    The base width and height are set to 8 and 6, respectively, for small graphs.
    The size is increased based on the number of nodes using a scaling factor of 0.1.
    The maximum size is capped at 100 for width and 40 for height.

    Examples
    --------
    >>> import networkx as nx
    >>> graph = nx.Graph()
    >>> graph.add_nodes_from([1, 2, 3, 4, 5])
    >>> calculate_figure_size(graph)
    (8.5, 6.6)
    """
    num_nodes = len(graph.nodes())
    base_width, base_height = 8, 6  # Base size for small graphs
    scaling_factor = 0.4  # Increase size based on the number of nodes

    # Cap the size to not exceed a maximum
    extra_width = min(100, base_width + scaling_factor * num_nodes)
    extra_height = min(40, base_height + scaling_factor * math.sqrt(num_nodes))

    return (extra_width, extra_height)


def draw_graph(deptree, save_path="deptree.png"):
    """
    Draw the dependency graph.

    Parameters
    ----------
    deptree : dict
        The dependency tree represented as a dictionary.
    save_path : str, optional
        The file path to save the graph image (default is "deptree.png").
    """
    print("Creating graph")
    graph = create_graph(deptree)

    print("Performing layout")
    pos = nx.drawing.nx_agraph.graphviz_layout(graph, prog="dot", root=0)

    print("Rescaling layout")
    pos = nx.rescale_layout_dict(pos, scale=3)

    plt.figure(figsize=calculate_figure_size(graph))

    print("Drawing nodes")
    colors = [color for color in nx.get_node_attributes(graph, "color").values()]
    nx.draw_networkx_nodes(graph, pos, node_shape="s", node_color=colors, node_size=500)

    print("Drawing edges")
    nx.draw_networkx_edges(graph, pos)

    print("Drawing labels")
    labels = nx.get_node_attributes(graph, "label")
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8)

    print("Saving")
    plt.axis("on")
    plt.savefig(save_path)


with open("matplotlib_deptree.json", "r") as dtree_data:
    dtree = json.loads(dtree_data.read())
