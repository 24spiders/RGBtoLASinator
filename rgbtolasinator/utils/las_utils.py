# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:04:10 2023

@author: Liam
"""

import laspy as lp
import numpy as np
import warnings

def load_las(las_path):
    '''Loads the las file at las_path. For class definitions, find "ASPRS LAS SPECIFICATION 1.4"
    
    Arguments:
        las_path: str, path to the las file
        
    Returns:
        las_data: np array of points as [X, Y, Z, Class]
        las_transform_dict: dict, transformation parameters of points for LAS coords to geospatial coords
    '''
    inFile = lp.file.File(las_path, mode = 'r')
    las_data = np.vstack([inFile.X, inFile.Y, inFile.Z, inFile.Classification]).transpose()
    scalex = inFile.header.scale[0]
    offsetx = inFile.header.offset[0]
    scaley = inFile.header.scale[1]
    offsety = inFile.header.offset[1]
    scalez = inFile.header.scale[2]
    offsetz = inFile.header.offset[2]
    inFile.close()
    
    las_transform_dict = {'scalex': scalex, 'offsetx': offsetx, 'scaley': scaley,
                      'offsety': offsety, 'scalez': scalez, 'offsetz': offsetz}
    
    return las_data, las_transform_dict

def project_las_geospatial(las_data, las_transform_dict):
    '''Converts las points from las coordinates to geospatial coordinates
    
    Arguments:
        las_data: np array of points as [X, Y, Z] as returned by load_las
        las_transform_dict: dict, transformation parameters of points for LAS coords to geospatial coords
        
    Returns:
        transformed_las_data: np array of points as [X, Y, Z] in geospatial coords
    '''
    # Convert las data to float
    transformed_las_data = las_data.astype('float')
    # Transform in x, y, z
    transformed_las_data[:,0] = ((las_data[:,0] * las_transform_dict['scalex']) + las_transform_dict['offsetx'])
    transformed_las_data[:,1] = ((las_data[:,1] * las_transform_dict['scaley']) + las_transform_dict['offsety'])
    transformed_las_data[:,2] = ((las_data[:,2] * las_transform_dict['scalez']) + las_transform_dict['offsetz'])
    
    return transformed_las_data

def las_to_px(las_data, las_transform_dict, ortho_transform_dict):
    '''Converts las points from las coordinates to pixel coordinates (x, y) of the orthophoto.
    (x, y) are transformed, z is converted to geospatial coordinates
    
    Arguments:
        las_data: np array of points as [X, Y, Z] as returned by load_las
        las_transform_dict: dict, transformation parameters of points for LAS coords to geospatial coords
        
    Returns:
        transformed_las_data: np array of points as [X, Y, Z] in pixel coords
    '''

    las_data = las_data.astype('float')
    las_data[:,0] = ((las_data[:,0] * las_transform_dict['scalex']) + las_transform_dict['offsetx'] - ortho_transform_dict['x0']) / ortho_transform_dict['px_w']
    las_data[:,1] = ((las_data[:,1] * las_transform_dict['scaley']) + las_transform_dict['offsety'] - ortho_transform_dict['y0']) / ortho_transform_dict['py_h']
    las_data[:,2] = ((las_data[:,2] * las_transform_dict['scalez']) + las_transform_dict['offsetz'])
    
    return las_data

def get_tree_from_las(tree_box: list, pointcloud):
    '''Inputs the pointcloud and the bounding box. Returns a subset of the pointcloud containing only points that are within the tree box.
        !!tree_box and pointcloud must be in the same coordinate system !!
        
    Arguments:
        tree_box: the tree bounding box, [xmin, ymin, xmax, ymax, ...]
        pointcloud: the pointcloud to subset from
    
    Returns:
        tree_pc: subset of pointcloud containing only points within tree_box bounds.
    '''

    # Get vertices from tree box  
    xmin = tree_box[0]
    ymin = tree_box[1]
    xmax = tree_box[2]
    ymax = tree_box[3]
    
    # Calculate indices based on bounds
    bound_x = np.logical_and(pointcloud[:, 0] > xmin, pointcloud[:, 0] < xmax)
    bound_y = np.logical_and(pointcloud[:, 1] > ymin, pointcloud[:, 1] < ymax)
    pc_ind = np.logical_and(bound_x, bound_y)
    
    # Raise a warning incase no points are found
    if len(pc_ind) == 0:
        warnings.warn('WARNING: No points found within tree bounding box! Are boxes and the pointcloud in the same coordinate system?')
    
    # Return subset
    tree_pc = pointcloud[pc_ind]
    return tree_pc