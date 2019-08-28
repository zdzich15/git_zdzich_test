#!/usr/bin/env python
# coding: utf-8

# In[54]:


import shapely.geometry
import pyproj
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import shapely
from shapely.ops import nearest_points
import numpy as np
from scipy import spatial


# In[35]:


get_ipython().run_cell_magic('prun', '', '# Set up projections\np_ll = pyproj.Proj(init=\'epsg:4326\')\np_mt = pyproj.Proj("+proj=eqdc +lat_0=39 +lon_0=-96 +lat_1=33 +lat_2=45 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs") #USA\n# p_mt=pyproj.Proj("+proj=eqdc +lat_0=30 +lon_0=10 +lat_1=43 +lat_2=62 +x_0=0 +y_0=0 +ellps=intl +units=m +no_defs") #PL\n\n#p_ll = pyproj.Proj(init=\'epsg:3857\')\n#p_mt = pyproj.Proj(init=\'epsg:4087\') # metric; same as EPSG:900913 3857\n#p_mt = pyproj.Proj(init=\'epsg:4979\')\n#p_mt = pyproj.Proj(init=\'esri:102031\')\n\n# Create corners of rectangle to be transformed to a grid\n#nw = shapely.geometry.Point((-5.0, 40.0))\n#se = shapely.geometry.Point((-4.0, 41.0))\n\n#nw = shapely.geometry.Point((55.053571, 13.709483))\n#se = shapely.geometry.Point((48.802844, 24.225555))\n\n#ws = shapely.geometry.Point((13.709483, 48.802844)) ok\n#en = shapely.geometry.Point((24.225555, 55.053571)) ok\n\n# sw = shapely.geometry.Point((48.555900, 10.846370)) #PL\n# ne = shapely.geometry.Point((54.821838, 26.158234)) #PL\n\n# sw = shapely.geometry.Point((24.873196,-126.613141)) #USA\n# ne = shapely.geometry.Point((41.921174, -103.527889)) #USA\n\nsw = shapely.geometry.Point((32.731125, -116.944403)) #USA SMALL\nne = shapely.geometry.Point((41.921174, -103.527889)) #USA SMALL\n\n# sw = shapely.geometry.Point((21.999586, -158.231030))\n# ne = shapely.geometry.Point((72.568437, 175.755116))\n\n#ws = shapely.geometry.Point((13.709483, 55.053571))\n#en = shapely.geometry.Point((24.225555, 48.802844))\n\nstepsize = 100000 # 50 km grid step size\n\n# Project corners to target projection\ns = pyproj.transform(p_ll, p_mt, sw.y, sw.x) # Transform NW point to 3857\ne = pyproj.transform(p_ll, p_mt, ne.y, ne.x) # .. same for SE\n\n# Iterate over 2D area\ngridpoints = []\nx = s[0]\nwhile x < e[0]:\n    y = s[1]\n    while y < e[1]:\n        p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))\n        gridpoints.append(p)\n        y += stepsize\n    x += stepsize\n\nwith open(r\'C:\\Users\\Zdzich\\Desktop\\GRID WORKING\\output\\testout4.csv\', \'w\') as of:\n    of.write(\'lat,lon\\n\')\n    for p in gridpoints:\n        of.write(\'{:f},{:f}\\n\'.format(p.y, p.x))\n        \nprint("Finished")')


# In[36]:


get_ipython().run_cell_magic('prun', '', "shp = gpd.read_file(r'C:\\Users\\Zdzich\\Desktop\\GRID WORKING\\grid\\countries_shp\\countries.shp')\n# filter_list = ['POL','CZE', 'SVK'] #PL\nfilter_list = ['USA'] #USA\n\nshp_filtered =  shp[shp.ISO3.isin(filter_list)]\nxmin, ymin, xmax, ymax = shp_filtered.total_bounds\nprint(ymin, xmin, ymax, xmax)\n#shp_filtered_buffer = shp_filtered.buffer(1)\n\n# shp_filtered_converted = shp_filtered.to_crs({'init': 'esri:102031'}) #PL\nshp_filtered_converted = shp_filtered.to_crs({'init': 'esri:102005'}) #USA\n\nbuffer_length_in_meters = (stepsize/3) \n#cpr_gdf['geometry'] = cpr_gdf.geometry.buffer(buffer_length_in_meters)\nshp_filtered_converted_buffer = shp_filtered_converted.buffer(buffer_length_in_meters)\n\n#type(shp_filtered)\nshp_filtered.plot()\nshp_filtered_converted_buffer.plot()\n\nshp_filtered_converted_buffer_crs = shp_filtered_converted_buffer.to_crs({'init': 'epsg:4326'})\nshp_filtered_converted_buffer_crs.plot()")


