import os

from src.config import load_env_file


def test_env_file_sets_variables_that_are_not_already_set(tmp_path, monkeypatch):
    monkeypatch.setenv("RISKLENS_TEST_EXISTING", "from-terminal")
    monkeypatch.setenv("RISKLENS_TEST_NEW", "x")
    monkeypatch.delenv("RISKLENS_TEST_NEW")  # so the test restores the variable afterwards
    env_file = tmp_path / ".env"
    env_file.write_text(
        '# a comment\n'
        'RISKLENS_TEST_NEW="quoted value"\n'
        'RISKLENS_TEST_EXISTING=from-file\n',
        encoding="utf-8",
    )

    loaded = load_env_file(env_file)

    assert os.environ["RISKLENS_TEST_NEW"] == "quoted value"
    assert os.environ["RISKLENS_TEST_EXISTING"] == "from-terminal"
    assert loaded == ["RISKLENS_TEST_NEW"]


def test_missing_env_file_is_ignored(tmp_path):
    assert load_env_file(tmp_path / "missing.env") == []
