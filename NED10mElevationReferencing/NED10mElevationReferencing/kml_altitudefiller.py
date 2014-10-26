from __future__ import print_function

# Copyright (c) 2014, Roger Lew [see LICENSE.txt]
#
# The project described was supported by NSF award number IIA-1301792 
# from the NSF Idaho EPSCoR Program and by the National Science Foundation.

import argparse    
import re
import os
import time

from elevationService import Server

if __name__ == "__main__":
    t0 = time.time()

    server = Server.getInstance()

    parser = argparse.ArgumentParser()
    parser.add_argument('kml', type=str,   
                        help='kml to fill               ("")')
    parser.add_argument('-z', '--zval',     type=str, 
                        help='value to replace          (0)')
    parser.add_argument('-f', '--offset',   type=float, 
                        help='z offset                  (0)')
    parser.add_argument('-o', '--outfile',   type=str,   
                        help='Output file               (<ORIGINAL_NAME>.alt.kml)')
    
    args = parser.parse_args()

    kml = args.kml
    zero = (args.zval, '')[args.zval is None]
    zoffset = (args.offset, 0.0)[args.offset is None]
    newkml = (args.outfile, kml.replace('.kml', '.alt.kml'))[args.outfile is None]

    #kml = 'testdata/subcatchments.kml'
    #zero = ''
    #zoffset = 1
    #newkml = 'testdata/subcatchments1.kml'
   
    pattern = '(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)' + (',\s*' + zero, '')[zero=='']

    print('Finding locations in %s...'%kml)
    with open(kml) as f:
        string = f.read()
        
    result_iter = re.finditer(pattern, string)

    print('Determining unique locations...' )
    replacement_set = set()
    for m in result_iter:
        replacement_set.add(m.group(0))
    replacement_set = list(replacement_set)
    n = len(replacement_set)
    
    print('Fetching %i elevations...'%n)
    t0_f = time.time()
    coord_list = []
    for p in replacement_set:
        lng,lat = p.split(',')[:2]
        coord_list.append('%s,%s'%(lng, lat))

    elevations = server.getElevations(coord_list)
    tend_f = time.time() - t0_f
    print('  Fetching %i locations took %0.2f seconds (%0.2f locations/second)'%\
          (n, tend_f, n/tend_f))

    print('\nWriting new kml...')
    
    if zero == '':
        for old, z in zip(replacement_set, elevations):
            new = '%s,%f'%(old, z + zoffset)
            string = string.replace(old, new)
    else:
        for old, z in zip(replacement_set, elevations):
            new = old[:-len(zero)] + str(z + zoffset)
            string = string.replace(old, new)

    with open(newkml, 'wb') as f:
        f.write(string)
        
    print('Done.\n\n'\
          'Conversion took %0.2f seconds and replaced %i unique locations'\
          %(time.time()-t0, n))
