# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 11:09:46 2023

@author: Liam
"""

from pascal_voc_writer import Writer

def read_pascalvoc(xml_file: str):
  '''This function takes in an xml file, and returns a nested list of box coordinates, and the box's type
  
  Arguments:
      xml_file: str, path to annotation file to be read
   
  Returns:
      filename: str, name of the file that was read
      list_with_all_boxes: list, A list of lists with format [xmin, ymin, xmax, ymax, label, prediction_confidence, extra1, extra2]
  
  '''
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
    ymin = int(float(boxes.find("bndbox/ymin").text))
    xmin = int(float(boxes.find("bndbox/xmin").text))
    ymax = int(float(boxes.find("bndbox/ymax").text))
    xmax = int(float(boxes.find("bndbox/xmax").text))
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
    '''
    This function writes the boxes to an xml in PASCALVOC format.
    'boxes' is a list of lists. A box in boxes is [xmin, ymin, xmax, ymax, label, conf, extra1, extra2]

    Parameters
    ----------
    boxes : list
        Boxes to write to the xml file.
    xml_path: str
        Path to save the xml

    Returns
    -------
    xml_path:
        Path the xml was saved

    '''
    
    # Init writer
    writer = Writer(xml_path[:-4], 0,0)
    
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

def px_to_geo(boxes: list, tif_file: str):
    ''' Converts boxes from pixel coordinates to geospatial coordinate points
    
    Arguments:
        boxes: list, returned from read_content
        tif_file: str, path to the associated raster
        print_csv: bool, whether or not to print a csv
    
    Returns:
        geo_boxes: list,[xmin_geo, ymin_geo, xmax_geo, ymax_geo, label, conf, box_x_geo, box_y_geo]
        Writes a csv file (if print_csv = True) at the tif file location of the tree detection in geospatial coordinates
    '''
    from osgeo import gdal
    # Get the tif transformation
    ortho = gdal.Open(tif_file)
    x0, px_w, py_w, y0, px_h, py_h = ortho.GetGeoTransform()
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
        
        # Changing boxes to geo coordinates
        # Note y flips because the axes flip
        xmin_geo = xmin * px_w + x0
        xmax_geo = xmax * px_w + x0
        ymax_geo = ymin * py_h + y0
        ymin_geo = ymax * py_h + y0
        geo_boxes.append([xmin_geo, ymin_geo, xmax_geo, ymax_geo, label, conf, box_x_geo, box_y_geo])
    return geo_boxes