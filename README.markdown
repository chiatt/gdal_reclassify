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
>Input classes as a comma-delimited string of value conditions that are to be reclassified. 

-r:
>Output classes as a comma-delimited string of values.  The number of input classes must match the number of result values. The order of
the output classes must match the order of the input classes. The output data type will match the datatype of the output classes.

-d:
>Default value. Value used to fill pixels that do not meet any conditions of the input classes. If no default value is specified, the default will be 0.

-n: 
>No data. Setting to "true" sets the default value as the nodata value.  If not set to "true" GDAL will determine the nodata value based on the ouput data type.

-p: 
>GDAL compression method. Examples:'COMPRESS=LZW','COMPRESS=PACKBITS','COMPRESS=DEFLATE' or 'COMPRESS=JPEG'. By default gdal_reclassfiy uses no compression. More information on compression can be found here: http://gis.stackexchange.com/a/1105/4701.

src_dataset:
>The source file name. 

dst_dataset:
>The destination tiff file name. 


EXAMPLE: 

        python gdal_reclassify.py source_dataset.tif destination_dataset.tif -c "<30, <50, <80, ==130, <210"
        -r "1, 2, 3, 4, 5" -d 0 -n true -p "COMPRESS=LZW"


Notes:
------

>Input classes are processed using numpy.select. This means that in many cases, consecutive ranges should be defined using "<" rather than ">" to avoid classes over-riding each other.  For example "> 0, > 2, > 4" will produce one class that is greater than 4 trumping the first two conditions, whereas "< 3, < 5, < 10" will produce 3 classes.

>Later versions will ouput different raster formats, but currently outputs must have the .tif extension. 

>Thanks to Chris Garrard for providing such great Python GDAL tutorials: http://www.gis.usu.edu/~chrisg/
