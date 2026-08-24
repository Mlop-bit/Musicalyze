from pathlib import Path

from ml.training.experiment_log import create_writer


def test_create_writer_produces_a_tensorboard_log_directory(tmp_path: Path) -> None:
    writer = create_writer("test-run", log_root=tmp_path)

    writer.add_scalar("loss", 0.5, 0)
    writer.flush()
    writer.close()

    run_dir = tmp_path / "test-run"
    assert run_dir.exists()
    assert any(run_dir.iterdir())
