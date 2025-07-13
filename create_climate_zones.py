import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import rasterio.features
import geopandas as gpd
from shapely.geometry import shape
import rioxarray
import odc.geo.xr

data_dir = Path("data")
raster_outfile = data_dir / "ipcc_climate_zones.nc"
geotiff_outfile = data_dir / "ipcc_climate_zones.tif"
plot_outfile = data_dir / "ipcc_climate_zones.png"
vector_outfile = data_dir / "ipcc_climate_zones.geojson"

######### Load and prepare climate data #########
print("Loading climate data...")

start_year = 1985
end_year = 2015

# elevation [meters]
elevation = xr.open_dataset(data_dir / "elevation_0.5deg.nc")['elevation']

# tmp - monthly average daily mean temperature [deg Celsius] monthly
tmp_monthly = (
	xr.open_mfdataset(data_dir.glob("cru_ts4.09.*.tmp.dat.nc"), decode_timedelta=True)
	.sel(time=slice(str(start_year), str(end_year)))['tmp']
	.load()
)

# MAT: mean annual temperature [deg Celsius]
mat = tmp_monthly.mean(dim='time').rename('mat')

# pre - precipitation [mm/month] monthly
pre_monthly = (
	xr.open_mfdataset(data_dir.glob("cru_ts4.09.*.pre.dat.nc"), decode_timedelta=True)
	.sel(time=slice(str(start_year), str(end_year)))['pre']
	.load()
)

# MAP: mean annual precipitation [mm/year]
map = (pre_monthly.sum(dim='time') / (end_year - start_year)).rename('map')

# pet - potential evapotranspiration [mm/day] monthly
pet_monthly = (
	xr.open_mfdataset(data_dir.glob("cru_ts4.09.*.pet.dat.nc"), decode_timedelta=True)
	.sel(time=slice(str(start_year), str(end_year)))['pet']
	.load()
)
# multiply by days in month, mm/day -> mm/month
pet_monthly = pet_monthly * pet_monthly['time'].dt.days_in_month

# PET: mean annual potential evapotranspiration [mm/year]
# convert mm/month -> mm/year
pet = (pet_monthly.sum(dim='time') / (end_year - start_year)).rename('pet')

# frs - frost day frequency	[days] monthly
frs_monthly = (
	xr.open_mfdataset(data_dir.glob("cru_ts4.09.*.frs.dat.nc"), decode_timedelta=True)
	.sel(time=slice(str(start_year), str(end_year)))['frs']
	.load()
)
# convert timedelta to float64
one_day = np.timedelta64(1, 'D')
frs_monthly = (frs_monthly / one_day).astype('float64')

# FRS: mean annual frost day frequency [days/year]
# convert days/month -> days/year
frs = (frs_monthly.sum(dim='time') / (end_year - start_year))

# ratio MAP:PET
ratio_map_pet = map / pet

# ######### Compute climate zones #########
print("Computing climate zones...")

climate_zones = xr.DataArray(
	np.zeros(elevation.shape),
	dims=('lat', 'lon'),
	coords={'lat': elevation.lat, 'lon': elevation.lon},
	)

mask_0 = (mat > 18) & (frs <= 7)
mask_1 = elevation > 1000
mask_2 = map > 2000
mask_3 = (map <= 2000) & (map > 1000)
mask_4 = mat > 10
mask_5 = ratio_map_pet > 1
mask_6 = mat > 0
mask_7 = (tmp_monthly < 10).all(dim='time')
land_mask = mat.notnull()

# 1 - Tropical Montane
climate_zones = xr.where(
    mask_0 & mask_1,
    1, climate_zones
)

# 2 - Tropical Wet
climate_zones = xr.where(
    mask_0 & ~mask_1 & mask_2,
    2, climate_zones
    )

# 3 - Tropical Moist
climate_zones = xr.where(
    mask_0 & ~mask_1 & ~mask_2 & mask_3,
    3, climate_zones
    )

# 4 - Tropical Dry
climate_zones = xr.where(
    mask_0 & ~mask_1 & ~mask_2 & ~mask_3,
    4, climate_zones
    )

# 5 - Warm Temperate Moist
climate_zones = xr.where(
    ~mask_0 & mask_4 & mask_5,
    5, climate_zones
    )

# 6 - Warm Temperate Dry
climate_zones = xr.where(
    ~mask_0 & mask_4 & ~mask_5,
    6, climate_zones
    )

