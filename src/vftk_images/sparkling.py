import pathlib

import attrs

from core import GenerateImage

containers_path = pathlib.Path(__file__).parent.absolute() / "containers"
images_path = pathlib.Path(__file__).parent.absolute() / "images"

@attrs.define
class SparklingImage(GenerateImage):



    def pipeline(self):
        """Build the complete Sparkling Apptainer image."""

        self.add_build_tools()

        self.system_libraries(
            libraries={
                "libgsl-dev": None,
                "libopenmpi-dev": None,
                "openmpi-bin": None,
            }
        )

        self.compile_source(
            commands=[
                "wget -q https://github.com/Kitware/CMake/releases/download/v4.2.3/cmake-4.2.3-linux-x86_64.sh -O /tmp/cmake.sh",
                "chmod +x /tmp/cmake.sh",
                "/tmp/cmake.sh --skip-license --prefix=/usr/local",
                "rm /tmp/cmake.sh",
                "cmake --version",
            ]
        )

        self.git_clone(
            repository_url="https://gitlab.com/andresruiz/Sparkling.git",
            branch="main",
            destination="/opt/Sparkling",
        )

        self.compile_source(
            commands=[
                "cd /opt/Sparkling",
                "rm -rf build",
                "mkdir build",
                "cd build",
                "cmake ..",
                "make -j$(nproc)",
            ]
        )

        self.add_env_vars(
            vars={
                "PATH": "/opt/Sparkling/build:$PATH",
            }
        )

        self.add_runscript(
            runscript=[
                "cd /opt/Sparkling",
                'exec "$@"',
            ]
        )

        self.add_labels(
            labels=[
                "Repository https://gitlab.com/andresruiz/Sparkling.git",
            ]
        )


# @attrs.define
# class SparklingImage(GenerateImage):

#     def pipeline(self):
#         """Build the complete Sparkling Apptainer image."""

#         # --------------------------------------------------------------
#         # System build dependencies
#         # --------------------------------------------------------------

#         self.add_build_tools()

#         self.system_libraries(
#             libraries={
#                 "libgsl-dev": None,
#                 "libopenmpi-dev": None,
#                 "openmpi-bin": None,
#                 "cmake": None
#             }
#         )

#         # --------------------------------------------------------------
#         # Sparkling source
#         # --------------------------------------------------------------

#         self.git_clone(
#             repository_url="https://gitlab.com/andresruiz/Sparkling.git",
#             branch="main",
#             destination="Sparkling"
#         )

#         # --------------------------------------------------------------
#         # Build Sparkling
#         # --------------------------------------------------------------

#         self.compile_source(
#             commands=[
#                 "cd /opt/Sparkling",
#                 "rm -rf build",
#                 "mkdir build",
#                 "cd build",
#                 "cmake ..",
#                 "make -j$(nproc)",
#             ]
#         )

#         # --------------------------------------------------------------
#         # Runtime environment
#         # --------------------------------------------------------------

#         self.add_env_vars(
#             vars={
#                 "PATH": "/opt/Sparkling/build:$PATH",
#             }
#         )

#         # --------------------------------------------------------------
#         # Container execution
#         # --------------------------------------------------------------

#         self.add_runscript(
#             runscript=[
#                 'cd /opt/Sparkling',
#                 'exec "$@"',
#             ]
#         )

#         # --------------------------------------------------------------
#         # Metadata
#         # --------------------------------------------------------------

#         self.add_labels(
#             labels=[
#                 "Repository https://gitlab.com/andresruiz/Sparkling.git",
#             ]
#         )

gen = SparklingImage(
    project_name="sparkling",
    version="0.0.2",
    workdir_def=containers_path,
    workdir_sif=images_path,
)

gen.pipeline()
gen.to_sif()
