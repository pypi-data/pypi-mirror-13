# -*- coding: utf-8 -*-
import copy
from datetime import datetime
import glob
import numpy as np
import os
import scipy.interpolate as scinter

import cf_units
import iris

from . import utils

def interp_cubes_to_points(cubelist, cube_name_and_axes,
                              verbose=0, extrapolation_mode='linear'):
    """ """
    src_cube = get_cube(cubelist, cube_name_and_axes['name'])
    pnts = []
    if 'dim_ave' in cube_name_and_axes:
        for iax in cube_name_and_axes['dim_ave']:
            iax_name = src_cube.coord(axis=iax).name()
            iax_pnts = 0.5 * (src_cube.coord(axis=iax).points[1:] + src_cube.coord(axis=iax).points[:-1])
            if all(iax_pnts > 180.0):
                iax_pnts = iax_pnts - 360.0
            pnts.append((iax_name, iax_pnts))

    else:
        for iax in 'xy':
            iax_name = src_cube.coord(axis=iax).name()
            iax_pnts = src_cube.coord(axis=iax).points
            if all(iax_pnts > 180.0):
                iax_pnts = iax_pnts - 360.0
            pnts.append((iax_name, iax_pnts))

    for k, icube in enumerate(cubelist):
        if verbose > 1:
            utils.tic()
        new_cube = iris.analysis.interpolate.linear(icube, pnts,
                                                    extrapolation_mode=extrapolation_mode)
        if verbose > 1:
            print('Interpolation of {} is completed.'.format(new_cube.name()))
            utils.toc()
            print()
        cubelist[k] = new_cube


def load_data(filenames, replace_unknowns=False, default_path='', verbose=False):
    if hasattr(filenames, '__iter__'):
        filenames = tuple([os.path.join(default_path, ifilename) for ifilename in filenames])
    else:
        filenames = glob.glob(os.path.join(default_path, filenames))

    datasets = []
    for fname in filenames:
        if verbose:
            print('Reading '+fname)
            print()
                
        cubelist = iris.load(fname)
        if replace_unknowns:
            replace_unknown_names(cubelist)
        if verbose:
            print(cubelist)
            print()
            print()
        datasets.append(cubelist)
            
    if hasattr(filenames, '__iter__'):
        return datasets
    else:
        return datasets[0]
    
    
def gather_cube(cubelists, cubenames, add_coord=None, 
                remove_aux_fac=False, remove_fcst_period=False, remove_aux_z=False,
                time_var_name='time_0'):
    """ Concatenate cube with some tweaks """
    cubes = []
    for icubename in cubenames:
        cube = []
        for icubelist in cubelists:
            icube = get_cube(icubelist, icubename)
            if isinstance(add_coord, dict):
                for idim in add_coord:
                    icube.add_dim_coord(add_coord[idim], int(idim))
            if remove_aux_fac:
                for ifactory in icube.aux_factories:
                    icube.remove_aux_factory(ifactory)
            if remove_fcst_period:
                for i_auxcoord in icube.aux_coords:
                    if i_auxcoord.name() == u'forecast_period':
                        icube.remove_coord(i_auxcoord)
            if remove_aux_z:
                for i_auxcoord in icube.aux_coords:
                    if i_auxcoord.name() in [u'surface_altitude',
                                             u'level_height',
                                             u'atmosphere_hybrid_height_coordinate']:
                        icube.remove_coord(i_auxcoord)
            if time_var_name is not None:
                icube.coord('time').var_name = time_var_name
            
            cube.append(icube)
        cube = iris.cube.CubeList(cube)
        concat = cube.concatenate()
        assert len(concat) == 1, 'Concatentation incomplete, so far only \n{}'.format(concat)
        cubes.append(concat[0])
     
    return cubes


def replace_unknown_names(dataset, default_name='unknown'):
    """ Replace missing names within an `iris.cube.CubeList` by using STASH attribute """
    for ivar in dataset:
        if default_name in ivar.name().lower():
            try:
                stash_id = ivar.attributes['STASH'].__str__()
                ivar.rename(utils.stash_id_to_name(stash_id))
            except AttributeError:
                print('Unable to rename, STASH attribute is missing')
                

def get_cube(cubelist, cube_name, lazy=True):
    """ Return a `cube` from a `iris.cube.CubeList` by name` """
    i = None
    for i in cubelist:
        if lazy:
            match = cube_name.lower() in i.name().lower()
        else:
            match = cube_name == i.name()

        if match:
            return i
    if i is None:
        raise ValueError('Cube with name {0} not found in {1}'.format(cube, cubelist))


def get_model_real_coords(vrbl, dims='tzyx'):
    """ Retrieve 'physical' coordinates of """
    pref_coords = dict(x=('x', 'grid_longitude', 'longitude'),
                       y=('y', 'grid_latitude', 'latitude'), 
                       z=('height', 'level_height', 'pressure', 'atmosphere_hybrid_height_coordinate'),
                       t=('time'))
    model_coords = []
    for iax in dims:
        idim = vrbl.coords(axis=iax)
        if len(idim) > 1:
            for icoord in idim:
                if icoord.name() in pref_coords[iax]:
                    model_coords.append(icoord)
        elif len(idim) == 1:
            model_coords.append(idim[0])
            
    if len(vrbl.shape) != len(model_coords):
        print('WARNING! Number of coordinates does not match the input variable shape!')
    return model_coords
        

