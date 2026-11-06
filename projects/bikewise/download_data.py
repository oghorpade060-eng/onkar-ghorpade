"""Download the original UCI archive and verify the exact hourly CSV used here."""
from io import BytesIO
import hashlib
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

SOURCE_URL = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"
EXPECTED_SHA256 = "e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f"
ROOT = Path(__file__).resolve().parent


def download(root=ROOT):
    folder = root / "data"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "hour.csv"
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == EXPECTED_SHA256:
        print("Dataset already present; SHA-256 verified.")
        return target
    with urlopen(SOURCE_URL, timeout=60) as response:
        archive = response.read(5_000_001)
    if len(archive) > 5_000_000:
        raise ValueError("Unexpected archive size; download was not accepted.")
    with ZipFile(BytesIO(archive)) as zipped:
        if zipped.getinfo("hour.csv").file_size > 3_000_000:
            raise ValueError("Unexpected CSV size.")
        data = zipped.read("hour.csv")
        if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
            raise ValueError("Dataset checksum changed. Review upstream before replacing the pinned dataset.")
        # Read known names only, rather than extracting arbitrary ZIP paths.
        temporary = folder / "hour.csv.part"
        temporary.write_bytes(data)
        temporary.replace(target)
        (folder / "Readme.txt").write_bytes(zipped.read("Readme.txt"))
    print(f"Downloaded and verified {len(data):,} bytes from UCI.")
    return target


if __name__ == "__main__":
    download()

