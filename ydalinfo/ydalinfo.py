#!/usr/bin/env python
################################################################################
# $Id$
#
# Project:  GDAL Utilities
# Purpose:  Python port of Commandline application to list info about a file.
# Author:   Even Rouault, <even dot rouault at mines dash paris dot org>
#
# Revision History:
#   2010-2011
#       Port from ydalinfo.c whose author is Frank Warmerdam
# 
#   2014
#       Pythonized the code
#       returns dict of information
#
################################################################################
# 
# Copyright (c) 2014, Roger Lew <rogerlew@gmail.com>
# Copyright (c) 2010-2011, Even Rouault <even dot rouault at mines-paris dot org>
# Copyright (c) 1998, Frank Warmerdam
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

from __future__ import print_function

from ast import literal_eval
from collections import OrderedDict, Counter
import json
import sys
import warnings
#import xml.dom.minidom

try:
    from osgeo import gdal
    from osgeo import osr
except:
    import gdal
    import osr

__doc__ = """\
Usage:
    ydalinfo [--help-general] [-mm] [-nostats] [-stemleaf] [-nogcp] [-nomd]
             [-norat] [-noct] [-nofl] [-checksum] [-mdd domain]* datasetname

 -mm
    Force computation of the actual min/max values for each band in the dataset
 -nostats
    Suppresses the computation if no statistics are stored in an image
 -stemleaf
    Produces a stem and leaf histogram for each band
 -nogcp
    Suppress ground control points list printing. It may be useful for datasets
    with huge amount of GCPs, such as L1B AVHRR or HDF4 MODIS which contain
    thousands of them.
 -nomd
    Suppress metadata printing. Some datasets may contain a lot of metadata
    strings.
 -norat
    Suppress printing of raster attribute table
 -noct
    Suppress printing of color table
 -nofl
    (GDAL >= 1.9.0) Only display the first file of the file list
 -checksum
    Force computation of the checksum for each band in the dataset
 -listmdd
    (GDAL >= 1.11) List all metadata domains available for the dataset
 -mdd domain
    Report metadata for the specified domain. Starting with GDAL 1.11, "all" can be used to report metadata in all domains
"""

def _stemleafReport(counts, multiplier=None):
    n = len(counts)
        
    if multiplier is None:
        _counts10x = []
        for i0 in xrange(0, n, 10):
            _counts10x.append(sum(counts[i0:i0+10]))
        multiplier = max(_counts10x)/100.0
        del _counts10x
        
    
    bin_edges = range(n)
    d = OrderedDict((((str(v)[:-1],' ')[v<10], Counter()) for v in bin_edges))
    
    for v, cnt in zip(bin_edges, (int(c/multiplier) for c in counts)):
        k = (str(v),' '+str(v))[v<10]
        d[k[:-1]][k[-1]] = cnt
        
    m=max(len(s) for s in d)
    lines = ['Stem leaf histogram:']
    for i, k in enumerate(d):
        elems = ''.join(sorted(d[k].elements()))
        if elems == '':
            i0 = i * 10
            elems = '.'*int(sum(counts[i0:i0+10])/multiplier)
        
        lines.append('  %s%s | %s' % (' ' * (m - len(k)), k, elems))

    lines.append('  Stem multiplier = %i'%multiplier)
    lines.append('  . = sum(10xbins) / Stem multiplier')

    print('\n'.join(lines))

def _parseProjectionWkt(pszPrettyWkt):
    """
    Parses the pretty print Wkt to a dictionary
    """
    if pszPrettyWkt is None:
        return None
    
    lastindent = -1
    newlines = []

    for L in pszPrettyWkt.split('\n'):
        n0 = len(L)
        L = L.lstrip()
        indent = n0 - len(L)

        if indent > lastindent:
            newlines.append('{"' + L.replace('[', '":[')
                                    .replace(']],',']}],')
                                    .replace(']]',']}]}'))
        else:
            newlines.append('"' + L.replace('[', '":[')
                                   .replace(']],',']}],')
                                   .replace(']]',']}]}'))
        lastindent = indent

    return literal_eval(''.join(newlines))

