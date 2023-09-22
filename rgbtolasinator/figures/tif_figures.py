# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 12:27:20 2023

@author: Liam
"""

from PIL import Image, ImageDraw, ImageFont
from osgeo import gdal
import numpy as np
import os
from itamtsupport.utils.img_annot_utils import geo_to_px
import matplotlib

def plot_height_tif(geo_boxes: list, tif_file: str, save_folder: str, linewidth = 4):
    ''' Draws xml boxes on the image specified. Writes the tree number on each box, to correlate with the output from plot_tree_projection().
    Colors the boxes based on the estimated tree height
    Preserves geospatial projection of image.
    
    Arguments:
        boxes: list, CONVERTED xml boxes
        tif_file: str, the path to the image that was annotated
        save_folder: str, path to save the annotated tif
        linewidth: int, the box line thickness
        
    Returns:
        The path where the annotated image is saved
        Prints a geospatially projected tif in the save_folder, filename now ending in '_drawn_boxes.tif'
    '''
    # Open the image, start to draw
    im = Image.open(tif_file)
    im = im.convert('RGB')
    img_width, img_height = im.size
    draw = ImageDraw.Draw(im)
    
    # Convert boxes back to pixel coords for drawing
    px_boxes = geo_to_px(geo_boxes, tif_file)
    
    # Init cmap
    cmap = matplotlib.cm.get_cmap('viridis')
    max_height = 0
    for box in px_boxes:
        height = float(box[7])
        if height > max_height:
            max_height = height
    font = ImageFont.truetype("fonts/arial.ttf", size=90)
    
    # For each tree box in the predicted boxes
    tree_num = 0
    for box in px_boxes:
        # Get the coordinate values of the box around each tree (here we need to convert back to pixel!)
        xmin = box[0]
        ymin = box[1]
        xmax = box[2]
        ymax = box[3]
        relative_height = float(box[7]) / max_height
        color = cmap(relative_height)[0:3]
        color = [int(x*255) for x in color]
        color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
        draw.rectangle([xmin, ymin, xmax, ymax], fill=None, outline=color, width=linewidth)
        draw.text([xmax, ymax], str(tree_num), font=font)
        tree_num += 1
    # Open with tif data
    ds = gdal.Open(tif_file)
    # Projecting
    arr = np.array(im)
    [rows, cols, channels] = arr.shape
    driver = gdal.GetDriverByName('GTiff')
    out_path = os.path.join(save_folder, tif_file.replace('.tif','_drawn_boxes.tif'))
    outdata = driver.Create(out_path, cols, rows, channels, gdal.GDT_Byte)
    outdata.SetGeoTransform(ds.GetGeoTransform())
    outdata.SetProjection(ds.GetProjection())
    outdata.GetRasterBand(1).WriteArray(arr[:,:,0])
    outdata.GetRasterBand(2).WriteArray(arr[:,:,1])
    outdata.GetRasterBand(3).WriteArray(arr[:,:,2])
    if channels == 4:
        outdata.GetRasterBand(4).WriteArray(arr[:,:,3])
    outdata.FlushCache()
    outdata = None
    ds = None
    return out_path