# In[37]:


get_ipython().run_cell_magic('prun', '', "df_grid = pd.read_csv(r'C:\\Users\\Zdzich\\Desktop\\GRID WORKING\\output\\testout4.csv')\ndf_grid['geometry'] = df_grid.apply(lambda row: Point(row.lon, row.lat), axis=1)\ndf_grid = gpd.GeoDataFrame(df_grid)\ndf_grid.geometry\n\n# points = gpd.GeoDataFrame(gridpoints)\n# points_geometry = points.rename(columns={0: 'geometry'})\n\nshps = gpd.GeoDataFrame(shp_filtered_converted_buffer_crs)\nshps_geometry = shps.rename(columns={0: 'geometry'})")


# In[38]:


get_ipython().run_cell_magic('prun', '', "intersection = gpd.sjoin(df_grid, shps_geometry, op='intersects')\nintersection.plot()")


# In[236]:


get_ipython().run_cell_magic('prun', '', "df_zip = pd.read_csv(r'C:\\Users\\Zdzich\\Desktop\\GRID WORKING\\USA_ZIPS.csv')\ndf_zip['geometry'] = df_zip.apply(lambda row: Point(row.lon, row.lat), axis=1)\ndf_zip = gpd.GeoDataFrame(df_zip)\n\ndf_zip.plot()")


# In[237]:


get_ipython().run_cell_magic('prun', '', "\n# unary_union_grid = df_grid.unary_union\nunary_union = df_zip.unary_union\n# print(unary_union_grid)\nprint(unary_union)\nunary_union.set_index('geometry', 'ZIP')")


# In[238]:


df_grid.geometry
df_grid.head()
df_grid.set_index('geometry')


# In[41]:


def nearest(row, geom_union, df1, df2, geom1_col='geometry', geom2_col='geometry', src_column=None):
    """Find the nearest point and return the corresponding value from specified column."""
    # Find the geometry that is closest
    nearest = df2[geom2_col] == nearest_points(row[geom1_col], geom_union)[1]
    # Get the corresponding value from df2 (matching is based on the geometry)
    value = df2[nearest][src_column].get_values()[int(0)]
    print('Found')
    return value


# In[57]:


get_ipython().run_cell_magic('prun', '', "df_grid['nearest_id'] = df_grid.apply(nearest, geom_union=unary_union, df1=df_grid, df2=df_zip, geom1_col='geometry', src_column='ZIP', axis=1)\ndf_grid.head(20)")


# In[239]:


df_grid


# In[118]:


# def find_idx_nearest_val(array, value):
#     idx_sorted = np.sort(array)
#     sorted_array = np.array(array[idx_sorted])
#     idx = np.searchsorted(sorted_array, value, side="left")
#     if idx >= len(array):
#         idx_nearest = idx_sorted[len(array)-1]
#     elif idx == 0:
#         idx_nearest = idx_sorted[0]
#     else:
#         if abs(value - sorted_array[idx-1]) < abs(value - sorted_array[idx]):
#             idx_nearest = idx_sorted[idx-1]
#         else:
#             idx_nearest = idx_sorted[idx]
#     return idx_nearest


# In[119]:


# find_idx_nearest_val(array_zip,df_grid)


# In[240]:


# df_zip = df_zip.set_index("ZIP")

array_zip = np.array(df_zip[['lat','lon']])
array_zip

# array_zip = (df_zip['lat'],df_zip['lon'])


# In[241]:


df_zip


# In[242]:


array_zip = np.array(df_zip[['lat','lon']])
points_list = list(array_zip)
points_list


# In[243]:


array_grid = np.array(df_grid[['lat','lon']])
array_grid


# In[244]:


# Shoe-horn existing data for entry into KDTree routines

def do_kdtree(points_list,array_grid):
    mytree = scipy.spatial.cKDTree(array_grid)
    dist, indexes = mytree.query(points_list)
    return indexes


# In[246]:


get_ipython().run_cell_magic('prun', '', 'results2 = do_kdtree(array_grid,points_list)\n# print(list(results2)')


# In[247]:


zip_matrix = pd.DataFrame(results2)
print(zip_matrix)


# In[248]:


zip_matrix.columns = ['index']
zip_matrix.set_index('index')
print(zip_matrix)

# f.reset_index(drop=True)
# f.index.name = 'foo'


# In[249]:


df_grid_and_zips = df_grid.join(zip_matrix)
df_grid_and_zips


# In[250]:


df_grid_and_zips.join(df_zip, lsuffix='_grid', rsuffix='_zip', on='index')


# In[ ]:




