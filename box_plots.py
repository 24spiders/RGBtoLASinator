# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 16:25:50 2023

@author: Liam
"""

# Import General
import argparse
import os

# Import from package
from rgbtolasinator.figures.pc_figures import plot_tree_projection
from rgbtolasinator.converter.utils import load_las, read_pascalvoc, project_las_geospatial
from rgbtolasinator.figures.tif_figures import plot_height_tif


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--las-file', type=str, help='path to the las file')
    parser.add_argument('--tif-file', type=str, help='path to the tif file')
    parser.add_argument('--converted-xml', type=str, help='path to the converted xml (from convert_annots)')
    parser.add_argument('--save-folder', type=str, default='./plots/', help='folder to save the plots')

    args = parser.parse_args()

    # Make the output path
    try:
        os.mkdir(args.save_folder)
    except FileExistsError:
        print(f'{args.save_folder} already exists and will be used\n')
    # Load converted boxes
    print('Loading annotations...\n')
    name, boxes = read_pascalvoc(args.converted_xml)
    print('Annotations loaded!\n')

    # Load LAS
    print('Loading las...\n')
    las, las_transform_dict = load_las(args.las_file)
    las = project_las_geospatial(las, las_transform_dict)
    print('Las loaded!\n')

    # Plot
    print('Plotting...\n')
    plot_tree_projection(boxes, las, args.save_folder)
    plot_height_tif(boxes, args.tif_file, args.save_folder)
    print('Plotting complete!\n')
