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
import glob
import os
import sys
import time
import multiprocessing

import h5py
import numpy as np

# 3rd party dependencies
DAYS = 'Days In Simulation'

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
    
    with open(fname, 'rb') as fid:
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
                
    # pack the table data into numpy arrays
    for (cname, v) in data.items():
        dtype = (np.float32, np.int16)[any([cname==s for s in uint_types])]
        data[cname] = np.array(v, dtype=dtype)

    return (meta, data)

if __name__ == '__main__':
    path = r'D:\ownCloud\documents\geo_data\Fernan\Lake_Fernan_simu_Single_OFE'
    ignore = ['pw0_gph.txt']
    
    fnames = []
    for fname in glob.glob(os.path.join(path, '*_gph.txt')):
        if not any([fn in fname for fn in ignore]):
            fnames.append(fname)
#            print fname
#            read_grp(fname)

    numcpus = 12

    # parallel worker pool
    pool = multiprocessing.Pool(numcpus)

    # this launches the batch processing of the grp files
    packed_tuples = pool.imap(read_grp, fnames)

    # this provides feedback as the sets of files complete. Using imap
    # guarentees that the files are in the same order as fnames but
    # delays receiving feedback

    fid = h5py.File('WEPPout.hdf5', 'w')
    gph = fid.create_group("gph")

    for i, (meta, data) in enumerate(packed_tuples):
        print('    {:<43}{:10}'.format(fnames[i], meta['id']))
        sub = gph.create_group(meta['id'])

        for k,v in meta.items():
            sub.attrs.create(k, v)

        for cname, v in data.items():
            sub.create_dataset(cname, compression="gzip", compression_opts=9, data=v)
            
    del packed_tuples

    fid.close()
