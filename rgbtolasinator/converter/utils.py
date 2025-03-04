# -*- coding: utf-8 -*-
"""
Created on Thur Apr 13 12:33:48 2023

@author: Liam
"""
import numpy as np
import laspy as lp
import warnings
from osgeo import gdal
from pascal_voc_writer import Writer
from csv import writer


# %% Annotation utils
def read_pascalvoc(xml_file: str):
    """This function takes in an xml file, and returns a nested list of box coordinates, and the box's type

    Args:
        xml_file (str): str, path to annotation file to be read

    Returns:
        filename (str): str, name of the file that was read
        list_with_all_boxes (list): A list of lists with format [xmin, ymin, xmax, ymax, label, prediction_confidence, extra1, extra2]

    """
    # This was modified from: https://stackoverflow.com/questions/53317592/reading-pascal-voc-annotations-in-python
    import xml.etree.ElementTree as ET
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Initialize list
    list_with_all_boxes = []
    # For each box listed in the .xml file
    filename = root.find('filename').text
    for boxes in root.iter('object'):
        # Initialize bounds, class
        ymin, xmin, ymax, xmax, label = None, None, None, None, None
        # Read the information from the .xml
        ymin = float(boxes.find("bndbox/ymin").text)
        xmin = float(boxes.find("bndbox/xmin").text)
        ymax = float(boxes.find("bndbox/ymax").text)
        xmax = float(boxes.find("bndbox/xmax").text)
        label = boxes.find("name").text
        conf = boxes.find('pose').text
        xtra1 = boxes.find("truncated").text
        xtra2 = boxes.find("difficult").text
        # Put the information into a list, append that list to master list to be output
        list_with_single_boxes = [xmin, ymin, xmax, ymax, label, conf, xtra1, xtra2]
        list_with_all_boxes.append(list_with_single_boxes)
    # Return the filename, and the list of all box bounds/classes
    return filename, list_with_all_boxes


def write_pascalvoc(boxes: list, xml_path: str):
    """
    This function writes the boxes to an xml in PASCALVOC format.
    'boxes' is a list of lists. A box in boxes is [xmin, ymin, xmax, ymax, label, conf, extra1, extra2]

    Args:
        boxes (list): Boxes to write to the xml file.
        xml_path (str): Path to save the xml

    Returns:
        xml_path (str): Path the xml was saved
    """
    # Init writer
    writer = Writer(xml_path[:-4], 0, 0)

    # Iterate through the boxes
    for box in boxes:
        xmin = box[0]
        ymin = box[1]
        xmax = box[2]
        ymax = box[3]
        label = box[4]
        conf = box[5]
        extra1 = box[6]
        extra2 = box[7]
        # Add box to the output
        writer.addObject(label, xmin, ymin, xmax, ymax, conf, extra1, extra2)

    # Save the file
    writer.save(xml_path)
    return xml_path


# %% Ortho Utils
def get_tif_transform(tif_file: str):
    """Gets the required tranformation parameters to convert from geospatial coordinates to pixel coords
    Note: From geo to pix: x_pix = (x_geo - x0) / px_w
    from pix to geo: xgeo = x_pix * px_w + x0
    Arguments:
        tif_file (str): path to tif file

    Returns:
        x0, px_w, py_w, y0, px_h, py_h: transformation parameters
    """
    # Read the ortho, get transform params
    ortho = gdal.Open(tif_file)
    x0, px_w, py_w, y0, px_h, py_h = ortho.GetGeoTransform()
    return x0, px_w, py_w, y0, px_h, py_h


def px_to_geo(boxes: list, tif_file: str, print_csv=False):
    """Converts boxes from pixel coordinates to geospatial coordinate points

    Args:
        boxes (list): returned from read_pascalvoc
        tif_file (str): path to the associated raster
        print_csv (bool): whether or not to print a csv

    Returns:
        geo_boxes (list): [xmin_geo, ymin_geo, xmax_geo, ymax_geo, label, conf, box_x_geo, box_y_geo]
        Writes a csv file (if print_csv = True) at the tif file location of the tree detection in geospatial coordinates
    """
    # Init csv
    if print_csv:
        csv = open(tif_file.replace('.tif', '_geo.csv'), 'w', newline='')
        csv_writer = writer(csv, delimiter=',')
        fieldnames = ['image_path', 'x', 'y', 'xmin', 'ymin', 'xmax', 'ymax', 'label']
        csv_writer.writerow(fieldnames)
    # Get the tif transformation
    x0, px_w, py_w, y0, px_h, py_h = get_tif_transform(tif_file)
    geo_boxes = []
    # Iterate through the boxes
    for box in boxes:
        xmin = box[0]
        ymin = box[1]
        xmax = box[2]
        ymax = box[3]
        label = box[4]
        conf = box[5]
        # Get the stem location
        box_x = (xmax - xmin) / 2 + xmin
        box_y = (ymax - ymin) / 2 + ymin
        # Convert stem location to geospatial coordaintes
        box_x_geo = box_x * px_w + x0
        box_y_geo = box_y * py_h + y0
        if print_csv:
            csv_writer.writerow([tif_file, box_x_geo, box_y_geo, xmin, ymin, xmax, ymax, label])

        # Changing boxes to geo coordinates
        # Note y flips because the axes flip
        xmin_geo = xmin * px_w + x0
        xmax_geo = xmax * px_w + x0
        ymax_geo = ymin * py_h + y0
        ymin_geo = ymax * py_h + y0
        geo_boxes.append([xmin_geo, ymin_geo, xmax_geo, ymax_geo, label, conf, box_x_geo, box_y_geo])
    return geo_boxes