def regrid_model_to_obs(datacontainer, obs_coord, model_coords=None,
                        obs_time_convert=True, rot_ll=True, shift=None, dims='tzyx'):
    if isinstance(obs_coord, tuple):
        if len(dims) != len(obs_coord):
            raise ValueError('Shape of the obs_coord does not equal to the dims keyword')
        else:
            obs_coord_dict = dict()
            for iax, i_coord in zip(dims, obs_coord):
                obs_coord_dict[iax] = i_coord
    elif isinstance(obs_coord, dict):
        obs_coord_dict = copy.deepcopy(obs_coord)
    else:
        raise ValueError('obs_coord can only be a tuple or a dict')    
    
    #print(np.nanmin(obs_coord_dict['x']),np.nanmax(obs_coord_dict['x']))
    #print(np.nanmin(obs_coord_dict['y']),np.nanmax(obs_coord_dict['y']))
    #print()
    #[ii+jj for ii, jj in zip(obs_coord[1:], zyxsh)]
    
    if isinstance(shift, dict):
        for iax in shift:
            obs_coord_dict[iax] += shift[iax]   
        
    if isinstance(datacontainer, list) or isinstance(datacontainer, tuple):
        ivar = get_cube(datacontainer[0], datacontainer[1])
    elif isinstance(datacontainer, dict):
        ivar = get_cube(datacontainer['dataset'], datacontainer['varname'])
    elif isinstance(datacontainer, iris.cube.Cube):
        ivar = datacontainer
    elif isinstance(datacontainer, np.ndarray):
        if model_coords is None or rot_ll is None:
            raise ValueError('Model coords must be passed explicitly if the input data is numpy.ndarray')
        else:
            ivar = datacontainer
    else:
        raise ValueError('Unrecognized input data type')
    if model_coords is None:
        model_coords = get_model_real_coords(ivar, dims=dims)
    model_coord_points = [i.points for i in model_coords]
    
    if obs_time_convert and 't' in dims:
        obs_coord_dict['t'] = model_coords[0].units.date2num(obs_coord_dict['t'])
        
    if rot_ll:
        try:
            nplon = ivar.coord_system().grid_north_pole_longitude
            nplat = ivar.coord_system().grid_north_pole_latitude
        except AttributeError:
            nplon = model_coords[-1].coord_system.grid_north_pole_longitude
            nplat = model_coords[-1].coord_system.grid_north_pole_latitude
        obs_coord_dict['x'], obs_coord_dict['y'] = iris.analysis.cartography.rotate_pole(obs_coord_dict['x'], obs_coord_dict['y'],
                                                                                         nplon, nplat)
    #print(np.nanmin(obs_coord_dict['x']),np.nanmax(obs_coord_dict['x']))
    #print(np.nanmin(obs_coord_dict['y']),np.nanmax(obs_coord_dict['y']))
    #print(ivar.coords(axis='x')[0].points.min(), ivar.coords(axis='x')[0].points.max())
    #print(ivar.coords(axis='y')[0].points.min(), ivar.coords(axis='y')[0].points.max())
    if isinstance(ivar, iris.cube.Cube):
        ivar_data = ivar.data
    elif isinstance(ivar, np.ndarray):
        ivar_data = ivar
            
    fill_value = np.array(np.nan).astype(ivar.dtype)

    InterpFun = scinter.RegularGridInterpolator(model_coord_points, ivar_data, bounds_error=False, fill_value=fill_value)
    
    obs_coord_interp_arg = []
    for iax in dims:
        obs_coord_interp_arg.append(obs_coord_dict[iax])
    obs_coord_interp_arg = np.vstack(obs_coord_interp_arg).T
    #print(model_coord_points)
    #print()
    #print(obs_coord_interp_arg)
    return InterpFun(obs_coord_interp_arg)


def unrotate_wind(cubelist,
                  uwind_name='x_wind', vwind_name='y_wind',
                  newcs=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS),
                  replace=False, verbose=0):

        u = get_cube(cubelist, uwind_name)
        v = get_cube(cubelist, vwind_name)

        if u is not None or v is not None:
            oldcs = u.coord_system()
            if verbose > 1:
                print('Rotating winds from {}'.format(oldcs) + ' to {}'.format(newcs))
                print()
            u_rot, v_rot = iris.analysis.cartography.rotate_winds(u, v, newcs)
            if replace:
                cubelist[cubelist.index(u)] = u_rot 
                cubelist[cubelist.index(v)] = v_rot 
            else:
                cubelist.append(u_rot)
                cubelist.append(v_rot)
        else:
            print('u-wind or v-wind cubes not found. No winds rotating.')


def convert_unit_str(str1, str2):
    return cf_units.Unit(str1).convert(1, cf_units.Unit(str2))
