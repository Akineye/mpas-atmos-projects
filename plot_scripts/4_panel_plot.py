import os
import numpy as np
from netCDF4 import Dataset

import matplotlib as mpl
mpl.use('Agg')  # avoid display requirement
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap


# --------------------------
# Open lat/lon grid file
# --------------------------
grid = Dataset("/data/folorunshoa/mpas_practice/test_3km_tex/latlon.nc", 'r')

# Basemap projection
bmap = Basemap(projection='cyl',
               llcrnrlat=28.5,  urcrnrlat=30.5,
               llcrnrlon=-96.0, urcrnrlon=-94.5,
               resolution='l')

# Dimensions & variables
time = grid.dimensions['Time']
lats = list(map(float, grid.variables['latitude']))
lons = list(map(float, grid.variables['longitude']))

# Build meshgrid from lat/lon vectors
x, y = np.meshgrid(lons, lats)

# Extract surface pressure: shape = (time, lat, lon)
th2m = grid.variables['th2m'][:, :, :]
t2m = grid.variables['t2m'][:, :, :]
qv = grid.variables['qv'][:, 0, :, :]
rh = grid.variables['relhum'][:, 0, :, :]

qv = qv * 1000  #convert to g/kg

print("x:", x.shape)
print("y:", y.shape)
print("th2m:", th2m.shape)
print("qv:", qv.shape)

th2m_mean = np.mean(th2m, axis=0)
t2m_mean = np.mean(t2m, axis=0)
qv_mean = np.mean(qv, axis=0)
rh_mean = np.mean(rh, axis=0)


#Plot attributes
fields = [th2m_mean, t2m_mean, rh_mean, qv_mean]
colors = [cm.plasma,cm.viridis,cm.inferno,cm.viridis]
title = ["2-m Theta", "2-m Temperature", "Relative Humidity at Surface", "Water Vapor at Surface"]
labels = ["Theta (K)","Temperature (K)","Relative Humidity (%)","Water Vapor (g/kg)"]
max_value = [300.0, 305.0, 100, 20]
min_value = [280.0, 295.0, 0.0, 10]
incr_val = [2.5, 1.5, 10, 1]

# --------------------------
# Plot for each variable
# --------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for i in range(4):   # panel ind
    ax = axes[i]

    plt.sca(ax)
 
    N_COLOR_LEVELS = int((max_value[i] - min_value[i]) * 5)
    color_levels = np.linspace(min_value[i], max_value[i], N_COLOR_LEVELS)
    color_ticks = np.arange(min_value[i], max_value[i] + incr_val[i], incr_val[i])

    ax.set_title(title[i])

    # Map features
    bmap.drawcoastlines()
    bmap.drawstates()
    bmap.drawcountries()
    #bmap.readshapefile('/data/folorunshoa/mpas_practice/plots/tex_3km/us_county/tl_2022_us_county','counties',linewidth=0.3,color='gray')
    bmap.drawparallels(np.arange(29.0, 31.0, 0.5),
            linewidth=1, labels=[1,0,0,0], fmt="%.1f")
    bmap.drawmeridians(np.arange(-96.0, -94.5, 0.5),
            linewidth=1, labels=[0,0,0,1], fmt="%.1f")

    # Individual plot
    cs = bmap.contourf(
            x, y,
            fields[i],
            levels=color_levels,
            extend='both',
            cmap=colors[i],
            zorder=1
    )

    cbar = fig.colorbar(cs, ax=ax, shrink=0.7)
    cbar.set_label(labels[i])
    cbar.set_ticks(color_ticks)

# Save figure
filename = f"panel_met_mean.png"
plt.savefig(filename, dpi=150)
plt.close()
print("Saved:", filename)
