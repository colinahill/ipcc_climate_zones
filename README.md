# IPCC Climate Zones

This repository allows creation of IPCC Climate Zones from raw data according to the 2019 definitions outlined in the [2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories](https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch03_Land%20Representation.pdf) pages 3.47 and 3.48, updated with [these ammendments](https://www.ipcc-nggip.iges.or.jp/public/2019rf/corrigenda1.html)


## Setup
* Install `pyenv` and set local env to Python 3.11
* Install `poetry`
* Install dependencies `poetry install` and run `poetry shell``
* Change directory to `data` with `cd data`
* Download CRU climate data `python download.py`
* Download and process elevation
    * Manually download 10km elevation from [Earth Env](https://www.earthenv.org/topography) to `data`
    * Regrid this to match the climate data `python regrid_elevation.py`
* Run notebooks to create the raster and vector layers
    * `cd ../` 
    * `poetry jupyter-lab`
    * In notebooks directory run `ipcc_cliamte_zones.ipynb` to aggregate climate data and apply the logic for classification, `vectorize_raster.ipynb` to convert the raster into vectors.