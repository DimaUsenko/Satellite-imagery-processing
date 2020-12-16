import rasterio
from rasterio import plot

import numpy as np

band_red = rasterio.open('LE07_L1TP_044034_20021222_20160927_01_T1_B3.tif')
band_nir = rasterio.open('LE07_L1TP_044034_20021222_20160927_01_T1_B4.tif')

red = band_red.read(1).astype('float64')
nir = band_nir.read(1).astype('float64')


ndvi=np.where((nir+red)==0.,0,(nir-red)/(nir+red))


ndviImage = rasterio.open('NDVI_RASTERIO.jpg','w',driver='Gtiff',
                          width=band_red.width,
                          height = band_red.height,
                          count=1, crs=band_red.crs,
                          transform=band_red.transform,
                          dtype='float64')
ndviImage.write(ndvi,1)
ndviImage.close()

ndvi = rasterio.open('NDVI_RASTERIO.jpg')
plot.show(ndvi,cmap='viridis',title='NDVI')
#plot.show(ndvi,cmap='RdYlGn',title='NDVI')
plot.show_hist(ndvi,  bins=50, lw=0.0, stacked=False, alpha=0.3,histtype='stepfilled', title="Histogram")
