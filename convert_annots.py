# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:30:30 2023

@author: Liam
"""
# Import General
import argparse
from tqdm import tqdm

# Import from package
from rgbtolasinator.converter.convert import infer_z_bounds
from rgbtolasinator.converter.utils import read_pascalvoc, write_pascalvoc, px_to_geo, load_las, project_las_geospatial


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--las-file', type=str, help='path to the las file')
    parser.add_argument('--xml-file', type=str, help='path to PascalVOC image annotations')
    parser.add_argument('--tif-file', type=str, help='path to the geospatially projected tif file the annotations are associated with')
    parser.add_argument('--save-path', type=str, default='converted_annots.xml', help='where to save the converted annots (ends in .xml)')
    parser.add_argument('--bottom-per', type=int, default=1, help='int, the percentile to define the bottom of the tree as')
    parser.add_argument('--top-per', type=int, default=99, help='int, the percentile to define the top of the tree as')
    parser.add_argument('--use-class', action='store_true', help='if passed, use class to define bounds. If passed, bottom_per considers only ground points and top_per considers only veg points')

    args = parser.parse_args()

    print('Loading LiDAR...\n')
    # Load PC
    las_data, las_transform_dict = load_las(args.las_file)
    las_data = project_las_geospatial(las_data, las_transform_dict)
    print('LiDAR Loaded!\n')

    print('Loading Annotations...\n')
    # Load annots
    name, px_boxes = read_pascalvoc(args.xml_file)
    geo_boxes = px_to_geo(px_boxes, args.tif_file)
    print('Annotations Loaded!\n')

    print('Converting...\n')
    # Convert
    boxes_3d = []
    pbar = tqdm(total=len(geo_boxes))
    for box in geo_boxes:
        box_3d = infer_z_bounds(box, las_data, bottom_percentile=args.bottom_per, top_percentile=args.top_per, use_class=args.use_class)
        boxes_3d.append(box_3d)
        pbar.update(1)
    print('Conversion Complete!\n')

    print('Writing file...\n')
    # Write
    write_pascalvoc(boxes_3d, args.save_path)
    print(f'File saved to {args.save_path}!\n')
    print('Complete!\n')
