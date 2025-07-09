# Downloads the CRU dataset from the University of East Anglia Climate Research Unit
import gzip
import urllib.request
from tqdm.auto import tqdm
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

base_url = "https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.09/cruts.2503051245.v4.09"
params = ["pet", "tmp", "pre", "frs"]
years = ["1971.1980", "1981.1990", "1991.2000", "2001.2010", "2011.2020"]

for param in tqdm(params, desc="Downloading parameters", leave=True):
    for year in tqdm(years, desc="Downloading years", leave=False):
        outfile = data_dir / f"cru_ts4.09.{year}.{param}.dat.nc"
        # Check if file already exists
        if outfile.exists():
            continue

        url = f"{base_url}/{param}/cru_ts4.09.{year}.{param}.dat.nc.gz"
        try:
            # Read the file inside the .gz archive located at url
            with urllib.request.urlopen(url) as response:
                with gzip.GzipFile(fileobj=response) as uncompressed:
                    file_content = uncompressed.read()

            # Write to file
            with open(outfile, 'wb') as f:
                f.write(file_content)

        except Exception as e:
            print(e)