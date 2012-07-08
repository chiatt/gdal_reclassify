Description
============

A command-line tool to reclassify raster data using GDAL.

Requirements
=============

* python
* numpy
* gdal binaries
* python-gdal bindings

Usage
=======

gdal_reclassify.py [-c source_classes] [-r dest_classes] [-d default] [-n default_as_nodata] src_dataset dst_dataset

-c:
>Input classes as a comma-delimited string of value conditions that are to be reclassified. Comparison operators must be separated from values with a space. 

-r:
>Output classes as a comma-delimited string of values.  The number of input classes must match the number of result values. The order of
the output classes must match the order of the input classes. The output data type will match the datatype of the output classes.

-d:
>Default value. Value used to fill pixels that do not meet any conditions of the input classes. If no default value is specified, GDAL will determine the value for pixels that do not meet input class conditions.

-n: 
>No data. Setting to "true" sets the default value as the nodata value.  If not set to "true" GDAL will determine the nodata value based on the ouput data type.

src_dataset:
>The source file name. 

dst_dataset:
>The destination tiff file name. 


EXAMPLE: 

    source_dataset.tif destination_dataset.tif -c "< 1, == 3, > 45" -r "5, 6, 7" -d -99 -n true

Notes:
------

>Input classes are processed using numpy.piecewise. This means that in many cases, consecutive ranges should be defined using ">" rather than "<" to avoid classes over-riding each other.  For example "< 3, < 5, < 10" will produce one class that is less than 10, whereas "> 0, > 2, > 4" will produce 3 classes.

>Later versions will ouput different raster formats, but currently outputs must have the .tif extension. 

>Thanks to Chris Garrard for providing such great Python GDAL tutorials: http://www.gis.usu.edu/~chrisg/
