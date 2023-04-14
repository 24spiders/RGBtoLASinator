# RGBtoLASinator
A simple package that reads 2D annotations and infers the third dimension, allowing for annotated pointclouds


## USAGE
### Converting Annots
1. Clone the repo to your system
2. Navigate to the directory
3. To convert annotations
4. 
```python convert_annots.py --las-file "path_to_las_file" --tif-file "path_to_tif_file" --xml-file "path_to_annotation_xml_file" --save-path "out_path/filename.xml" --bottom-per 1 --top-per 99 --use-class```

Note: `bottom-per` and `top-per` are the percentile to use when defining the top and bottom of the tree.

Note: Only pass `--use-class` if you have a classified pointcloud, and you want to use ground class to find the bottom and vegetation class to find the top


### Plotting
To assess the boxes, a plotting function has been included that plots a side view of the tree pointclouds, as well as the top and bottom bounds that were chosen
1. Clone the repo to your system
2. Navigate to the directory
3. To plot

```python box_plots.py --las-file "path_to_las_file" --converted-xml "path_to_output_xml_from_convert_annots.py" --save-folder "path_to_folder_to_save_plots_to"```
