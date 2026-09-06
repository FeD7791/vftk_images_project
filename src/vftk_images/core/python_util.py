from .util import write_values

def install_native_python(filepath, path="/opt/python"):
    """
    Create a virtual environment using the system Python installation.

    Ubuntu 20.04 → Python 3.8
    Ubuntu 22.04 → Python 3.10
    Ubuntu 24.04 → Python 3.12

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        Path to the Apptainer definition file.
    path : str or pathlib.PurePosixPath, optional
        Path where the Python virtual environment will be created.
        Default is ``"/opt/python"``.

    Notes
    -----
    The system Python itself is not installed by this method. Only the
    ``python3-venv`` package is installed to provide the ``venv`` module.

    A symbolic link is also created so that ``python`` points to the
    system ``python3`` executable.
    """



    # Install the venv module required to create a virtual environment.
    write_values(
        filepath=filepath,
        header="%post",
        lines="apt-get update && apt-get install -y python3-venv python3.8-dev\n"
    )


    # Create the virtual environment using the system Python.
    write_values(
        filepath=filepath,
        header="%post",
        lines=f"python3 -m venv {path}"
    )