# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:20:58 2023

@author: Liam
"""

import numpy as np
import os
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import warnings
from rgbtolasinator.converter.utils import get_tree_from_las
from tqdm import tqdm


def _tree_cmap():
    """Creates a tree colormap (brown to green)

    Returns:
        treecmap (matplotlib ListedColormap): A ListedColormap (brown to green)
    """
    # Create a colormap
    N = 256
    vals = np.ones((N, 4))
    vals[0:75, 0] = np.linspace(102/256, 0, 75)
    vals[75:, 0] = 0
    vals[0:75, 1] = np.linspace(51/256, 102/256, 75)
    vals[75:, 1] = 102/256
    vals[:, 2] = np.linspace(0/256, 0, N)
    treecmap = ListedColormap(vals)
    return treecmap


def plot_tree_projection(boxes: list, pointcloud, save_folder):
    """
    Plots a 2d projection of the trees. POINTCLOUD and BOXES BOTH IN GEO COORDINATES (See  project_las_geospatial() and px_to_geo())

    Args:
        boxes (list): List of tree bounding boxes.
        pointcloud (np array): The pointcloud the trees are in
        save_folder (str): path to the folder to save the plots to

    Returns:
        Plots :)
    """
    cmap = _tree_cmap()
    ii = 0
    pbar = tqdm(total=len(boxes))
    for tree in boxes:
        tree_pc = get_tree_from_las(tree, pointcloud)
        if len(tree_pc) == 0:
            warnings.warn('No points within the tree box; Tree #' + str(ii))
            continue
        # Plot the 2d projection
        fig, axs = plt.subplots(1, 1)
        # Plot the height bars
        height_min = float(tree[6])
        height_max = float(tree[7])
        axs.axhline(y=height_max, color='r', linestyle='-', linewidth=3)
        axs.axhline(y=height_min, color='r', linestyle='-', linewidth=3)
        # Plot tree pc
        axs.scatter(tree_pc[:, 0], tree_pc[:, 2], s=0.25, c=tree_pc[:, 2], cmap=cmap)
        axs.set_xticks([])
        axs.set_xlabel('Projection of Tree in x-z Plane')
        axs.set_ylabel('Height (m)')
        axs.axis('scaled')
        fig.tight_layout()
        # fig.show()
        filename = str(ii) + '.png'
        d = os.path.join(save_folder, filename)
        fig.savefig(d, dpi=150)
        ii += 1
        pbar.update(1)
    pbar.close()
