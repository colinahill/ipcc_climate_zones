import xarray as xr

# Reference grid
ref = xr.open_dataset("cru_ts4.07.2011.2020.tmp.dat.nc")

# Elevation - rename coords to match reference and interpolate, then write to disk
da = xr.open_dataarray("elevation_10KMmn_GMTEDmn.tif").rename({'x': 'lon', 'y': 'lat'}).drop(['band', 'spatial_ref']).squeeze('band')
da.name = 'elevation'
da = da.interp_like(ref, method='linear').rename('elevation')
da.to_netcdf("elevation_0.5deg.nc")