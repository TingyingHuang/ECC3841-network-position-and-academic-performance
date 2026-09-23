"""Download the public input data required by this project's pipeline.

Source: Smirnov & Thurner (2017), Harvard Dataverse, doi:10.7910/DVN/SZA9YW.
The download is deliberately kept out of Git so a fresh clone stays lightweight.
"""
from pathlib import Path
from urllib.request import urlretrieve


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "data" / "friendship_gpa" / "data.mat"
URL = "https://dataverse.harvard.edu/api/access/datafile/3007394"


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists() and TARGET.stat().st_size > 0:
        print(f"Already present: {TARGET}")
        return
    print(f"Downloading data.mat from {URL}")
    urlretrieve(URL, TARGET)
    if TARGET.stat().st_size == 0:
        raise RuntimeError("Downloaded data.mat is empty")
    print(f"Saved {TARGET} ({TARGET.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
