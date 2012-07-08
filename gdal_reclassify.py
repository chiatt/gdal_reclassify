#!/usr/bin/env python
import optparse
from osgeo import gdal
from gdalconst import *
import numpy as np
import operator

gdal.AllRegister()


def getIntType(array_of_numbers):
    low, high = min(array_of_numbers), max(array_of_numbers)
    int_types = [
        (0, 255, np.uint8),
        (-128, 127, np.int16),
        (0, 65535, np.uint16),
        (-32768, 32767, np.int16),
        (0, 4294967295, np.uint32),
        (-2147483648, 2147483647, np.int32),
        (0, 18446744073709551615, np.uint64),
        (-9223372036854775808, 9223372036854775807, np.int64)
        ]

    for i in int_types:
        if low >= i[0] and high <= i[1]:
            int_np_type = i[2]
            break
    return int_np_type


def parseOutClasses(number_string):
    data_types = {
            np.dtype(np.uint8): GDT_Byte,
            np.dtype(np.int8): GDT_Int16,
            np.dtype(np.uint16): GDT_UInt16,
            np.dtype(np.int16): GDT_Int16,
            np.dtype(np.uint32): GDT_UInt32,
            np.dtype(np.int32): GDT_Int32,
            np.dtype(np.float32): GDT_Float32,
            np.dtype(np.int64): GDT_Int32,
            np.dtype(np.float64): GDT_Float32
        }

    out_classes = [i.strip() for i in number_string]
    pytype = int
    np_dtype = np.int
    for i in out_classes:
        if '.' in i:
            pytype = float
    out_classes_parsed = [pytype(g) for g in out_classes]
    if pytype == float:
        np_dtype = np.float_
    else:
        np_dtype = getIntType(out_classes_parsed)
    gdal_dtype = data_types[np.dtype(np_dtype)]
    return np_dtype, gdal_dtype, out_classes_parsed


def parseInClasses(in_classes, pytype):
    in_classes_parsed = []
    for i in in_classes:
        x = i.split(" ")
        in_classes_parsed.append((x[0].strip(), pytype(x[1].strip())))
    return in_classes_parsed


def reclassArray(np_array, in_classes, out_classes, np_dtype, default):
    if np_dtype not in (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64):
        in_array = np_array.astype(float)
    else:
        in_array = np_array
    op_dict = {"<": operator.lt, "<=": operator.le, "==": operator.eq,
        "!=": operator.ne, ">=": operator.ge, ">": operator.gt}
    try:
        rr = np.piecewise(in_array, [op_dict[i[0]](in_array,i[1]) for i in in_classes], out_classes)
        #rr = np.select([op_dict[i[0]](in_array,i[1]) for i in in_classes_parsed], out_classes, default)
        r = rr.astype(np_dtype)
    finally:
        in_array = None
    return r


def processDataset(infile, outfile, classes, reclasses, default, nodata):
    """
    Much of the code in this function relating to reading and writing gdal
    datasets - especially reading block by block was acquired from
    Chris Garrard's Utah State Python Programming GIS slides:
        http://www.gis.usu.edu/~chrisg/
    """
    if default:
        print default
        reclasses.append(default)
    np_dtype, gdal_dtype, out_classes, = parseOutClasses(reclasses)
    src_ds = gdal.Open(infile)
    if src_ds is None:
        print 'Could not open image'
        sys.exit(1)
    rows, cols = src_ds.RasterYSize, src_ds.RasterXSize
    print rows
    print cols
    transform = src_ds.GetGeoTransform()
    block_size = src_ds.GetRasterBand(1).GetBlockSize()
    proj = src_ds.GetProjection()
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(outfile, cols, rows, 1, gdal_dtype)
    out_band = dst_ds.GetRasterBand(1)
    x_block_size = block_size[0]
    y_block_size = block_size[1]
    sample = src_ds.ReadAsArray(0, 0, 1, 1)
    pytype = float
    if sample.dtype in (np.uint8, np.int8, np.uint16, np.int16, np.uint32, np.int32, np.uint64):
        pytype = int
    in_classes = parseInClasses(classes, pytype)
    for i in range(0, rows, y_block_size):
        if i + y_block_size < rows:
            num_rows = y_block_size
        else:
            num_rows = rows - i
        for j in range(0, cols, x_block_size):
            if j + x_block_size < cols:
                num_cols = x_block_size
            else:
                num_cols = cols - j
            block = src_ds.ReadAsArray(j, i, num_cols, num_rows)
            reclassed_block = reclassArray(block, in_classes, out_classes, np_dtype, default)
            out_band.WriteArray(reclassed_block, j, i)
    out_band.FlushCache()
    out_band.GetStatistics(0, 1)
    dst_ds.SetGeoTransform(transform)
    if nodata in ["True", "true"]:
        print nodata
        try:
            nodata_value = int(default)
        except:
            nodata_value = float(default)
        out_band.SetNoDataValue(nodata_value)
    dst_ds.SetProjection(proj)
    src_ds = None


def main():
    p = optparse.OptionParser()
    p.add_option('--conditions', '-c', default=[], help=("A comma delimited"
        " string of values to be reclassified. Comparison operators must be"
        " separated from values with a space."
        "  EXAMPLE: '< 1, == 3, > 45'"))
    p.add_option('--result_classes', '-r', default=[], help=("Output classes."
        " A comma delimited string of values.  The number of input classes must"
        " match the number of result values. The order of the output classes"
        " must match the order of the input classes.  EXAMPLE: '5, 6, 7'"))
    p.add_option('--default', '-d', default=False, help=("Value used to fill"
        " pixels that do not meet any conditions of the input classes."))
    p.add_option('--default_as_nodata', '-n', default=[], help=("Setting to"
        " 'true' sets the default value as the nodata value."))
    options, arguments = p.parse_args()
    src_file, dst_file, str_cond, str_reclass = arguments[0], arguments[1], options.conditions, options.result_classes
    in_classes = [i.strip() for i in str_cond.split(",")]
    out_classes = str_reclass.split(",")
    nodata = options.default_as_nodata
    default = options.default
    if len(in_classes) == len(out_classes):
        processDataset(src_file, dst_file, in_classes, out_classes, default, nodata)
    else:
        print "The number of conditions must equal the number of result classes."

if __name__ == '__main__':
    main()


