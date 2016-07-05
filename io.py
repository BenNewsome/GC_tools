#!/usr/bin/python
"""
This script analysis a folder containing bpch files and outputs the results
in a single netCDF file in the folder.

This allows for significantly faster and easier input of data, 
and more common anaylsis techniques like pandas without extra 
post processing. 
"""

def open_netCDF(folder='none',filename='ctm.nc'):
    """
    Opens the netCDF file from a GEOS-Chem run.
    Converts all .bpch files in a folder to a netCDF file if required.
    The Default folder is the current folder.
    The default ouptut filename is ctm.nc.
    Returns a netCDF4 Dataset object.
    """

    import logging
    import os
    if (folder == 'none'):
        folder = os.getcwd()
    netCDF_filename = os.path.join(folder, filename)
           

    logging.info('Opening netCDF file: ' + netCDF_filename)

    from netCDF4 import Dataset
    # Try to open a netCDF file
    try:
        # Hope for success
        netCDF_data = Dataset(netCDF_filename)
        logging.info("netCDF file opened successfuly")
    except:
        # If no netCDF file loaded, try making one from bpch
        logging.debug('No netCDF file found. Attempting to create one.')
        try:
            from pygchem import datasets
        except:
            import pygchem.datafields as datasets
        import glob
        bpch_files = glob.glob(folder + '/*.bpch*' )
        logging.debug('Found ' + str(len(bpch_files)) + ' bpch files.')
        if (len(bpch_files) == 0):
            logging.error('No bpch files found.')
            raise IOError('Cannot find bpch files.')
            return
        pygchem_data = datasets.load(bpch_files)
        # Convert the dataset to an iris cube and export as netCDF
        logging.debug('Creating a netCDF file from bpch.')
        import iris
        iris.fileformats.netcdf.save(pygchem_data, netCDF_filename)
        netCDF_data = Dataset(netCDF_filename)
        if (netCDF_data == None):
            logging.error('Error creating netCDF file from bpch.')
            raise IOError('Error creating netCDF file from bpch.')

    return netCDF_data
    
