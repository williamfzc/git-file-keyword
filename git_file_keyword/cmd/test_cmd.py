from click.testing import CliRunner

from . import main


def test_main_function():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            "..",
            "--include",
            "**/*.py",
            # "--openai_key",
            # "xxx",
        ],
    )
    print(result)