def _metadataReport(hDataset, papszExtraMDDomains):
    papszMetadata = hDataset.GetMetadata_List()
    if papszMetadata is not None:
        print( "Metadata:" )
        for metadata in papszMetadata:
            print( "  %s" % metadata )

    for extra_domain in papszExtraMDDomains:
        papszMetadata = hDataset.GetMetadata_List(extra_domain)
        if papszMetadata is not None and len(papszMetadata) > 0 :
            print( "Metadata (%s):" % extra_domain)
            for metadata in papszMetadata:
              print( "  %s" % metadata )

    groups = ["IMAGE_STRUCTURE", "SUBDATASETS", "GEOLOCATION", "RPC"]
    
    for grp in groups:
        papszMetadata = hDataset.GetMetadata_List(grp)
        
        if papszMetadata is not None:
             
            print(grp + ":")
            for metadata in papszMetadata:
                print("  %s" % metadata)
                
def _coordinateReport( hDataset, hTransform, name, x, y, verbose):
    line = "%-11s " % name

    # Transform the point into georeferenced coordinates.
    gt = hDataset.GetGeoTransform(can_return_null = True)
    if gt is not None:
        dfGeoX = gt[0] + gt[1] * x + gt[2] * y
        dfGeoY = gt[3] + gt[4] * x + gt[5] * y

    else:
        line = line + ("(%7.1f,%7.1f)" % (x, y ))
        if verbose: print(line)
        return x, y

    # Report the georeferenced coordinates
    if abs(dfGeoX) < 181 and abs(dfGeoY) < 91:
        line += ( "(%12.7f,%12.7f) " % (dfGeoX, dfGeoY ))

    else:
        line += ( "(%12.3f,%12.3f) " % (dfGeoX, dfGeoY ))

    # Transform to latlong and report
    if hTransform is not None:
        pnt = hTransform.TransformPoint(dfGeoX, dfGeoY, 0)
        if pnt is not None:
            line += ( "(%s," % gdal.DecToDMS( pnt[0], "Long", 2 ) )
            line += ( "%s)" % gdal.DecToDMS( pnt[1], "Lat", 2 ) )

        if verbose: print(line)
    
    return dfGeoX, dfGeoY

