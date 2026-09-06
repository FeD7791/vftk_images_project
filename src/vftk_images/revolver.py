import pathlib

import attrs

from .core import GenerateImage

containers_path = pathlib.Path(__file__).parent.absolute() / "containers"
images_path = pathlib.Path(__file__).parent.absolute() / "images"

@attrs.define
class RevolverImage(GenerateImage):

    def pipeline(self):

        self.add_post_env_vars(
            {"DEBIAN_FRONTEND":"noninteractive"}
        )
        self.add_build_tools()

        self.system_libraries(
            libraries={
                "libgsl-dev": None,
                "libopenmpi-dev": None,
                "openmpi-bin": None,
            }
        )

        self.add_native_python() # 3.8 for ubuntu 20.04

        self.add_python_lib(
            {
                "astropy": "5.2.2",
                "asttokens": "3.0.1",
                "backcall": "0.2.0",
                "contourpy": "1.1.1",
                "cycler": "0.12.1",
                "Cython": "3.2.4",
                "decorator": "5.2.1",
                "executing": "2.2.1",
                "fonttools": "4.57.0",
                "healpy": "1.16.5",
                "importlib_resources": "6.4.5",
                "ipdb": "0.13.13",
                "ipython": "8.12.3",
                "jedi": "0.19.2",
                "kiwisolver": "1.4.7",
                "matplotlib": "3.7.5",
                "matplotlib-inline": "0.1.6",
                "numpy": "1.24.4",
                "packaging": "26.0",
                "parso": "0.8.7",
                "pexpect": "4.9.0",
                "pickleshare": "0.7.5",
                "pillow": "10.4.0",
                "prompt_toolkit": "3.0.52",
                "ptyprocess": "0.7.0",
                "pure_eval": "0.2.3",
                "pyerfa": "2.0.0",
                "pyFFTW": "0.13.1",
                "Pygments": "2.19.2",
                "pyparsing": "3.1.4",
                "python-dateutil": "2.9.0.post0",
                "PyYAML": "6.0.3",
                "scipy": "1.10.1",
                "six": "1.17.0",
                "stack-data": "0.6.3",
                "tomli": "2.4.1",
                "traitlets": "5.14.3",
                "typing_extensions": "4.13.2",
                "wcwidth": "0.7.0",
                "zipp": "3.20.2",
            }
        )


        self.git_clone(
            repository_url="https://github.com/FeD7791/Revolver.git",
            branch="main",
            destination="/opt/Revolver",
        )


        self.compile_source(
            commands=[
                "export PATH=/opt/python/bin:$PATH",
                "cd /opt/Revolver",
                "make clean",
                "make",
            ]
        )


        self.add_env_vars(
            vars={
                    "PATH": "/opt/python/bin:/usr/local/bin:$PATH",
                    "PYTHONPATH" : "/opt/Revolver:$PYTHONPATH",
                    "LC_ALL" : "C",
            }
        )

        self.add_runscript(
            runscript=[
                "cd /opt/Revolver",
                'exec "$@"',
            ]
        )

        # Los tests verifican que la instalación de Revolver se haya realizado
        # correctamente con soporte para MPI. En particular, comprueban que el
        # ejecutable voz1b1_mpi exista y sea ejecutable, que las herramientas de
        # OpenMPI (mpirun y mpicc) estén disponibles, y que el ejecutable MPI esté
        # correctamente enlazado con la librería libmpi.

        self.add_tests(
            commands=[
                "test -x /opt/Revolver/bin/voz1b1_mpi",
                "which mpirun",
                "which mpicc",
                "ldd /opt/Revolver/bin/voz1b1_mpi | grep -q libmpi",
            ]
        )


gen = RevolverImage(
    os_from="ubuntu:20.04",
    project_name="revolver",
    version="0.0.1",
    workdir_def=containers_path,
    workdir_sif=images_path,
)
