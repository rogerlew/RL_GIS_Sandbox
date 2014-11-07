#ydalinfo
A gdalinfo replacement that provides extents, stemleaf band histogram, JSON 
output and is callable from python.

###Synopsis

    ydalinfo [--help-general] [-mm] [-nostats] [-stemleaf] [-nogcp] [-nomd]
             [-norat] [-noct] [-nofl] [-checksum] [-mdd domain]* datasetname

###Option Descriptions

<dl>
  <dt>-mm</dt>
  <dd>Force computation of the actual min/max values for each band in the dataset</dd>

  <dt>-nostats</dt>
  <dd>Suppresses the computation if no statistics are stored in an image</dd>
  
  <dt>-stemleaf</dt>
  <dd>Produces a stem and leaf histogram for each band</dd>
  
  <dt>-nostats</dt>
  <dd>Suppresses the computation if no statistics are stored in an image</dd>
  
  <dt>-nogcp</dt>
  <dd>Suppress ground control points list printing. It may be useful for datasets
    with huge amount of GCPs, such as L1B AVHRR or HDF4 MODIS which contain
    thousands of them.</dd>
  
  <dt>-nomd</dt>
  <dd>Suppress metadata printing. Some datasets may contain a lot of metadata
    strings.</dd>
  
  <dt>-norat</dt>
  <dd>Suppress printing of raster attribute table</dd>
  
  <dt>-noct</dt>
  <dd>Suppress printing of color table</dd>
  
  <dt>-nofl</dt>
  <dd>(GDAL >= 1.9.0) Only display the first file of the file list</dd>
  
  <dt>-checksum</dt>
  <dd>Force computation of the checksum for each band in the dataset</dd>
  
  <dt>-listmdd</dt>
  <dd>(GDAL >= 1.11) List all metadata domains available for the dataset</dd>
  
  <dt>-mdd domain</dt>
  <dd>Report metadata for the specified domain. Starting with GDAL 1.11, "all" 
      can be used to report metadata in all domains</dd>
</dl>
 
