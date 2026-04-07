import io
import sys

from src import utils


def test_setup_environment_prints_ascii_safe_console_messages(monkeypatch, tmp_path):
    stdout_buffer = io.BytesIO()
    ascii_stdout = io.TextIOWrapper(stdout_buffer, encoding="cp1252")

    monkeypatch.setattr(sys, "stdout", ascii_stdout)
    monkeypatch.setattr(utils, "OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setattr(utils, "set_random_seeds", lambda seed=utils.RANDOM_SEED: None)

    utils.setup_environment()
    ascii_stdout.flush()

    assert "Output directory:" in stdout_buffer.getvalue().decode("cp1252")
