from abc import ABC
import pathlib

import attrs

from . import util


@attrs.define
class GenerateImage(ABC):
    """Generate and configure an Apptainer definition file.

    The class provides a high-level interface for creating an Apptainer
    definition file and adding files, Python installations, system
    libraries, environment variables, labels, and runtime commands.

    Parameters
    ----------
    _project_name : str
        Name of the software project for which the image is generated.
    _version : str
        Version identifier of the project.
    _workdir_def : str or pathlib.PurePosixPath
        Directory where the Apptainer definition file will be created.
    _workdir_sif : str or pathlib.PurePosixPath
        Directory where the resulting SIF image will be created.
    _basic_scheeme : list of str, optional
        Apptainer definition-file sections to include.
    _bootstrap : str, optional
        Bootstrap agent used to obtain the base image.
    _os_from : str, optional
        Base image used to construct the container.
    _apptainer_dir : str or pathlib.PurePosixPath, optional
        Directory inside the container where project files and software
        are installed.

    Notes
    -----
    The definition file is created during object initialization. The
    resulting file is named ``<project_name>_<version>.def``.
    """


    _project_name:str = attrs.field()
    _version:str = attrs.field()

    _workdir_def:str | pathlib.Path = attrs.field(converter=pathlib.Path)
    _workdir_sif:str | pathlib.Path = attrs.field(converter=pathlib.Path)

    _basic_scheeme:list[str] = attrs.field(
        default=[
            "%files",
            "%post",
            "%environment",
            "%runscript",
            "%test",
            "%labels"
        ]
    )

    _bootstrap:str = attrs.field(default="docker")
    _os_from:str = attrs.field(default="ubuntu:22.04") # Reasonable unless a vf needs another for compatibility
    _apptainer_dir:str = attrs.field(default="/opt", converter=pathlib.PurePosixPath)


    def __attrs_post_init__(self):
        """Initialize the Apptainer definition file.

        Creates the definition and SIF output paths, writes the definition
        file header and predefined sections, and adds the project name and
        version as labels.
        """
        self._workdir_def.mkdir(exist_ok=True, parents=True)
        self._workdir_sif.mkdir(exist_ok=True, parents=True)

        self._workdir_def = (
            self._workdir_def / f"{self._project_name}_{self._version}.def")
        
        self._workdir_sif = (
            self._workdir_sif / f"{self._project_name}_{self._version}.sif")


        with open(self._workdir_def, "w") as f:
            f.write(f"Bootstrap: {self._bootstrap}\n")
            f.write(f"From: {self._os_from}\n")
            for header in self._basic_scheeme:
                f.write(f"{header}\n")
        
        self.add_labels(labels=self._project_name)
        self.add_labels(labels=self._version)


    def add_files(self, input_path):
        """Add a file or directory to the ``%files`` section.

        Parameters
        ----------
        input_path : str or pathlib.PurePosixPath
        .PurePosixPath to the file or directory on the host system that should
            be copied into the container.

        Notes
        -----
        The destination inside the container is automatically constructed
        using ``_apptainer_dir`` and the name of ``input_path``.
        """

        input_path = pathlib.PurePosixPath(input_path)
    
        util.files(
            filepath=self._workdir_def,
            input_path=input_path,
            output_container_path=self._apptainer_dir / input_path.name
            )
        

    def add_python(self, python_version):
        """Add a Python installation to the container.

        Parameters
        ----------
        python_version : str
            Python version to install.
        """
        util.install_python(
            filepath=self._workdir_def,
            version=python_version,
            path=self._apptainer_dir
        )

    def add_python_lib(self, packages:dict):
        """Add Python packages to the container.

        Parameters
        ----------
        packages : dict
            Mapping between package names and their versions.

            The expected format is ``{package_name: version}``.
        """
        util.add_python_library(
            filepath=self._workdir_def,
            packages=packages,
            python_path=self._apptainer_dir / "python"
        )

    def add_build_tools(self):
        """Add the required system build tools to the container.

        Installs the ``build-essential`` package and updates the APT
        package index.
        """
        util.install_build_tools(
            filepath=self._workdir_def
        )

    def system_libraries(self, libraries:dict):
        """Add system libraries to the container.

        Parameters
        ----------
        libraries : dict
            Mapping between system package names and their versions.

            The expected format is ``{package_name: version}``.
        """
        util.system_libraries(
            filepath=self._workdir_def,
            packages=libraries
        )

    def add_env_vars(self, vars):
        """Add environment variables to the ``%environment`` section.

        Parameters
        ----------
        vars : dict
            Mapping between environment variable names and their values.

            For example, ``{"PATH": "/opt/bin:$PATH"}``.
        """
        util.add_environment(
            filepath=self._workdir_def,
            variables=vars
        )

    def add_runscript(self, runscript):
        """Add commands to the ``%runscript`` section.

        Parameters
        ----------
        runscript : str or list of str
            Command or commands executed when the container is invoked
            using ``apptainer run``.
        """
        util.write_values(
            filepath=self._workdir_def,
            header="%runscript",
            lines=runscript
        )

    def add_labels(self, labels):
        """Add metadata labels to the ``%labels`` section.

        Parameters
        ----------
        labels : str or list of str
            Label values to add to the definition file.
        """
        util.write_values(
            filepath=self._workdir_def,
            header="%labels",
            lines=labels
        )

    def to_sif(self):
        """Build the Apptainer SIF image.

        The definition file associated with this instance is passed to
        Apptainer using ``apptainer build --fakeroot``.
        """
        util.build_sif(
            self._workdir_def,
            self._workdir_sif
        )

    def clear_section(self, section):
        """Remove all contents from an Apptainer definition section.

        Parameters
        ----------
        section : str
            Name of the section to clear, for example ``"%post"`` or
            ``"%environment"``.
        """
        util.clear_section(
            filepath=self._workdir_def,
            header=section
        )

    def git_clone(self, repository_url, destination="repository", branch=None):
        util.git_clone(
            filepath=self._workdir_def,
            repository=repository_url,
            destination=self._apptainer_dir / destination,
            branch=branch

        )

    def compile_source(self, commands):
        util.compile_source(
            filepath=self._workdir_def, commands=commands
        )


    def add_tests(self, commands):
        util.add_testing(
            filepath=self._workdir_def,
            commands=commands
        )