# 7 - Cool Temperate Moist
climate_zones = xr.where(
    ~mask_0 & ~mask_4 & mask_6 & mask_5,
    7, climate_zones
    )

# 8 - Cool Temperate Dry
climate_zones = xr.where(
    ~mask_0 & ~mask_4 & mask_6 & ~mask_5,
    8, climate_zones
    )

# 11 - Polar Moist
climate_zones = xr.where(
    ~mask_0 & ~mask_6 & ~mask_4 & mask_7 & mask_5,
    11, climate_zones
    )

# 12 - Polar Dry
climate_zones = xr.where(
    ~mask_0 & ~mask_6 & ~mask_4 & mask_7 & ~mask_5,
    12, climate_zones
    )

# 9 - Boreal Moist
climate_zones = xr.where(
    ~mask_0 & ~mask_6 & ~mask_4 & ~mask_7 & mask_5,
    9, climate_zones
    )

# 10 - Boreal Dry
climate_zones = xr.where(
    ~mask_0 & ~mask_6 & ~mask_4 & ~mask_7 & ~mask_5,
    10, climate_zones
    )

# 0 - no data
climate_zones = xr.where(land_mask, climate_zones, 0)

# Prepare the DataArray for writing to disk
climate_zones = climate_zones.rename('ipcc_climate_zone')

# Convert to int16
climate_zones = climate_zones.astype('int16')

description = (
	"IPCC Climate Zones 2019, defined on page 3.47 and 3.48 of" \
	"https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch03_Land" \
	"Representation.pdf, ammended with updates described at" \
	"https://www.ipcc-nggip.iges.or.jp/public/2019rf/corrigenda1.html"
)

mapping = {
    0: 'no data',
    1: 'Tropical Montane',
    2: 'Tropical Wet',
    3: 'Tropical Moist',
    4: 'Tropical Dry',
    5: 'Warm Temperate Moist',
    6: 'Warm Temperate Dry',
    7: 'Cool Temperate Moist',
    8: 'Cool Temperate Dry',
    9: 'Boreal Moist',
    10: 'Boreal Dry',
    11: 'Polar Moist',
    12: 'Polar Dry',
}

labels_string = ", ".join([f"{k}: {v}" for k, v in mapping.items()])

climate_zones = climate_zones.assign_attrs({
    "description": description,
    "Labels for climate zones": labels_string,
    })

crs = 'EPSG:4326'
climate_zones = climate_zones.odc.assign_crs(crs)

# Save as netcdf
climate_zones.to_netcdf(raster_outfile)
print(f"Raster saved to {raster_outfile}")

# Save as GeoTIFF
climate_zones.rename({'lon': 'x', 'lat': 'y'}).rio.to_raster(geotiff_outfile)
print(f"GeoTIFF saved to {geotiff_outfile}")

########## Plot the climate zones #########
print("Plotting climate zones...")
labels = list(mapping.values())
ticks = [i + 0.5 for i in range(13)]

fig, ax = plt.subplots(figsize=(16, 8))
climate_zones.plot(
	cmap=plt.get_cmap('viridis', 13),
	levels=range(14),
	cbar_kwargs={'ticks': ticks, 'pad': 0.02, 'label': 'IPCC Climate Zones'},
	ax=ax
)
cbar = ax.collections[0].colorbar
cbar.set_ticklabels(labels)
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('')
plt.savefig(plot_outfile, dpi=300, bbox_inches='tight')
print(f"Plot saved to {plot_outfile}")

######### Vectorise the raster data #########
print("Vectorising raster data...")

vectors = rasterio.features.shapes(
	source=climate_zones.data,
	transform=climate_zones.odc.transform,
)

# Extract the polygon coordinates and values from the vectors generator
polygons = []
values = []
for polygon, value in vectors:
	# Convert polygon coordinates into polygon shapes
	polygons.append(shape(polygon))
	values.append(value)

# Create a Geopandas GeoDataFrame populated with the polygons
gdf = gpd.GeoDataFrame(
	data={"climate_zone": values},
	geometry=polygons,
	crs=crs,
)

# Dissolve the GeoDataFrame by climate zone
gdf = gdf.dissolve(by='climate_zone').reset_index()

# Map the integer climate zone values to their string labels
gdf['climate_zone'] = gdf['climate_zone'].astype(int).map(mapping)

gdf.to_file(vector_outfile, driver='GeoJSON', index=False)
print(f"Vector data saved to {vector_outfile}")