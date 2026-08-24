from pathlib import Path

from torch.utils.tensorboard import SummaryWriter


def create_writer(run_name: str, log_root: Path = Path("runs")) -> SummaryWriter:
    return SummaryWriter(log_dir=str(log_root / run_name))
