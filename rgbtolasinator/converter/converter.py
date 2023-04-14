# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:23:05 2023

@author: Liam
"""

import numpy as np
import warnings

def infer_z_bounds(tree_box: list, pointcloud, bottom_percentile = 1, top_percentile = 99):
    '''Inputs the pointcloud and a tree bounding box. Infers the zmin and zmax bounds of the tree box using the pointcloud.
    The zmax is defined as the top 99 percentile of points within the 2d bounding box
    The zmin is defined as the bottom 1 percentile of points within the 2d bounding box
    !! tree_box and pointcloud must be in the same coordinate system !!
    
    Arguments:
        tree_box: the tree bounding box, [xmin, ymin, xmax, ymax, ...]
        pointcloud: the pointcloud to subset from
        bottom_percentile: int, the percentile to define the bottom of the tree as
        top_percentile: int, the percentile to define the top of the tree as
        
    Returns:
        tree_box_with_z: [xmin, ymin, xmax, ymax, label, conf, zmin, zmax]
    '''
    # Get vertices from tree box  
    xmin = tree_box[0]
    ymin = tree_box[1]
    xmax = tree_box[2]
    ymax = tree_box[3]
    label = tree_box[4]
    conf = tree_box[5]
    
    
    # Calculate indices based on bounds
    bound_x = np.logical_and(pointcloud[:, 0] > xmin, pointcloud[:, 0] < xmax)
    bound_y = np.logical_and(pointcloud[:, 1] > ymin, pointcloud[:, 1] < ymax)
    pc_ind = np.logical_and(bound_x, bound_y)
    
    # Raise a warning incase no points are found
    if len(pc_ind) == 0:
        warnings.warn('WARNING: No points found within tree bounding box! Are boxes and the pointcloud in the same coordinate system?')
    
    # Return subset
    tree_pc = pointcloud[pc_ind]
    
    zmin = np.percentile(tree_pc[:,2], bottom_percentile)
    zmax = np.percentile(tree_pc[:,2], top_percentile)
    
    tree_box_with_z = [xmin, ymin, xmax, ymax, label, conf, zmin, zmax]
    
    return tree_box_with_z
