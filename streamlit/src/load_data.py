"""Carga dos cinco arquivos originais, sem ajustes manuais."""
# [IA] registro 3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('orders', 'order_items', 'products', 'sellers', 'order_reviews')


def load_data(folder=ROOT / 'data/raw'):
    folder = Path(folder)
    paths = [folder / f'olist_{name}_dataset.csv' for name in NAMES]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise ValueError(f'Arquivos ausentes em {folder}: {", ".join(missing)}')
    return tuple(pd.read_csv(p, dtype='string') for p in paths)
