from click.testing import CliRunner

from . import main


def test_main_function():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--repo",
            "/Users/bytedance/workspace/bd/bear-web",
            "--include",
            "src/business/**/*.tsx",
            # "--openai_key",
            # "xxx",
        ],
    )
    print(result)
