from pathlib import Path
import shutil
from datetime import datetime,timedelta
import time
import requests


RAW_DATA_DIR = Path("data/raw/nse")

NSE_BASE_URL = "https://www.nseindia.com"

NSE_HISTORICAL_URL = (
    f"{NSE_BASE_URL}/api/historicalOR/"
    "generateSecurityWiseHistoricalData"
)

NSE_PAGE_URL = (
    f"{NSE_BASE_URL}/historical/"
    "price-and-volume-data-per-security"
)


def create_nse_session():
    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": "text/csv,application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": NSE_PAGE_URL,
        "Connection": "keep-alive",
    })

    return session

def validate_date(date_string):
    """
    Validate an NSE date string in DD-MM-YYYY format.
    """

    try:
        datetime.strptime(
            date_string,
            "%d-%m-%Y",
        )
    except ValueError:
        raise ValueError(
            f"Invalid date: {date_string}. "
            "Expected format: DD-MM-YYYY."
        )

    return True


def validate_date_range(start_date, end_date):
    """
    Validate start and end dates.
    """

    validate_date(start_date)
    validate_date(end_date)

    start = datetime.strptime(
        start_date,
        "%d-%m-%Y",
    )

    end = datetime.strptime(
        end_date,
        "%d-%m-%Y",
    )

    if start > end:
        raise ValueError(
            "start_date cannot be after end_date."
        )

    return True


def validate_symbol(symbol):
    """
    Validate and normalize an NSE symbol.
    """

    if not isinstance(symbol, str):
        raise TypeError(
            "Symbol must be a string."
        )

    symbol = symbol.strip().upper()

    if not symbol:
        raise ValueError(
            "Symbol cannot be empty."
        )

    return symbol




def download_nse_data(symbol, start_date, end_date):
    symbol = validate_symbol(symbol)
    validate_date_range(start_date, end_date)

    params = {
        "symbol": symbol,
        "series": "EQ",
        "type": "priceVolumeDeliverable",
        "from": start_date,
        "to": end_date,
        "csv": "true",
    }

    session = create_nse_session()

    response = session.get(
        NSE_HISTORICAL_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type", ""
    ).lower()

    if "text/csv" not in content_type:
        raise ValueError(
            "NSE did not return CSV data. "
            f"Content-Type: {content_type}"
        )

    if not response.content:
        raise ValueError("NSE returned an empty response.")

    symbol_dir = RAW_DATA_DIR / symbol
    symbol_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"{symbol}_EQ_"
        f"{start_date}_"
        f"{end_date}.csv"
    )

    destination = symbol_dir / filename
    destination.write_bytes(response.content)

    return destination


def generate_six_month_ranges(start_date, end_date):
    """
    Generate six-month date ranges between start_date and end_date.
    """

    start = datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.strptime(end_date, "%d-%m-%Y")

    ranges = []

    current = start

    while current <= end:

        # Six-month chunk
        if current.month <= 6:
            chunk_end = current.replace(
                month=6,
                day=30,
            )
        else:
            chunk_end = current.replace(
                month=12,
                day=31,
            )

        # Don't go beyond requested end date
        chunk_end = min(chunk_end, end)

        ranges.append(
            (
                current.strftime("%d-%m-%Y"),
                chunk_end.strftime("%d-%m-%Y"),
            )
        )

        # Move to next six-month period
        if current.month <= 6:
            current = current.replace(
                month=7,
                day=1,
            )
        else:
            current = current.replace(
                year=current.year + 1,
                month=1,
                day=1,
            )

    return ranges





def download_full_history(
    symbol,
    start_date,
    end_date,
    delay_seconds=1,
    max_retries=3,
):
    """
    Download complete NSE historical data month by month.

    Existing monthly files are skipped.
    Failed downloads are retried.
    """

    symbol = validate_symbol(symbol)
    validate_date_range(start_date, end_date)

    six_month_ranges = generate_six_month_ranges(
        start_date,
        end_date
    )

    downloaded_files = []
    skipped_files = []
    failed_ranges = []

    total = len(six_month_ranges)

    symbol_dir = RAW_DATA_DIR / symbol
    symbol_dir.mkdir(parents=True, exist_ok=True)

    for index, (chunk_start, chunk_end) in enumerate(
        six_month_ranges,
        start=1
    ):

        filename = (
            f"{symbol}_EQ_"
            f"{chunk_start}_"
            f"{chunk_end}.csv"
        )

        destination = symbol_dir / filename

        print(
            f"[{index}/{total}] "
            f"{symbol}: "
            f"{chunk_start} → {chunk_end}"
        )

    
        if destination.exists():
            print("    SKIPPED: file already exists.")
            skipped_files.append(destination)
            continue

   
        success = False

        for attempt in range(1, max_retries + 1):

            try:

                file_path = download_nse_data(
                    symbol=symbol,
                    start_date=chunk_start,
                    end_date=chunk_end,
                )

                downloaded_files.append(file_path)

                print(
                    f"    SUCCESS "
                    f"(attempt {attempt})"
                )

                success = True
                break

            except Exception as error:

                print(
                    f"    Attempt {attempt} failed: "
                    f"{error}"
                )

                if attempt < max_retries:
                    time.sleep(2)

        
        if not success:

            print("    FAILED after all retries.")

            failed_ranges.append(
                (chunk_start, chunk_end)
            )

      
        if index < total:
            time.sleep(delay_seconds)


    print()
    print("=" * 50)
    print("DOWNLOAD SUMMARY")
    print("=" * 50)

    print(f"Downloaded : {len(downloaded_files)}")
    print(f"Skipped    : {len(skipped_files)}")
    print(f"Failed     : {len(failed_ranges)}")

    if failed_ranges:

        print()
        print("Failed ranges:")

        for start, end in failed_ranges:
            print(f"  {start} → {end}")

    return {
        "downloaded": downloaded_files,
        "skipped": skipped_files,
        "failed": failed_ranges,
    }




def save_raw_file(source_path, symbol):
    """
    Copy an existing NSE CSV into the project's
    raw data directory.
    """

    source_path = Path(source_path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {source_path}"
        )

    if source_path.suffix.lower() != ".csv":
        raise ValueError(
            "Expected a CSV file."
        )

    symbol = validate_symbol(symbol)

    symbol_dir = RAW_DATA_DIR / symbol

    symbol_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        symbol_dir / source_path.name
    )

    shutil.copy2(
        source_path,
        destination,
    )

    return destination


def list_raw_files(symbol=None):
    """
    List raw NSE CSV files stored in the project.
    """

    if symbol:
        symbol = validate_symbol(symbol)
        search_dir = RAW_DATA_DIR / symbol
    else:
        search_dir = RAW_DATA_DIR

    if not search_dir.exists():
        return []

    return sorted(
        search_dir.rglob("*.csv")
    )