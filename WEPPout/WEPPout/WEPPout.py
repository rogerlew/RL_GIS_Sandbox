from __future__ import print_function

# Copyright (c) 2014, Roger Lew (rogerlew.gmail.com)
# All rights reserved.
#
# The project described was supported by NSF award number IIA-1301792 
# from the NSF Idaho EPSCoR Program and by the National Science Foundation.

"""
This packs GPH (geopotential height) outputs from the Water Erosion and Prediction Project (WEPP) 
model into a HDF5 container.
"""

__version__ = "0.0.1"

# standard library modules
import array
from glob import glob
import os
import sys
import time
import multiprocessing

# 3rd party dependencies
import h5py
import numpy as np

DAYS = 'Days In Simulation'

def read_slope(fname):
    """
    reads a slope text data file


    Parameters
    ----------
      fname : string
        path to the slope file

    Returns
    -------
      (meta, OFEs) : tuple(dict, dict)
        It is returning this way to support multiprocessing
    """
    
    # http://milford.nserl.purdue.edu/weppdocs/usersummary/HillSlopeData.html


    meta = {}
    OFEs = []

    meta['fname'] = fname
    meta['id'] = ''.join([L for L in fname if L in '0123456789'])
    
    fid = open(fname, 'r')
    lines = fid.readlines()
    lines = [L for L in lines if len(L) > 0]
    lines = [L.strip() for L in lines if L.lstrip()[0] != '#']
    
    meta['dataver'] = lines[0]
    n = meta['nelem'] = int(lines[1])

    line = lines[2].split()
    meta['azm'] = float(line[0])
    meta['fwidth'] = float(line[1])

    for i in range(3, 3+(n*2), 2):
        ofe = {}

        nslpts, slplen = lines[i].split()
        nslpts = ofe['nslpts'] = int(nslpts)
        ofe['slplen'] = float(slplen)

        line = lines[i+1].replace(',', '')
        points = [float(L) for L in line.split()]
        points = np.array(points).reshape(nslpts, 2)
        ofe['distance'] = points[:, 0]
        ofe['steepness'] = points[:, 1]

        OFEs.append(ofe)
    
    return meta,OFEs

def read_cli(fname):
    """
    reads a cligen text data file


    Parameters
    ----------
      fname : string
        path to the cli file

    Returns
    -------
      (meta, data) : tuple(dict, dict)
        It is returning this way to support multiprocessing
    """
    
    meta = {}
    data = None
    header = []

    meta['fname'] = fname
    meta['id'] = ''.join([L for L in fname if L in '0123456789'])
    
    fid = open(fname, 'r')
    meta['CLIGEN Version'] = fid.readline().strip()
    fid.readline()
    meta['Station'] = ' '.join(fid.readline().strip().split())

    fid.readline()
    line = fid.readline().strip().split()
    meta['Latitude'] = float(line[0])
    meta['Longitude'] = float(line[1])
    meta['Elevation'] = float(line[2])
    meta['Obs. Years'] = float(line[3])
    meta['Beginning Year'] = float(line[4])
    meta['Years Simulated'] = float(line[5])
    meta['Command Line'] = ' '.join(line[6:])

    fid.readline()
    meta['Observed monthly ave max temperature (C)'] = \
        list(map(float, fid.readline().split()))

    fid.readline()
    meta['Observed monthly ave min temperature (C)'] = \
        list(map(float, fid.readline().split()))

    fid.readline()
    meta['Observed monthly ave solar radiation (Langleys/day)'] = \
        list(map(float, fid.readline().split()))

    fid.readline()
    meta['Observed monthly ave precipitation (mm)'] = \
        list(map(float, fid.readline().split()))

    header = fid.readline().strip().split()
        
    fid.readline()

    _data = []
    for line in fid.readlines():
        cells = line.split()

        if len(cells) != len(header):
            break

        _data.append([float(c) for c in cells])
        
    data = {}
    for h,v in zip(header, zip(*_data)):
        data[h] = v

    del _data
    del header

    return (meta,data)

