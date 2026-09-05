import pathlib
import subprocess
import tempfile

from vftk_images.sparkling import SparklingImage


def test_sparkling_image():

    with tempfile.TemporaryDirectory() as tempdir:

        tempdir = pathlib.Path(tempdir)

        gen = SparklingImage(
            project_name="sparkling",
            version="0.0.2",
            workdir_def=tempdir,
            workdir_sif=tempdir,
        )

        gen.pipeline()
        gen.to_sif()

        subprocess.run(
            [
                "apptainer",
                "test",
                str(tempdir / "sparkling_0.0.2.sif"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


