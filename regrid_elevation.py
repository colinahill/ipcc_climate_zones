import xarray as xr
from pathlib import Path

data_dir = Path("data")

outfile = data_dir / "elevation_0.5deg.nc"
# Check if the output file already exists
if outfile.exists():
	print(f"Output file {outfile} already exists. Skipping regrid.")
	exit(0)

# Open reference grid (climate data)
ref = xr.open_dataset(data_dir / "cru_ts4.09.1971.1980.pet.dat.nc")

# Regrid elevation - rename coords to match reference and interpolate, then write to disk
da = (
	xr.open_dataarray(data_dir / "elevation_10KMmd_GMTEDmd.tif")
	.rename({'x': 'lon', 'y': 'lat'})
	.drop_vars(['band', 'spatial_ref'])
	.squeeze('band')
)
da.name = 'elevation'
da = da.interp_like(ref, method='linear').rename('elevation')
da.to_netcdf(outfile)