"""Download the public input data required by this project's pipeline.

Source: Smirnov & Thurner (2017), Harvard Dataverse, doi:10.7910/DVN/SZA9YW.
The download is deliberately kept out of Git so a fresh clone stays lightweight.
Dataverse refuses Python's default user agent (HTTP 403), so the request names
this project instead. The SHA-256 check confirms the file is the one analysed.
"""
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "friendship_gpa" / "data.mat"
URL = "https://dataverse.harvard.edu/api/access/datafile/3007394"
SHA256 = "f9bcaffad1b8ede50fcf7afe875f6c664c0e06188043f85fde320b29d35b63b7"
USER_AGENT = "ECC3841-network-position-and-academic-performance (research download)"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists() and TARGET.stat().st_size > 0:
        print(f"Already present: {TARGET}")
    else:
        print(f"Downloading data.mat from {URL}")
        with urlopen(Request(URL, headers={"User-Agent": USER_AGENT}), timeout=120) as resp:
            TARGET.write_bytes(resp.read())
        print(f"Saved {TARGET} ({TARGET.stat().st_size:,} bytes)")
    digest = sha256(TARGET)
    if digest != SHA256:
        raise RuntimeError(f"data.mat checksum mismatch: expected {SHA256}, got {digest}")
    print("Checksum OK")


if __name__ == "__main__":
    main()
