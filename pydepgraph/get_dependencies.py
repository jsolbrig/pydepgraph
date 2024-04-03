"""Functions for building a JSON dependency tree with package sizes."""

from pathlib import Path
import json
import subprocess


def get_deptree(package_name):
    """
    Get the dependency tree for a given package.

    Parameters
    ----------
    package_name : str
        The name of the package.

    Returns
    -------
    dict
        The dependency tree in JSON format.
    """
    # Use pip show command to get package information
    result = subprocess.run(
        ["pipdeptree", "--json-tree", "-p", package_name],
        capture_output=True,
        text=True,
    )
    deptree = json.loads(result.stdout)
    return deptree


def case_insensitive_startswith_search(directory, pattern):
    """
    Search for files in a directory that start with a given pattern, ignoring case.

    Parameters
    ----------
    directory : str
        The directory to search in.
    pattern : str
        The pattern to match at the start of the file names.

    Returns
    -------
    list
        A list of file paths that match the given pattern, ignoring case.
    """
    return [
        str(path)
        for path in Path(directory).glob("*")
        if path.name.lower().startswith(pattern.lower())
    ]


def kbytes_to_human_readable(num_kbytes):
    """
    Convert a number in kilobytes to a human-readable format.

    Parameters
    ----------
    num_kbytes : int or float
        The number of kilobytes to convert.

    Returns
    -------
    str
        The human-readable format of the input number, with the appropriate unit (KB,
        MB, GB, etc.).

    Examples
    --------
    >>> kbytes_to_human_readable(2048)
    '2MB'

    >>> kbytes_to_human_readable(1024)
    '1MB'

    >>> kbytes_to_human_readable(512)
    '512KB'
    """
    for unit in ["KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(num_kbytes) < 1024.0:
            return f"{int(num_kbytes)}{unit}"
        num_kbytes /= 1024.0
    return f"{num_kbytes:3d} YB"


def get_package_location(package_name):
    """
    Get the location of a package installed via pip.

    Parameters
    ----------
    package_name : str
        The name of the package.

    Returns
    -------
    str
        The location of the package.

    Raises
    ------
    ValueError
        If the package's location is not found.
    """
    # Use pip show command to get package information
    result = subprocess.run(
        ["pip", "show", package_name], capture_output=True, text=True
    )
    output = result.stdout

    # Parse the output to get the package location
    for line in output.splitlines():
        if line.startswith("Location:"):
            location = line.split(":")[1].strip()
            return location

    # Raise a ValueError if the package's location isn't found
    raise ValueError(f"Location not found for package: {package_name}")


def get_package_size(package_name):
    """
    Get the size of a package in human readable format.

    Parameters
    ----------
    package_name : str
        The name of the package.

    Returns
    -------
    str
        The size of the package in human-readable format.

    """
    # Get the location of the package
    location = get_package_location(package_name)

    # Use the du command to get the size of the directory and its contents
    package_dirs = case_insensitive_startswith_search(location, package_name)
    sizes = []
    for package_dir in package_dirs:
        result = subprocess.run(
            ["du", "-s", package_dir], capture_output=True, text=True
        )
        output = result.stdout
        # Parse the output to get the size
        sizes.append(int(output.split()[0]))
    size = kbytes_to_human_readable(sum(sizes))
    return size


def add_package_sizes(
    packages, _package_sizes={}, _pkg_ind=0, _cur_depth=-1, _is_root=True
):
    """
    Add package sizes to the given list of packages and their dependencies.

    Parameters
    ----------
    packages : list
        A list of dictionaries representing python packages as returned by pipdeptree.
    _package_sizes : dict, optional
        A dictionary containing the package sizes the sizes of packages that have
        already been collected. Defaults to an empty dictionary.
    _pkg_ind : int, optional
        The index of the current package. Defaults to 0.
    _cur_depth : int, optional
        The current depth of the package in the dependency tree. Defaults to -1.
    _is_root : bool, optional
        Indicates whether the current package is the root package. Defaults to True.

    Returns
    -------
    package_sizes : dict
        A dictionary containing the package sizes.
    _pkg_ind : int
        The index of the last processed package.
    """
    cur_depth = _cur_depth + 1
    for package in packages:
        if package["key"] not in _package_sizes:
            package_size = get_package_size(package["package_name"])
            _package_sizes[package["key"]] = package_size

        package["size"] = _package_sizes[package["key"]]

        print_line = ""
        if cur_depth >= 1:
            print_line = "|- "
        if cur_depth >= 2:
            print_line = "   " * (cur_depth - 2) + print_line
        print_line += f"{package['key']}:\t{package['size']}"
        print(print_line)

        _pkg_ind += 1

        if package.get("dependencies", None):
            _package_sizes, _pkg_ind = add_package_sizes(
                package["dependencies"],
                _package_sizes=_package_sizes,
                _pkg_ind=_pkg_ind,
                _cur_depth=cur_depth,
                _is_root=False,
            )

    if _is_root:
        return _package_sizes
    else:
        return _package_sizes, _pkg_ind


def get_deptree_with_sizes(
    package_name, cache_file=None, refresh=False, no_cache=False
):
    """
    Get the dependency tree for a given package with package sizes.

    Parameters
    ----------
    package_name : str
        The name of the package.

    cache_file : str, optional
        The file path to the dependencies cache file. If provided, the function will try
        to load the dependency tree from this file. If the file is not found, the
        function will collect the dependency tree and save it to this file.

    refresh : bool, optional
        If True, the function will always collect the dependency tree, even if it exists
        in the cache file. Defaults to False.

    no_cache : bool, optional
        If True, the function will not use the cache file and will always collect the
        dependency tree. Defaults to False.

    Returns
    -------
    dict
        The dependency tree in JSON format with package sizes.

    Raises
    ------
    FileNotFoundError
        If the provided `cache_file` is not found.

    Notes
    -----
    This function retrieves the dependency tree for a given package and adds package
    sizes to each node in the tree. The package sizes are calculated based on the size
    of the package files.

    If `cache_file` is provided, the function will try to load the dependency tree
    from this file. If the file is not found or `no_cache` is True, the function will
    collect the dependency tree and save it to this file.

    If `refresh` is True, the function will always collect the dependency tree, even if
    it exists in the cache file and update it in the cache file.

    Example
    -------
    >>> get_deptree_with_sizes('numpy', 'deps_cache.json', refresh=True)
    {'name': 'numpy', 'size': 1024, 'dependencies': [{'name': 'scipy', 'size': 512,
    'dependencies': []}]}
    """
    if cache_file and not no_cache:
        deptree = None

        # Load the dependency tree from the cache file unless we want to refresh it
        if not refresh:
            try:
                with open(cache_file, "r") as file:
                    deptree = json.load(file)[package_name]
            except (FileNotFoundError, KeyError):
                pass

        # Collect the dependency tree if it was not found in the cache or we want to
        # refresh it
        if not deptree:
            # Collect the dependency tree
            deptree = get_deptree(package_name)
            # Call the function with the loaded dependencies
            add_package_sizes(deptree)

        # Save the dependency tree to the cache file
        # Each package's dependencies are stored under a new key in the cache file
        try:
            with open(cache_file, "r") as file:
                cache_deptree = json.load(file)
        except FileNotFoundError:
            cache_deptree = {}
        cache_deptree[package_name] = deptree
        with open(cache_file, "w") as file:
            json.dump(cache_deptree, file, indent=2)

    # If no cache file is provided or we want to ignore the cache
    else:
        # Collect the dependency tree
        deptree = get_deptree(package_name)
        # Call the function with the loaded dependencies
        add_package_sizes(deptree)

    return deptree
