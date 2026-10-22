import sys
from pathlib import Path

from ml.core.config import Settings
from ml.training.loader import load_jamendo
from ml.training.train import train_jamendo
from ml.training.wrap_up import wrap_up_jamendo

BATCH_SIZE = 32


def main() -> None:
    root = Path(sys.argv[1])
    splits = root / "repo" / "data" / "splits" / "split-0"
    output_dir = str(root / "output")

    settings = Settings()

    load_jamendo(
        settings,
        train_file_path=str(splits / "autotagging_moodtheme-train.tsv"),
        valid_file_path=str(splits / "autotagging_moodtheme-validation.tsv"),
        test_file_path=str(splits / "autotagging_moodtheme-test.tsv"),
        moodtheme_file_path=str(root / "repo" / "data" / "autotagging_moodtheme.tsv"),
        audio_dir=str(root / "audio"),
        output_dir=output_dir,
        batch_size=BATCH_SIZE,
    )
    train_jamendo(settings, output_dir)
    wrap_up_jamendo(settings, output_dir)


if __name__ == "__main__":
    main()