def _bandReport(hDataset, iBand, verbose, bComputeMinMax, bApproxStats,
                bStats, bReportStemleaf, bComputeChecksum,
                bShowMetadata, bShowRAT):
    
    hBand = hDataset.GetRasterBand(iBand )
    
    (nBlockXSize, nBlockYSize) = hBand.GetBlockSize()
    d_type = gdal.GetDataTypeName(hBand.DataType)
    c_interp = gdal.GetColorInterpretationName(hBand.GetRasterColorInterpretation())
    if verbose:
        print( "Band %d Block=%dx%d Type=%s, ColorInterp=%s" % ( 
               iBand, nBlockXSize, nBlockYSize, d_type, c_interp ))
    
    desc = hBand.GetDescription()
    if desc is not None and len(desc) > 0 and verbose:
        print( "  Description = %s" % desc )

    dfMin = hBand.GetMinimum()
    dfMax = hBand.GetMaximum()
    if dfMin is not None or dfMax is not None or bComputeMinMax:

        line =  "  "
        if dfMin is not None:
            line +=  ("Min=%.3f " % dfMin)
        if dfMax is not None:
            line +=  ("Max=%.3f " % dfMax)

        if bComputeMinMax:
            gdal.ErrorReset()
            adfCMinMax = hBand.ComputeRasterMinMax(False)
            if gdal.GetLastErrorType() == gdal.CE_None:
              line +=  ( "  Computed Min/Max=%.3f,%.3f" % ( \
                      adfCMinMax[0], adfCMinMax[1] ))

        if verbose: print(line)

    stats = hBand.GetStatistics( bApproxStats, bStats)
    # Dirty hack to recognize if stats are valid. If invalid, the returned
    # stddev is negative
    if stats[3] >= 0.0 and verbose:
        print( "  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( \
                stats[0], stats[1], stats[2], stats[3] ))

    if bReportStemleaf:

        hist = hBand.GetDefaultHistogram(force = True, callback = gdal.TermProgress)
        if hist is not None and verbose:
            dfMin = hist[0]
            dfMax = hist[1]
            nBucketCount = hist[2]
            panHistogram = hist[3]

            _stemleafReport(panHistogram)

#            print( "  %d buckets from %g to %g:" % ( \
#                    nBucketCount, dfMin, dfMax ))
#            line = '  '
#            for bucket in panHistogram:
#                line +=  ("%d " % bucket)
#
#            if verbose: print(line)

    checksum = hBand.Checksum()
    if bComputeChecksum and verbose:
        print( "  Checksum=%d" % checksum)
    
    dfNoData = hBand.GetNoDataValue()
    if dfNoData is not None and verbose:
        if dfNoData != dfNoData:
            print( "  NoData Value=nan" )
        else:
            print( "  NoData Value=%.18g" % dfNoData )

    if hBand.GetOverviewCount() > 0:

        line = "  Overviews: "
        for iOverview in range(hBand.GetOverviewCount()):

            if iOverview != 0 :
                line +=   ", "

            hOverview = hBand.GetOverview( iOverview );
            if hOverview is not None:

                line +=  ( "%dx%d" % (hOverview.XSize, hOverview.YSize))

                pszResampling = \
                    hOverview.GetMetadataItem( "RESAMPLING", "" )

                if pszResampling is not None \
                   and len(pszResampling) >= 12 \
                   and EQUAL(pszResampling[0:12],"AVERAGE_BIT2"):
                    line +=  "*"

            else:
                line +=  "(null)"

        if verbose: print(line)

        if bComputeChecksum:

            line = "  Overviews checksum: "
            for iOverview in range(hBand.GetOverviewCount()):

                if iOverview != 0:
                    line +=   ", "

                hOverview = hBand.GetOverview( iOverview );
                if hOverview is not None:
                    line +=  ( "%d" % hOverview.Checksum())
                else:
                    line +=  "(null)"
            if verbose: print(line)

    if hBand.HasArbitraryOverviews() and verbose:
        print( "  Overviews: arbitrary" )

    nMaskFlags = hBand.GetMaskFlags()
    if (nMaskFlags & (gdal.GMF_NODATA|gdal.GMF_ALL_VALID)) == 0:

        hMaskBand = hBand.GetMaskBand()

        line = "  Mask Flags: "
        if (nMaskFlags & gdal.GMF_PER_DATASET) != 0:
            line +=  "PER_DATASET "
        if (nMaskFlags & gdal.GMF_ALPHA) != 0:
            line +=  "ALPHA "
        if (nMaskFlags & gdal.GMF_NODATA) != 0:
            line +=  "NODATA "
        if (nMaskFlags & gdal.GMF_ALL_VALID) != 0:
            line +=  "ALL_VALID "
        if verbose: print(line)

        if hMaskBand is not None and \
            hMaskBand.GetOverviewCount() > 0:

            line = "  Overviews of mask band: "
            for iOverview in range(hMaskBand.GetOverviewCount()):

                if iOverview != 0:
                    line +=   ", "

                hOverview = hMaskBand.GetOverview( iOverview );
                if hOverview is not None:
                    line +=  ( "%d" % hOverview.Checksum())
                else:
                    line +=  "(null)"
    
    unitType = hBand.GetUnitType()
    if len(unitType) > 0 and verbose:
        print( "  Unit Type: %s" % unitType)

    papszCategories = hBand.GetRasterCategoryNames()
    if papszCategories is not None and verbose:
        print( "  Categories:" );
        i = 0
        for category in papszCategories:
            print( "    %3d: %s" % (i, category) )
            i += 1

    if hBand.GetScale() != 1.0 or hBand.GetOffset() != 0.0 and verbose:
        print( "  Offset: %.15g,   Scale:%.15g" % \
                    ( hBand.GetOffset(), hBand.GetScale()))

    if bShowMetadata:
        papszMetadata = hBand.GetMetadata_List()
    else:
        papszMetadata = None
    if bShowMetadata and papszMetadata is not None and len(papszMetadata) > 0 and verbose:
        print( "  Metadata:" )
        for metadata in papszMetadata:
            print( "    %s" % metadata )

    if bShowMetadata:
        papszMetadata = hBand.GetMetadata_List("IMAGE_STRUCTURE")
    else:
        papszMetadata = None
    if bShowMetadata and papszMetadata is not None and len(papszMetadata) > 0 and verbose:
        print( "  Image Structure Metadata:" )
        for metadata in papszMetadata:
            print( "    %s" % metadata )

    hTable = hBand.GetRasterColorTable()
    if hBand.GetRasterColorInterpretation() == gdal.GCI_PaletteIndex  \
        and hTable is not None and verbose:

        print( "  Color Table (%s with %d entries)" % (\
                gdal.GetPaletteInterpretationName( \
                    hTable.GetPaletteInterpretation(  )), \
                hTable.GetCount() ))

        if bShowColorTable:

            for i in range(hTable.GetCount()):
                sEntry = hTable.GetColorEntry(i)
                print( "  %3d: %d,%d,%d,%d" % ( \
                        i, \
                        sEntry[0],\
                        sEntry[1],\
                        sEntry[2],\
                        sEntry[3] ))
               
    if bShowRAT:
        hRAT = hBand.GetDefaultRAT()

                    
    return { 'BandNum': iBand,
             'BlockSize': (nBlockXSize, nBlockYSize),
             'Type': d_type,
             'ColorInterp': c_interp,
             'Minimum': dfMin,
             'Maximum': dfMax,
             'Description': desc,
             'CheckSum': checksum,
             'NoDataValue': dfNoData,
             'MaskFlags': nMaskFlags,
             'UnitType': unitType,
             'Categories:': papszCategories,
             'Metadata': hBand.GetMetadata_Dict(),
             'ColorTable': hTable,
             'RAT': hBand.GetDefaultRAT()}


def ydalinfo(pszFilename, bComputeMinMax=False, bSample=False,
             bShowGCPs=True, bShowMetadata=True, bShowRAT=True,
             bStats=False, bApproxStats=True, bShowColorTable=True,
             bComputeChecksum=False, bReportStemleaf=False,
             papszExtraMDDomains=None, pszProjection=None, hTransform=None,
             bShowFileList=True, bJson=False, verbose=False):
        
    if papszExtraMDDomains is None:
        papszExtraMDDomains = []


    jsonDict = {'DatasetName' : pszFilename}
    hDataset = gdal.Open( pszFilename, gdal.GA_ReadOnly )

    if hDataset is None:
        if verbose:
            msg = "ydalinfo failed - unable to open '%s'." % pszFilename
            print(msg)
            return
        raise Exception(msg)    
    
    # Driver
    hDriver = hDataset.GetDriver()
    jsonDict['Driver'] = {'ShortName': hDriver.ShortName,
                          'LongName': hDriver.LongName,
                          'Metadata': hDriver.GetMetadata_Dict()}
    
#    xml_str = jsonDict['Driver']['Metadata'].get('DMD_CREATIONOPTIONLIST', '')
#    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml()
#   jsonDict['Driver']['Metadata']['DMD_CREATIONOPTIONLIST'] = pretty_xml
    
    if verbose:
        print("Driver: %s/%s" % (hDriver.ShortName, hDriver.LongName))

    # FileList
    papszFileList = hDataset.GetFileList()
    jsonDict['FileList'] = papszFileList
    
    if bShowFileList and verbose:
        if papszFileList is None or len(papszFileList) == 0:
            print( "Files: none associated" )
        else:
            print( "Files: %s" % papszFileList[0] )
            for i in xrange(1, len(papszFileList)):
                print( "       %s" % papszFileList[i] )
    
    # Size      
    jsonDict['Size'] = [hDataset.RasterXSize, hDataset.RasterYSize]
    
    if verbose:
        print( "Size is %d, %d" % (hDataset.RasterXSize, hDataset.RasterYSize))

    #Projection
    pszProjection = hDataset.GetProjectionRef()
    if pszProjection is not None:

        hSRS = osr.SpatialReference()
        if hSRS.ImportFromWkt(pszProjection ) == gdal.CE_None:
            pszPrettyWkt = hSRS.ExportToPrettyWkt(False)

            if verbose:
                print( "Coordinate System is:\n%s" % pszPrettyWkt )
        else:
            if verbose:
                print( "Coordinate System is `%s'" % pszProjection )
            
    jsonDict['CoordinateSystem'] = _parseProjectionWkt(pszPrettyWkt)

    # Geotransform
    adfGeoTransform = hDataset.GetGeoTransform(can_return_null = True)
    jsonDict['Geotransform'] = adfGeoTransform
    
    if adfGeoTransform is not None and verbose:

        if adfGeoTransform[2] == 0.0 and adfGeoTransform[4] == 0.0:
            print( "Origin = (%.15f,%.15f)" % ( \
                    adfGeoTransform[0], adfGeoTransform[3] ))

            print( "Pixel Size = (%.15f,%.15f)" % ( \
                    adfGeoTransform[1], adfGeoTransform[5] ))

        else:
            print( "GeoTransform =\n" \
                    "  %.16g, %.16g, %.16g\n" \
                    "  %.16g, %.16g, %.16g" % ( \
                    adfGeoTransform[0], \
                    adfGeoTransform[1], \
                    adfGeoTransform[2], \
                    adfGeoTransform[3], \
                    adfGeoTransform[4], \
                    adfGeoTransform[5] ))

    # GCPs
    if bShowGCPs and hDataset.GetGCPCount() > 0 and verbose:

        pszProjection = hDataset.GetGCPProjection()
        if pszProjection is not None:

            hSRS = osr.SpatialReference()
            if hSRS.ImportFromWkt(pszProjection ) == gdal.CE_None:
                pszPrettyWkt = hSRS.ExportToPrettyWkt(False)
                print( "GCP Projection = \n%s" % pszPrettyWkt )

            else:
                print( "GCP Projection = %s" % \
                        pszProjection )

        gcps = hDataset.GetGCPs()
        
        if verbose:
            i = 0
            for gcp in gcps:

                print( "GCP[%3d]: Id=%s, Info=%s\n" \
                        "          (%.15g,%.15g) -> (%.15g,%.15g,%.15g)" % ( \
                        i, gcp.Id, gcp.Info, \
                        gcp.GCPPixel, gcp.GCPLine, \
                        gcp.GCPX, gcp.GCPY, gcp.GCPZ ))
                i = i + 1

    # Metadata
    if bShowMetadata and verbose:
        _metadataReport(hDataset, papszExtraMDDomains)
        
    # Setup projected to lat/long transform if appropriate.
    if pszProjection is not None and len(pszProjection) > 0:
        hProj = osr.SpatialReference( pszProjection )
        if hProj is not None:
            hLatLong = hProj.CloneGeogCS()

        if hLatLong is not None:
            gdal.PushErrorHandler( 'CPLQuietErrorHandler' )
            hTransform = osr.CoordinateTransformation( hProj, hLatLong )
            gdal.PopErrorHandler()
            if gdal.GetLastErrorMsg().find( 'Unable to load PROJ.4 library' ) != -1:
                hTransform = None

    # Corners
    if verbose: print("Corner Coordinates:")
    x, y = hDataset.RasterXSize, hDataset.RasterYSize
    ul = _coordinateReport( hDataset, hTransform, "Upper Left", 0.0, 0.0, verbose)
    ll = _coordinateReport( hDataset, hTransform, "Lower Left", 0.0, y, verbose)
    ur = _coordinateReport( hDataset, hTransform, "Upper Right", x, 0.0, verbose)
    lr = _coordinateReport( hDataset, hTransform, "Lower Right", x, y, verbose)
    _coordinateReport( hDataset, hTransform, "Center", x/2.0, y/2.0, verbose)

    
    jsonDict['CornerCoordinates'] = { 'UpperLeft': ul,
                                      'LowerLeft': ll,
                                      'UpperRight': ur,
                                      'LowerRight': lr }
    
    jsonDict['Bands'] = []
    # Loop over bands
    for iBand in xrange(1, hDataset.RasterCount + 1):
        bandopts = [hDataset, iBand, verbose, bComputeMinMax, bApproxStats,
                    bStats, bReportStemleaf, bComputeChecksum,
                    bShowMetadata, bShowRAT]
        jsonDict['Bands'].append(_bandReport(*bandopts))

    if bJson:
        print(json.dumps(jsonDict))
    return jsonDict

if __name__ == '__main__':
    version_num = int(gdal.VersionInfo('VERSION_NUM'))
    release_name = gdal.VersionInfo("RELEASE_NAME")
    if version_num < 1800: # because of GetGeoTransform(can_return_null)
        print('ERROR: Python bindings of GDAL 1.8.0 or later required')
        sys.exit(1)
        
    argv = gdal.GeneralCmdLineProcessor(sys.argv)

    bComputeMinMax = False
    bSample = False
    bShowGCPs = True
    bShowMetadata = True
    bShowRAT=True
    bStats = True
    bApproxStats = True
    bShowColorTable = True
    bComputeChecksum = False
    bReportStemleaf = False
    pszFilename = None
    papszExtraMDDomains = []
    pszProjection = None
    hTransform = None
    bShowFileList = True
    bVerbose = True
    bJson = False

    # Parse arguments.
    i, nArgc = 1, len(argv)
    while i < nArgc:
        lwr_arg = argv[i].lower()
        if lwr_arg == "--utility_version":
            print("%s is running against GDAL %s" %
                   (argv[0], release_name))
            sys.exit()
        elif lwr_arg == "-mm":
            bComputeMinMax = True
        elif lwr_arg == "-stemleaf":
            bReportStemleaf = True
        elif lwr_arg == "-json":
            bVerbose = False
            bJson = True
        elif lwr_arg == "-nostats":
            bStats = False
            bApproxStats = False
        elif lwr_arg == "-approx_stats":
            bStats = True
            bApproxStats = True
        elif lwr_arg == "-sample":
            bSample = True
        elif lwr_arg == "-checksum":
            bComputeChecksum = True
        elif lwr_arg == "-nogcp":
            bShowGCPs = False
        elif lwr_arg == "-nomd":
            bShowMetadata = False
        elif lwr_arg == "-norat":
            bShowRAT = False
        elif lwr_arg == "-noct":
            bShowColorTable = False
        elif lwr_arg == "-mdd" and i < nArgc-1:
            i += 1
            papszExtraMDDomains.append( argv[i] )
        elif lwr_arg == "-nofl":
            bShowFileList = False
        elif argv[i][0] == '-':
            warnings.warn("Do not understand '%s' flag"%argv[i])
        elif pszFilename is None:
            pszFilename = argv[i]
        else:
            warnings.warn("Could not parse '%s'"%argv[i])
        
        i += 1

    if pszFilename is None:
        print(__doc__)
        sys.exit()
    
    ydalinfo(pszFilename, 
             bComputeMinMax=bComputeMinMax, 
             bSample=bSample, 
             bShowGCPs=bShowGCPs, 
             bShowMetadata=bShowMetadata, 
             bShowRAT=bShowRAT, 
             bStats=bStats, 
             bApproxStats=bApproxStats, 
             bShowColorTable=bShowColorTable, 
             bComputeChecksum=bComputeChecksum, 
             bReportStemleaf=bReportStemleaf, 
             papszExtraMDDomains=papszExtraMDDomains, 
             pszProjection=pszProjection, 
             hTransform=hTransform, 
             bShowFileList=bShowFileList,
             bJson=bJson,
             verbose=bVerbose)
