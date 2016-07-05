"""
Functions for GeosChem netCDF files.
Based on TS AC_tools.funcs4GEOSC
All opperations are performed on a netCDF file created by AC_tools.io
"""

import logging

def get_variable_data( netCDF_file, variable ):
    """
    Get variable data from netCDF file.
    """
    logging.info('Getting {variable} data from netCDF file'.format(variable=variable))

    try:
        variable_data = netCDF_file.variables[variable]
        dimensions = variable_data.dimensions
        logging.info('Found data with dimensions {dimensions}'.format(dimensions=dimensions))
    except:
        logging.error('Could not find variable {variable}'.format(variable=variable))
        raise IOError('Could not find variable {variable}'.format(variable=variable))
    return variable_data

def get_surface_area( netCDF_file ):
    """
    Optains a 2D map of gridBOx surfice areas.
    """
    from .GC_funcs import get_variable_data
    logging.info( 'Getting surfice area from netCDF file' )

    surface_area = get_variable_data( netCDF_file, 'DXYP__DXYP' )

    if not (len(surface_area.shape) == 2):
        logging.error('Problem obtaining the surfice area')

    return surface_area;

def get_variables( netCDF_file, show=True ):
    """
    Print a list of variables included in the netCDF file.
    """
    logging.info("Getting the list of netCDF variables")

    variables = []
    for variable in netCDF_file.variables:
        variables.append(variable)
    if show==True:
        for variable in variables:
            print variable
    return variables;


def get_land_map( netCDF_file ):
    """
    Get the land, water, ice (LWI) from GEOS-Chem with integers for land(1) and water(0).
    Ice fraction is provided as a fractional vaule.
    """
#    from .GC_funcs import get_variable_data
#    logging.info('Getting the land map.')
#    land_map = get_variable_data(netCDF_file, 'LANDMAP__LWI')
#    return land_map
    return

def get_air_mass( netCDF_file ):
    """
    Get the air mass of every gridbox.
    """

    from .GC_funcs import get_variable_data
    logging.info('Getting the air mass.')
    air_mass = get_variable_data(netCDF_file, 'BXHGHT_S__AD')
    return air_mass
    

def get_trop_time( netCDF_file ):
    """
    Get the percentage of time each gridbox spends in the troposphere
    """

    from .GC_funcs import get_variable_data
    trop_time_variable_name = "TIME_TPS__TIMETROP"
    trop_time = get_variable_data( netCDF_file, trop_time_variable_name )
    return trop_time

def get_species_data( netCDF_file, species ):
    """
    Gets the species data in mixing ratio from the netCDF file.
    """
    logging.info( 'Getting {species} data.'.format(species=species) )

    assert isinstance(species, str), 'Species provided is not a string'
    from .GC_funcs import get_variable_data
    variable_name = 'IJ_AVG_S__' + species
    variable_data = get_variable_data( netCDF_file, variable_name)
    return variable_data

def get_tropospheric_species_mass( netCDF_file, species ):
    """
    Return the mass of a species in each gridbox in gramms.
    """
    
    import numpy as np
    from .GC_funcs import get_species_data
    from .GC_funcs import get_air_mols
    from .GC_funcs import get_trop_time
    from MChem_tools.MChem_tools import species as get_species_info

    logging.info('Getting the tropospheric {species} mass.'.format(species=species))

    species_data = get_species_data( netCDF_file, species )
    trop_time = get_trop_time( netCDF_file )
    species_info = get_species_info( species )

    air_moles = get_air_mols( netCDF_file)
    species_moles = np.multiply(air_moles, np.divide(species_data,1E9))
    species_mass = np.multiply( species_moles, species_info.RMM )

    trop_species_mass = np.multiply( species_mass[:,:,:38], trop_time )
    return trop_species_mass


def get_air_mols( netCDF_file ):
    """"
    Get the number of molecules in each gridbox.
    """
    import numpy as np
    from .GC_funcs import get_air_mass

    air_mass = get_air_mass( netCDF_file )
    # Air density for N2 + O2
    air_moles = np.divide(np.multiply(air_mass,1E3) , (0.78*28.0 + 0.22*32))

    return air_moles


def get_tropospheric_burden( netCDF_file, variable ):
    """
    Get the tropospheic burden in Tg from the provided netCDf file.
    """
    import numpy as np
    from .GC_funcs import get_tropospheric_species_mass

    trop_species_mass = get_tropospheric_species_mass( netCDF_file, variable )

    # Get the total in Tg.
    total_trop_species_mass = np.sum(trop_species_mass)
    total_trop_species_mass = total_trop_species_mass / 1E12

    return float(total_trop_species_mass)

def get_volume( netCDF_file ):
    """
    Get the volume of ell gridboxes in m^3.
    """
    from .GC_funcs import get_variable_data
    import numpy as np

    height = get_variable_data(netCDF_file, "BXHGHT_S__BXHEIGHT")
    area = get_variable_data(netCDF_file, "DXYP__DXYP")

    # Move time to the first dimension for easier multiplication.
    height = np.rollaxis(height[:],-1,0)
    volume = np.multiply( height, area )
    # Move time back to final axis
    volume = np.rollaxis(volume, 0, np.size(volume.shape))    

    return volume
    
def get_tropospheric_PL(netCDF_file, group_name, group_RMM):
    """
    Get the amount per gridbox of tropsopheric production for a group in Tg per gridbox.
    """
    logging.info("Getting the tropospheric prod/loss for {variable}".format(variable=group_name))

    import numpy as np
    from .GC_funcs import get_variable_data
    from .GC_funcs import get_air_mass
    from .GC_funcs import get_trop_time
    from .GC_funcs import get_air_mols
    from .GC_funcs import get_volume

    assert isinstance(group_name, str), "Invalid PL group name. Not a string."
    assert isinstance(group_RMM, float), "Group RMM not a float."

    variable_name = "PORL_L_S__"+group_name
    
    PL = get_variable_data( netCDF_file, variable_name )
    air_mols = get_air_mols( netCDF_file )
    air_mass = get_air_mass( netCDF_file )
    trop_time = get_trop_time( netCDF_file )
    volume = get_volume( netCDF_file )/1E6 # Get in cm^3

    # Convert from molec/cm3/s to molec/s
    PL = np.multiply( PL, volume[:,:,:38])

    # Convert from molec/s to gram/s
    PL = np.multiply(PL, group_RMM) 

    PL = np.multiply( PL, air_mass[:,:,:38] )
    PL = np.multiply( PL, trop_time )
    
    return  PL 
    

def get_tropospheric_total_PL(netCDF_file, group_name, group_RMM):
    """
    Get the total amount of tropospheric producution for a group in Tg.
    """
    from .GC_funcs import get_tropospheric_PL
    import numpy as np
    PL = get_tropospheric_PL( netCDF_file, group_name, group_RMM)
    PL = np.sum(PL)

    PL = float(PL)


    return PL
    
    