def read_grp(fname):
    """
    reads a gph text data file


    Parameters
    ----------
      fname : string
        path to the gph file

    Returns
    -------
      (meta, data) : tuple(dict, dict)
        It is returning this way to support multiprocessing
    """
    global DAYS
    uint_types = [DAYS,
                  'Current crop type',                          
                  'Current residue on ground type',             
                  'Previous residue on ground type',            
                  'Old residue on ground type',                 
                  'Current dead root type',                     
                  'Previous dead root type',                    
                  'Old dead root type']

    meta = {}
    data = None
    header = []

    meta['fname'] = fname
    meta['id'] = ''.join([L for L in fname if L in '0123456789'])
    
    fid = open(fname, 'rb')
    for i, line in enumerate(fid.readlines()):
        line_as_list = line.strip().split()

        if len(line_as_list) == 0:
            continue

        elif line_as_list[0][0] == '#':
            continue

        elif line_as_list[0] == 'int':
            try:
                meta[line[1]] = int(line[2])
            except:
                pass
                    
        elif line_as_list[0] == 'float':
            try:
                meta[line[1]] = float(line[2])
            except:
                pass

        elif line_as_list[0] == 'char':
            continue

        elif line_as_list[0][0] == '{':
            cname = line.strip()[1:-1].replace(r'kg/m',      r'kg*m**-1')   \
                                        .replace(r'kg/m**2',   r'kg*m**-2')   \
                                        .replace(r'kg/m**3',   r'kg*m**-3')   \
                                        .replace(r'kg/m**4',   r'kg*m**-4')   \
                                        .replace(r'mm/hr',     r'mm*hr**-1')  \
                                        .replace(r'mm/h',      r'mm*hr**-1')  \
                                        .replace(r'm/day',     r'm*day**-1')  \
                                        .replace(r'g/cc',      r'g*cc**-1')   \
                                        .replace(r'kg-s/m**4', r'kg-s*m**-4') \
                                        .replace(r's/m',       r's*m**-1')    \
                                        .replace(r'Irrigation_volume_supplied/unit_area',
                                                r'Irrigation_volume_supplied*unit_area**-1')
            header.append(cname)

        else:
            if len(header) == len(line_as_list):
                        
                # if we are here and data == None we need to initialize the data dictionary
                if data == None:
                    data = {}
                    for cname in header:
                        typecode = ('f', 'h')[any([cname==s for s in uint_types])]
                        data[cname] = array.array(typecode)

                for (cname, string) in zip(header, line_as_list):
                    if any([cname==s for s in uint_types]):
                        value = int(string)
                    else:
                        value = float(string)

                    if cname == DAYS:

                        if value in set(data[DAYS]):
                            break

                    data[cname].append(value)

            else:
                raise Exception('Failed to parse line %i, unexpected number of columns.'%(i+1))
                
    fid.close()

    # pack the table data into numpy arrays
    for (cname, v) in data.items():
        dtype = (np.float32, np.int16)[any([cname==s for s in uint_types])]
        data[cname] = np.array(v, dtype=dtype)

    return (meta, data)

if __name__ == '__main__':
    path = r'D:\ownCloud\documents\geo_data\Fernan\Lake_Fernan_simu_Single_OFE'
    
    fid = h5py.File('WEPPout.hdf5', 'w')

    numcpus = 12

    # parallel worker pool
    pool = multiprocessing.Pool(numcpus)

    #
    # Read the gph data files in parallel
    #
    ignore = ['pw0_gph.txt']
    
    fnames = []
    for fname in glob(os.path.join(path, '*_gph.txt')):
        if not any([fn in fname for fn in ignore]):
            fnames.append(fname)

    # this launches the batch processing of the grp files
    packed_tuples = pool.imap(read_grp, fnames)

    # this provides feedback as the sets of files complete. Using imap
    # guarentees that the files are in the same order as fnames but
    # delays receiving feedback

    gph = fid.create_group("gph")

    for i, (meta, data) in enumerate(packed_tuples):
        print('  %s' % fnames[i])
        sub = gph.create_group(meta['id'])

        for k,v in meta.items():
            sub.attrs.create(k, v)

        for cname, v in data.items():
            sub.create_dataset(cname, compression="gzip", compression_opts=9, data=v)
            
    #
    # Read the cli data files in parallel
    #
    fnames = glob(os.path.join(path, 'cli', '*.cli'))

    # this launches the batch processing of the grp files
    packed_tuples = pool.imap(read_cli, fnames)

    cli = fid.create_group("cli")

    for i, (meta, data) in enumerate(packed_tuples):
        print('  %s' % fnames[i])
        sub2 = cli.create_group(meta['id'])

        for k,v in meta.items():
            sub2.attrs.create(k, v)

        for cname, v in data.items():
            sub2.create_dataset(cname, compression="gzip", compression_opts=9, data=v)
         
    #
    # Read the slope data files in parallel
    #
    ignore = ['slope_ofe.out']

    fnames = []
    for fname in glob(os.path.join(path, 'slope', '*.out')):
        if not any([fn in fname for fn in ignore]):
            fnames.append(fname)

    # this launches the batch processing of the slope files
    packed_tuples = pool.imap(read_slope, fnames)
    
    cli = fid.create_group("slope")

    for i, (meta, OFEs) in enumerate(packed_tuples):
        print('  %s' % fnames[i])
        sub3 = cli.create_group(meta['id'])

        for k,v in meta.items():
            sub3.attrs.create(k, v)
            
        sub4 = sub3.create_group('OFEs')
        
        for j, ofe in enumerate(OFEs):
            sub5 = sub4.create_group(str(j))
            sub5.attrs.create('nslpts', ofe['nslpts'])
            sub5.create_dataset('distance', data=ofe['distance'])
            sub5.create_dataset('steepness', data=ofe['steepness'])
          
    fid.close()
