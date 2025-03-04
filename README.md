# RGBtoLASinator
A simple package that reads 2D annotations and infers the third dimension, allowing for annotated pointclouds

![alt text](https://github.com/WildFire-ML/RGBtoLASinator/blob/main/img/plot_example.png?raw=true)

This package reads an annotated tif and its corresponding annotations, as well as the pointcloud overlapping it. It then performs a coordinate transformation so the 2D image annotations are overlaid on the 3D pointcloud. Then, z (vertical) bounds of the box are made by analyzing the points that fall within the 2D box, thus creating a 3D box. Finally, writes an xml containing x,y,z (in geospatial coordinates), and label information for the box. Also includes a plotting tool for assessing the performance

## INSTALLATION
The package doesn't need to be installed for you to use the converter. But if installation is preferrable, you can install it in developer mode by navigating to the clone directory and using

```python setup.py develop```

## USAGE
### Converting Annots
1. Clone the repo to your system
2. Navigate to the directory
3. To convert annotations

```python convert_annots.py --las-file "path_to_las_file" --tif-file "path_to_tif_file" --xml-file "path_to_annotation_xml_file" --save-path "out_path/filename.xml" --bottom-per 1 --top-per 99 --use-class```

Note: `bottom-per` and `top-per` are the percentile to use when defining the top and bottom of the tree.

Note: Only pass `--use-class` if you have a classified pointcloud, and you want to use ground class to find the bottom and vegetation class to find the top


### Plotting
To assess the boxes, a plotting function has been included that plots a side view of the tree pointclouds, as well as the top and bottom bounds that were chosen
1. Clone the repo to your system
2. Navigate to the directory
3. To plot

```python box_plots.py --las-file "path_to_las_file" --converted-xml "path_to_output_xml_from_convert_annots.py" --save-folder "path_to_folder_to_save_plots_to"```
