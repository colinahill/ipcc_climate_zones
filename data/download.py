import gzip
import urllib.request
from tqdm.auto import tqdm
import os


# CRU dataset
base_url = "https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/cruts.2304141047.v4.07/"
params = ["pet", "tmp", "pre", "frs"]
years = ["1971.1980", "1981.1990", "1991.2000", "2001.2010", "2011.2020"]

for param in tqdm(params):
    for year in tqdm(years, leave=False):
        url = base_url + param + "/cru_ts4.07." + year + "." + param + ".dat.nc.gz"
        outfile = "cru_ts4.07." + year + "." + param + ".dat.nc"

        # check if file already exists
        if os.path.exists(outfile):
            continue

        try:
            # Read the file inside the .gz archive located at url
            with urllib.request.urlopen(url) as response:
                with gzip.GzipFile(fileobj=response) as uncompressed:
                    file_content = uncompressed.read()

            # write to file in binary mode 'wb'
            with open(outfile, 'wb') as f:
                f.write(file_content)

        except Exception as e:
            print(e)