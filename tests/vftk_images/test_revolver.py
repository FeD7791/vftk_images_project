import pathlib
import subprocess
import tempfile

from vftk_images.revolver import RevolverImage

# sudo apt install squashfuse PARA VER IMAGENES y usar apptainer shell

def test_revolver_image():

    with tempfile.TemporaryDirectory() as tempdir:

        tempdir = pathlib.Path(tempdir)

        gen = RevolverImage(
            os_from="ubuntu:20.04",
            project_name="revolver",
            version="0.0.1",
            workdir_def=tempdir,
            workdir_sif=tempdir,
        )

        gen.pipeline()
        gen.to_sif()

        subprocess.run(
            [
                "apptainer",
                "test",
                str(tempdir / "revolver_0.0.1.sif"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = subprocess.run(
            [
                "apptainer",
                "exec",
                str(tempdir / "revolver_0.0.1.sif"),
                "ls",
                "/opt/Revolver/src",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        print(result.stdout)