def geo_to_px(geo_boxes: list, tif_file: str):
    """
    Converts boxes from geospatial coordinates to pixel coordinates

    Args:

        geo_boxes (list): Geospatial boxes, [xmin_geo, ymin_geo, xmax_geo, ymax_geo, label, conf, box_x_geo, box_y_geo]
        tif_file (str):  path to the associated raster.

    Returns:
        px_boxes (list): boxes in pixel coordaintes

    """
    # Get the tif transformation
    ortho = gdal.Open(tif_file)
    x0, px_w, py_w, y0, px_h, py_h = ortho.GetGeoTransform()
    px_boxes = []
    for box in geo_boxes:
        xmin_geo = box[0]
        ymin_geo = box[1]
        xmax_geo = box[2]
        ymax_geo = box[3]
        label = box[4]
        conf = box[5]
        xtra1 = box[6]
        xtra2 = box[7]

        # Changing boxes to geo coordinates
        # Note y flips because the axes flip
        xmin = (xmin_geo - x0) / px_w
        xmax = (xmax_geo - x0) / px_w
        ymin = (ymax_geo - y0) / py_h
        ymax = (ymin_geo - y0) / py_h
        px_boxes.append([xmin, ymin, xmax, ymax, label, conf, xtra1, xtra2])
    return px_boxes


# %% LAS utils
def load_las(las_path):
    """Loads the las file at las_path. For class definitions, find "ASPRS LAS SPECIFICATION 1.4"

    Args:
        las_path (str): path to the las file

    Returns:
        las_data (np array): points as [X, Y, Z, Class]
        las_transform_dict (dict): transformation parameters of points for LAS coords to geospatial coords
    """
    if lp.__version__.startswith('1.'):
        inFile = lp.file.File(las_path, mode='r')
        las_data = np.vstack([inFile.X, inFile.Y, inFile.Z, inFile.Classification]).transpose()
    elif lp.__version__.startswith('2.'):
        inFile = lp.read(las_path)
        las_data = np.vstack([inFile.X, inFile.Y, inFile.Z, inFile.classification]).transpose()
    scalex = inFile.header.scale[0]
    offsetx = inFile.header.offset[0]
    scaley = inFile.header.scale[1]
    offsety = inFile.header.offset[1]
    scalez = inFile.header.scale[2]
    offsetz = inFile.header.offset[2]
    if lp.__version__.startswith('1.'):
        inFile.close()

    las_transform_dict = {'scalex': scalex, 'offsetx': offsetx, 'scaley': scaley,
                          'offsety': offsety, 'scalez': scalez, 'offsetz': offsetz}

    return las_data, las_transform_dict


def project_las_geospatial(las_data, las_transform_dict):
    """Converts las points from las coordinates to geospatial coordinates

    Args:
        las_data (np array): points as [X, Y, Z, Class]
        las_transform_dict (dict): transformation parameters of points for LAS coords to geospatial coords

    Returns:
        transformed_las_data (np array): points as [X, Y, Z] in geospatial coords
    """
    # Convert las data to float
    transformed_las_data = las_data.astype('float')
    # Transform in x, y, z
    transformed_las_data[:, 0] = ((las_data[:, 0] * las_transform_dict['scalex']) + las_transform_dict['offsetx'])
    transformed_las_data[:, 1] = ((las_data[:, 1] * las_transform_dict['scaley']) + las_transform_dict['offsety'])
    transformed_las_data[:, 2] = ((las_data[:, 2] * las_transform_dict['scalez']) + las_transform_dict['offsetz'])

    return transformed_las_data


def get_tree_from_las(tree_box: list, pointcloud):
    """Inputs the pointcloud and the bounding box. Returns a subset of the pointcloud containing only points that are within the tree box.
        !!tree_box and pointcloud must be in the same coordinate system !!

    Arguments:
        tree_box (list): the tree bounding box, [xmin, ymin, xmax, ymax, ...]
        pointcloud: the pointcloud to subset from

    Returns:
        tree_pc: subset of pointcloud containing only points within tree_box bounds.
    """

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
