import pathlib
import subprocess



def files(filepath, input_path, output_container_path):
    """Add a file or directory to the ``%files`` section.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    input_path : str or pathlib.PurePosixPath
        PurePosixPath to the source file or directory on the host.
    output_container_path : str or pathlib.PurePosixPath
        Destination directory inside the container.
    """
    _write_in_file(
        filepath=filepath,
        header="%files",
        line=f"{input_path} {output_container_path / input_path.name}"
    )


def build_sif(input_def_path, output_sif_path):
    """Build an Apptainer SIF image from a definition file.

    Parameters
    ----------
    input_def_path : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    output_sif_path : str or pathlib.PurePosixPath
        PurePosixPath where the generated SIF image will be written.

    Raises
    ------
    subprocess.CalledProcessError
        If the Apptainer build command exits with a non-zero status.
    """
    cmd = [
        "apptainer",
        "build",
        "--fakeroot",
        output_sif_path,
        input_def_path,
    ]

    subprocess.run(cmd, check=True)

def _write_in_file(filepath, header, line):
    """Insert a line at the end of an Apptainer definition section.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the definition file.
    header : str
        Section header where the line should be inserted.
    line : str
        Line to insert.
    """
    filepath = pathlib.Path(filepath)

    lines = filepath.read_text().splitlines()

    index = lines.index(header)

    # Buscar el final de la sección
    index += 1

    while index < len(lines) and not lines[index].startswith("%"):
        index += 1

    lines.insert(index, line)

    filepath.write_text("\n".join(lines) + "\n")


def write_values(filepath, header, lines):
    """Write one or more lines to an Apptainer definition section.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the definition file.
    header : str
        Section header where the values should be inserted.
    lines : str or list of str
        Line or lines to insert.
    """

    if isinstance(lines, str | pathlib.PurePosixPath):
        _write_in_file(filepath=filepath, header=header, line=str(lines))
    elif isinstance(lines, list):
        lines = list(map(str, lines))
        for line in lines:
            _write_in_file(filepath=filepath, header=header, line=line)
    else:
        raise ValueError(f"lines hould be either str or list got: {type(lines)}")

    


def add_python_library(filepath, packages:dict, python_path="/opt/python"):
    """Add Python packages to the container using ``uv``.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    packages : dict
        Mapping between package names and versions.
    python_path : str or pathlib.PurePosixPath, optional
        PurePosixPath to the Python virtual environment.
    """
    if not isinstance(packages, dict):
        raise ValueError("packages should be dict with package:version")
    for key, value in packages.items():
        line = _uv_install(package=key, version=value, python_path=python_path)
        _write_in_file(filepath=filepath, header="%post", line=line)




def install_python(filepath, version, path="/opt/python"):
    """Install Python and create a virtual environment.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    version : str
        Python version to install.
    path : str or pathlib.PurePosixPath, optional
        PurePosixPath where the Python virtual environment will be created.
    """

    _write_in_file(
        filepath=filepath,
        header="%post",
        line=f"apt-get install -y python{version} python{version}-dev\n"
    )
    _write_in_file(
        filepath=filepath,
        header="%post",
        line=f"python{version} -m venv {path}"
    )


def install_uv(filepath):
    """Install uv in the container.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        Path to the Apptainer definition file.
    """
    _write_in_file(
        filepath=filepath,
        header="%post",
        line=(
            "wget -qO- https://astral.sh/uv/install.sh "
            "| sh"
        ),
    )

    # Es necesario mover uv a /usr/local/bin o crear un enlace porque el
    # instalador lo coloca en /root/.local/bin, que no está necesariamente
    # incluido en el PATH durante el %post, por lo que el comando uv no puede ser
    # encontrado.

    _write_in_file(
        filepath=filepath,
        header="%post",
        line=(
            "mv /root/.local/bin/uv /usr/local/bin/uv"
        ),
    )


def _uv_install(package, version, python_path):
    """Generate a ``uv pip install`` command.

    Parameters
    ----------
    package : str
        Name of the Python package.
    version : str
        Package version.
    python_path : str or pathlib.PurePosixPath
        PurePosixPath to the Python environment.

    Returns
    -------
    str
        Shell command for installing the requested package.
    """
    return f'uv pip install --python {python_path}/bin/python "{package}=={version}"'


def install_build_tools(filepath):
    """Add the basic system build tools to the definition file.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    """
    _write_in_file(
        filepath=filepath, header="%post", line="apt-get update\n")

    _write_in_file(
        filepath=filepath,
        header="%post",
        line="apt-get install -y build-essential git wget ca-certificates")

    



def _install_system_library(filepath, package, version=None):
    """Add an APT system-library installation command.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    package : str
        Name of the APT package.
    version : str
        Version of the package to install.
    """
    if version is None:
        line = f"apt-get install -y {package}"
    else:
        line = f"apt-get install -y {package}={version}"

    _write_in_file(
        filepath=filepath,
        header="%post",
        line=line
    )

def system_libraries(filepath, packages:dict):
    """Add multiple system libraries to the definition file.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    packages : dict
        Mapping between package names and versions.
    """
    for key, value in packages.items():
        _install_system_library(
            filepath=filepath, package=key, version=value
        )


def add_post_environment(filepath, variables: dict):
    """Add environment variables to the ``%post`` section.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    variables : dict
        Mapping between environment variable names and values.
    """
    if not isinstance(variables, dict):
        raise ValueError("variables should be a dict")

    lines = [
        f"export {name}={value}"
        for name, value in variables.items()
    ]

    write_values(
        filepath=filepath,
        header="%post",
        lines=lines,
    )




def add_environment(filepath, variables: dict):
    """Add environment variables to the ``%environment`` section.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    variables : dict
        Mapping between environment variable names and values.
    """
    if not isinstance(variables, dict):
        raise ValueError("variables should be a dict")

    lines = [
        f"export {name}={value}"
        for name, value in variables.items()
    ]

    write_values(
        filepath=filepath,
        header="%environment",
        lines=lines,
    )


def clear_section(filepath, header):
    """Remove all lines from an Apptainer definition section.

    Parameters
    ----------
    filepath : str or pathlib.PurePosixPath
        PurePosixPath to the Apptainer definition file.
    header : str
        Section header whose contents should be removed.
    """
    filepath = pathlib.PurePosixPath(filepath)

    lines = filepath.read_text().splitlines()

    index = lines.index(header)

    # Comienza justo después del header
    start = index + 1

    # Buscar el siguiente header
    end = start
    while end < len(lines) and not lines[end].startswith("%"):
        end += 1

    # Borrar únicamente el contenido de la sección
    del lines[start:end]

    filepath.write_text("\n".join(lines) + "\n")


def git_clone(filepath, repository, destination, branch=None):
    if branch is None:
        command = f"git clone {repository} {destination}"
    else:
        command = f"git clone --branch {branch} {repository} {destination}"

    _write_in_file(
        filepath=filepath,
        header="%post",
        line=command,
    )


def compile_source(filepath, commands):

    if isinstance(commands, str):
        commands = [commands]

    if not isinstance(commands, list):
        raise ValueError("commands should be str or list")

    for command in commands:
        _write_in_file(
            filepath=filepath,
            header="%post",
            line=command,
        )


def add_testing(filepath, commands:list | str):
    write_values(
        filepath=filepath,
        header="%test",
        lines=commands,
    )