###Example Usage

    D:\...>ydalinfo.py AgeoTiffFile.tif
    Driver: GTiff/GeoTIFF
    Files: AgeoTiffFile.tif
           AgeoTiffFile.tif.aux.xml
    Size is 2000, 1272
    Coordinate System is:
    GEOGCS["NAD83",
        DATUM["North_American_Datum_1983",
            SPHEROID["GRS 1980",6378137,298.2572221010002,
                AUTHORITY["EPSG","7019"]],
            TOWGS84[0,0,0,0,0,0,0],
            AUTHORITY["EPSG","6269"]],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433],
        AUTHORITY["EPSG","4269"]]
    Origin = (-116.771229116629925,47.766431568303531)
    Pixel Size = (0.000092600467652,-0.000092579260068)
    Metadata:
      AREA_OR_POINT=Area
    IMAGE_STRUCTURE:
      INTERLEAVE=BAND
    Corner Coordinates:
    Upper Left  (-116.7712291,  47.7664316) (116d46'16.42"W, 47d45'59.15"N)
    Lower Left  (-116.7712291,  47.6486707) (116d46'16.42"W, 47d38'55.21"N)
    Upper Right (-116.5860282,  47.7664316) (116d35' 9.70"W, 47d45'59.15"N)
    Lower Right (-116.5860282,  47.6486707) (116d35' 9.70"W, 47d38'55.21"N)
    Center      (-116.6786286,  47.7075512) (116d40'43.06"W, 47d42'27.18"N)
    Band 1 Block=2000x1 Type=Float32, ColorInterp=Gray
      Description = ned10m_01
      Min=648.742 Max=1464.331
      Minimum=648.742, Maximum=1464.331, Mean=864.296, StdDev=174.992
      NoData Value=-3.4028234663852886e+38
      Metadata:
        LAYER_TYPE=athematic
        STATISTICS_MAXIMUM=1464.3306884766
        STATISTICS_MEAN=864.29576737852
        STATISTICS_MINIMUM=648.74151611328
        STATISTICS_STDDEV=174.99244854215
    
    D:\...>
    
    
###Stem and Leaf Band Histograms
    
    D:\...>ydalinfo.py AgeoTiffFile.tif -stemleaf                      
    Driver: GTiff/GeoTIFF                                                                                                   
    Files: AgeoTiffFile.tif                                                                                       
           AgeoTiffFile.tif.aux.xml                                                                               
    Size is 2000, 1272                                                                                                      
    Coordinate System is:                                                                                                   
    GEOGCS["NAD83",                                                                                                         
        DATUM["North_American_Datum_1983",                                                                                  
            SPHEROID["GRS 1980",6378137,298.2572221010002,                                                                  
                AUTHORITY["EPSG","7019"]],                                                                                  
            TOWGS84[0,0,0,0,0,0,0],                                                                                         
            AUTHORITY["EPSG","6269"]],                                                                                      
        PRIMEM["Greenwich",0],                                                                                              
        UNIT["degree",0.0174532925199433],                                                                                  
        AUTHORITY["EPSG","4269"]]                                                                                           
    Origin = (-116.771229116629925,47.766431568303531)                                                                      
    Pixel Size = (0.000092600467652,-0.000092579260068)                                                                     
    Metadata:                                                                                                               
      AREA_OR_POINT=Area                                                                                                    
    IMAGE_STRUCTURE:                                                                                                        
      INTERLEAVE=BAND                                                                                                       
    Corner Coordinates:                                                                                                     
    Upper Left  (-116.7712291,  47.7664316) (116d46'16.42"W, 47d45'59.15"N)                                                 
    Lower Left  (-116.7712291,  47.6486707) (116d46'16.42"W, 47d38'55.21"N)                                                 
    Upper Right (-116.5860282,  47.7664316) (116d35' 9.70"W, 47d45'59.15"N)                                                 
    Lower Right (-116.5860282,  47.6486707) (116d35' 9.70"W, 47d38'55.21"N)                                                 
    Center      (-116.6786286,  47.7075512) (116d40'43.06"W, 47d42'27.18"N)                                                 
    Band 1 Block=2000x1 Type=Float32, ColorInterp=Gray                                                                      
      Description = ned10m_01                                                                                               
      Min=648.742 Max=1464.331                                                                                              
      Minimum=648.742, Maximum=1464.331, Mean=864.296, StdDev=174.992                                                       
    Stem leaf histogram:                                                                                                    
         | 000000000000000000000011222333444445555556667777788889999                                                        
       1 | 000000001111111111111111111111111111111111111111222222222333333333444444455555666666777788889999                 
       2 | 00011112222333334444555566666777778888899999                                                                     
       3 | 0000001111122222333333444444555556666677777788888899999                                                          
       4 | 000001111112222223333344444555555666666677777888888999999                                                        
       5 | 000001111222223333344444555556666677777888889999                                                                 
       6 | 0000011111222233334444455555666677778888899999                                                                   
       7 | 0000111122223333444555666777888999                                                                               
       8 | 000111222333444555666777888999                                                                                   
       9 | 00011122233344455566677888999                                                                                    
      10 | 000112233445566778899                                                                                            
      11 | 00112233445566778899                                                                                             
      12 | 00112233445566778899                                                                                             
      13 | 001122334456789                                                                                                  
      14 | 0123456789                                                                                                       
      15 | 0123456789                                                                                                       
      16 | 0123456789                                                                                                       
      17 | .........                                                                                                        
      18 | .......                                                                                                          
      19 | ......                                                                                                           
      20 | ......                                                                                                           
      21 | ....                                                                                                             
      22 | ...                                                                                                              
      23 | ..                                                                                                               
      24 | ..                                                                                                               
      25 |                                                                                                                  
      Stem multiplier = 3507                                                                                                
      . = sum(10xbins) / Stem multiplier                                                                                    
      NoData Value=-3.4028234663852886e+38                                                                                  
      Metadata:                                                                                                             
        LAYER_TYPE=athematic                                                                                                
        STATISTICS_MAXIMUM=1464.3306884766                                                                                  
        STATISTICS_MEAN=864.29576737852                                                                                     
        STATISTICS_MINIMUM=648.74151611328                                                                                  
        STATISTICS_STDDEV=174.99244854215                                                                                   
                                                                                                                            
    D:\...>                   
    
###JSON Output

    D:\...>ydalinfo.py AgeoTiffFile.tif -json
    
###Python Usage

```python
>>> from ydalinfo import ydalinfo
>>> gdict = ydalinfo('AgeoTiffFile.tif')
>>> from pprint import pprint
>>> pprint(gdict)
{'Bands': [{'BandNum': 1,
            'BlockSize': (2000, 1),
            'Categories:': None,
            'CheckSum': 43262,
            'ColorInterp': 'Gray',
            'ColorTable': None,
            'Description': 'ned10m_01',
            'MaskFlags': 8,
            'Maximum': 1464.3306884766,
            'Metadata': {'LAYER_TYPE': 'athematic',
                         'STATISTICS_MAXIMUM': '1464.3306884766',
                         'STATISTICS_MEAN': '864.29576737852',
                         'STATISTICS_MINIMUM': '648.74151611328',
                         'STATISTICS_STDDEV': '174.99244854215'},
            'Minimum': 648.74151611328,
            'NoDataValue': -3.4028234663852886e+38,
            'RAT': None,
            'Type': 'Float32',
            'UnitType': ''}],
 'CoordinateSystem': {'GEOGCS': ['NAD83',
                                 {'AUTHORITY': ['EPSG', '4269'],
                                  'DATUM': ['North_American_Datum_1983',
                                            {'AUTHORITY': ['EPSG',
                                                           '6269'],
                                             'SPHEROID': ['GRS 1980',
                                                          6378137,
                                                          298.2572221010002,
                                                          {'AUTHORITY': ['EPSG',
                                                                         '7019']}],
                                             'TOWGS84': [0,
                                                         0,
                                                         0,
                                                         0,
                                                         0,
                                                         0,
                                                         0]}],
                                  'PRIMEM': ['Greenwich', 0],
                                  'UNIT': ['degree', 0.0174532925199433]}]},
 'CornerCoordinates': {'LowerLeft': (-116.77122911662993, 47.64867074949666),
                       'LowerRight': (-116.58602818132573, 47.64867074949666),
                       'UpperLeft': (-116.77122911662993, 47.76643156830353),
                       'UpperRight': (-116.58602818132573, 47.76643156830353)},
 'DatasetName': 'AgeoTiffFile.tif',
 'Driver': {'LongName': 'GeoTIFF',
            'Metadata': {'DCAP_CREATE': 'YES',
                         'DCAP_CREATECOPY': 'YES',
                         'DCAP_VIRTUALIO': 'YES',
                         'DMD_CREATIONDATATYPES': 'Byte UInt16 Int16 UInt32 Int32 Float32 Float64 CInt16 CInt32 CFloat32 CFloat64',
                         'DMD_CREATIONOPTIONLIST': "<CreationOptionList>   <Option name='COMPRESS' type='string-select'>       <Value>NONE</Value>       <Value>LZW</Value>       <Value>PACKBITS</Value>       <Value>JPEG</Value>       <Value>CCITTRLE</Value>       <Value>CCITTFAX3</Value>       <Value>CCITTFAX4</Value>       <Value>DEFLATE</Value>       <Value>LZMA</Value>   </Option>   <Option name='PREDICTOR' type='int' description='Predictor Type'/>   <Option name='JPEG_QUALITY' type='int' description='JPEG quality 1-100' default='75'/>   <Option name='ZLEVEL' type='int' description='DEFLATE compression level 1-9' default='6'/>   <Option name='LZMA_PRESET' type='int' description='LZMA compression level 0(fast)-9(slow)' default='6'/>   <Option name='NBITS' type='int' description='BITS for sub-byte files (1-7), sub-uint16 (9-15), sub-uint32 (17-31)'/>   <Option name='INTERLEAVE' type='string-select' default='PIXEL'>       <Value>BAND</Value>       <Value>PIXEL</Value>   </Option>   <Option name='TILED' type='boolean' description='Switch to tiled format'/>   <Option name='TFW' type='boolean' description='Write out world file'/>   <Option name='RPB' type='boolean' description='Write out .RPB (RPC) file'/>   <Option name='BLOCKXSIZE' type='int' description='Tile Width'/>   <Option name='BLOCKYSIZE' type='int' description='Tile/Strip Height'/>   <Option name='PHOTOMETRIC' type='string-select'>       <Value>MINISBLACK</Value>       <Value>MINISWHITE</Value>       <Value>PALETTE</Value>       <Value>RGB</Value>       <Value>CMYK</Value>       <Value>YCBCR</Value>       <Value>CIELAB</Value>       <Value>ICCLAB</Value>       <Value>ITULAB</Value>   </Option>   <Option name='SPARSE_OK' type='boolean' description='Can newly created files have missing blocks?' default='FALSE'/>   <Option name='ALPHA' type='string-select' description='Mark first extrasample as being alpha'>       <Value>NON-PREMULTIPLIED</Value>       <Value>PREMULTIPLIED</Value>       <Value>UNSPECIFIED</Value>       <Value aliasOf='NON-PREMULTIPLIED'>YES</Value>       <Value aliasOf='UNSPECIFIED'>NO</Value>   </Option>   <Option name='PROFILE' type='string-select' default='GDALGeoTIFF'>       <Value>GDALGeoTIFF</Value>       <Value>GeoTIFF</Value>       <Value>BASELINE</Value>   </Option>   <Option name='PIXELTYPE' type='string-select'>       <Value>DEFAULT</Value>       <Value>SIGNEDBYTE</Value>   </Option>   <Option name='BIGTIFF' type='string-select' description='Force creation of BigTIFF file'>     <Value>YES</Value>     <Value>NO</Value>     <Value>IF_NEEDED</Value>     <Value>IF_SAFER</Value>   </Option>   <Option name='ENDIANNESS' type='string-select' default='NATIVE' description='Force endianness of created file. For DEBUG purpose mostly'>       <Value>NATIVE</Value>       <Value>INVERTED</Value>       <Value>LITTLE</Value>       <Value>BIG</Value>   </Option>   <Option name='COPY_SRC_OVERVIEWS' type='boolean' default='NO' description='Force copy of overviews of source dataset (CreateCopy())'/>   <Option name='SOURCE_ICC_PROFILE' type='string' description='ICC profile'/>   <Option name='SOURCE_PRIMARIES_RED' type='string' description='x,y,1.0 (xyY) red chromaticity'/>   <Option name='SOURCE_PRIMARIES_GREEN' type='string' description='x,y,1.0 (xyY) green chromaticity'/>   <Option name='SOURCE_PRIMARIES_BLUE' type='string' description='x,y,1.0 (xyY) blue chromaticity'/>   <Option name='SOURCE_WHITEPOINT' type='string' description='x,y,1.0 (xyY) whitepoint'/>   <Option name='TIFFTAG_TRANSFERFUNCTION_RED' type='string' description='Transfer function for red'/>   <Option name='TIFFTAG_TRANSFERFUNCTION_GREEN' type='string' description='Transfer function for green'/>   <Option name='TIFFTAG_TRANSFERFUNCTION_BLUE' type='string' description='Transfer function for blue'/>   <Option name='TIFFTAG_TRANSFERRANGE_BLACK' type='string' description='Transfer range for black'/>   <Option name='TIFFTAG_TRANSFERRANGE_WHITE' type='string' description='Transfer range for white'/></CreationOptionList>",
                         'DMD_EXTENSION': 'tif',
                         'DMD_HELPTOPIC': 'frmt_gtiff.html',
                         'DMD_LONGNAME': 'GeoTIFF',
                         'DMD_MIMETYPE': 'image/tiff',
                         'DMD_SUBDATASETS': 'YES'},
            'ShortName': 'GTiff'},
 'FileList': ['AgeoTiffFile.tif',
              'AgeoTiffFile.tif.aux.xml'],
 'Geotransform': (-116.77122911662993,
                  9.260046765209751e-05,
                  0.0,
                  47.76643156830353,
                  0.0,
                  -9.257926006829539e-05),
 'Size': [2000, 1272]}
>>> 
```
