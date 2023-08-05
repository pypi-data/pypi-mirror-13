[![PyPI version](https://badge.fury.io/py/pyBigWig.svg)](https://badge.fury.io/py/pyBigWig) [![Travis-CI status](https://travis-ci.org/dpryan79/pyBigWig.svg?branch=master)](https://travis-ci.org/dpryan79/pyBigWig.svg?branch=master)

# pyBigWig
A python extension written in C for quick access to bigWig files. This extension uses [libBigWig](https://github.com/dpryan79/libBigWig) for local and remote file access.

# Installation
You can install this extension directly from github with:

    pip install git+git://github.com/dpryan79/pyBigWig.git

# Usage
Basic usage is as follows:

## Load the extension

    >>> import pyBigWig

## Open a bigWig file

This will work if your working directory is the pyBigWig source code directory.

    >>> bw = pyBigWig.open("test/test.bw")

Note that if the file doesn't exist you'll see an error message and `None` will be returned.

## Access the list of chromosomes and their lengths

`bigWigFile` objects contain a dictionary holding the chromosome lengths, which can be accessed with the `chroms()` accessor.

    >>> bw.chroms()
    dict_proxy({'1': 195471971L, '10': 130694993L})

You can also directly query a particular chromosome.

    >>> bw.chroms("1")
    195471971L

The lengths are stored a the "long" integer type, which is why there's an `L` suffix. If you specify a non-existant chromosome then nothing is output.

    >>> bw.chroms("c")
    >>> 

## Print the header

It's sometimes useful to print a bigWig's header. This is presented here as a python dictionary containing: the version (typically `4`), the number of zoom levels (`nLevels`), the number of bases described (`nBasesCovered`), the minimum value (`minVal`), the maximum value (`maxVal`), the sum of all values (`sumData`), and the sum of all squared values (`sumSquared`). The last two of these are needed for determining the mean and standard deviation.

    >>> bw.header()
    {'maxVal': 2L, 'sumData': 272L, 'minVal': 0L, 'version': 4L, 'sumSquared': 500L, 'nLevels': 1L, 'nBasesCovered': 154L}

## Compute summary information on a range

BigWig files are used to store values associated with positions and ranges of them. Typically we want to quickly access the average value over a range, which is very simple:

    >>> bw.stats("1", 0, 3)
    [0.2000000054637591]

Suppose instead of the mean value, we instead wanted the maximum value:

    >>> bw.stats("1", 0, 3, type="max")
    [0.30000001192092896]

Other options are "min" (the minimum value), "coverage" (the fraction of bases covered), and "std" (the standard deviation of the values).

It's often the case that we would instead like to compute values of some number of evenly spaced bins in a given interval, which is also simple:

    >>> bw.stats("1",99,200, type="max", nBins=2)
    [1.399999976158142, 1.5]

`nBins` defaults to 1, just as `type` defaults to `mean`.

If the start and end positions are omitted then the entire chromosome is used:

    >>> bw.stats("1")
    [1.3351851569281683]

## Retrieve values for individual bases in a range

While the `stats()` method **can** be used to retrieve the original values for each base (e.g., by setting `nBins` to the number of bases), it's preferable to instead use the `values()` accessor.

    >>> bw.values("1", 0, 3)
    [0.10000000149011612, 0.20000000298023224, 0.30000001192092896]

The list produced will always contain one value for every base in the range specified. If a particular base has no associated value in the bigWig file then the returned value will be `nan`.

    >>> bw.values("1", 0, 4)
    [0.10000000149011612, 0.20000000298023224, 0.30000001192092896, nan]

## Retrieve all intervals in a range

Sometimes it's convenient to retrieve all entries overlapping some range. This can be done with the `intervals()` function:

    >>> bw.intervals("1", 0, 3)
    ((0, 1, 0.10000000149011612), (1, 2, 0.20000000298023224), (2, 3, 0.30000001192092896))

What's returned is a list of tuples containing: the start position, end end position, and the value. Thus, the example above has values of `0.1`, `0.2`, and `0.3` at positions `0`, `1`, and `2`, respectively.

If the start and end position are omitted then all intervals on the chromosome specified are returned:

    >>> bw.intervals("1")
    ((0, 1, 0.10000000149011612), (1, 2, 0.20000000298023224), (2, 3, 0.30000001192092896), (100, 150, 1.399999976158142), (150, 151, 1.5))

## Close a bigWig file

A file can be closed with a simple `bw.close()`, as is commonly done with other file types.

# A note on coordinates

Wiggle and BigWig files use 0-based half-open coordinates, which are also used by this extension. So to access the value for the first base on `chr1`, one would specify the starting position as `0` and the end position as `1`. Similarly, bases 100 to 115 would have a start of `99` and an end of `115`. This is simply for the sake of consistency with the underlying bigWig file and may change in the future.

# To do

 - [ ] Writer functions? It's unclear how much these would even be used.
 - [X] The global curl cleanup stuff isn't being done at all currently.
