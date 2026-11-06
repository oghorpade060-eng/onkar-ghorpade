"""Download the public UCI corpus, verifying the exact data bytes."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

DATA_PATH = Path(__file__).parent / "data" / "SMSSpamCollection"
DATA_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
DATA_SHA256 = "7d039a24a6083ed9ef0f806ebad56bbb976e3aeb8de05669173bfdc4996c239d"


def download(destination=DATA_PATH):
    destination = Path(destination)
    if destination.exists():
        data = destination.read_bytes()
        if sha256(data).hexdigest() == DATA_SHA256:
            return destination
        raise ValueError("Existing dataset has a different checksum; inspect it before replacing it.")
    with urlopen(DATA_URL, timeout=60) as response:
        archive = response.read(2_000_001)
    if len(archive) > 2_000_000:
        raise ValueError("Unexpectedly large download.")
    with ZipFile(BytesIO(archive)) as bundle:
        data = bundle.read("SMSSpamCollection")
    if sha256(data).hexdigest() != DATA_SHA256:
        raise ValueError("Dataset checksum mismatch.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return destination


if __name__ == "__main__":
    print(f"Dataset ready: {download()}")
