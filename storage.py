"""File handling: read and write the two CSV files."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"
PODCAST_COLS = ["podcast", "category"]
EPISODE_COLS = ["podcast", "title", "date", "minutes", "rating"]


def load(path, columns):
    """Read one CSV. Missing or empty file gives an empty table."""
    try:
        table = pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=columns)
    if list(table.columns) != columns:
        raise ValueError(f"{Path(path).name} must have columns: {', '.join(columns)}")
    return table


def load_all():
    return (load(DATA / "podcasts.csv", PODCAST_COLS),
            load(DATA / "episodes.csv", EPISODE_COLS))


def save_all(podcasts, episodes):
    DATA.mkdir(exist_ok=True)
    podcasts.to_csv(DATA / "podcasts.csv", index=False)
    episodes.to_csv(DATA / "episodes.csv", index=False)
