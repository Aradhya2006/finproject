from pathlib import Path
import shutil

RAW_DATA_DIR = Path("data/raw/nse")

def save_raw_file(source_path, symbol):
    source_path = Path(source_path)

    if not source_path.exists():
        raise FileNotFoundError(f"source file not found: {source_path}")



    if source_path.suffix.lower() != ".csv":
        raise ValueError("Expected a CSV file.")


    symbol_dir = RAW_DATA_DIR / symbol
    symbol_dir.mkdir(parents = True , exist_ok = True)


    destination = symbol_dir / source_path.name

    shutil.copy2(source_path, destination)

    return destination



def list_raw_files(symbol=None):
    if symbol:
        search_dir =  RAW_DATA_DIR / symbol

    else :
        search_dir = RAW_DATA_DIR 


    if not search_dir.exists():
        return []

    return sorted(search_dir.rglob("*.csv"))



