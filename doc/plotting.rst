========
Plotting
========

Plotting is straightforward::

  $ cis plot $var:$filenames

This will attempt to locate the variable ``$var`` in all of the specified ``$filenames``, work out its metadata (e.g. units, labels, etc.) and the appropriate chart type to plot, so that a line graph is used for two dimensional data, a scatter plot is used for three dimensional ungridded data and a heatmap for three dimensional gridded data. Other types of chart can be specified using the ``--type`` option. Available options are:

`` line ``
  a simple line plot, for three dimensional data the third variable is represented by the line colour

`` scatter ``
  a scatter plot, for three dimensional data the third variable is represented by the maker

`` heatmap ``

`` contour ``

`` contourf ``
  a filled contour plot

`` histogram3d ``

`` histogram2d ``

`` comparativescatter ``

`` overlay ``
  a collection of plots overlaid on one another (see [#overlay])

`` scatteroverlay ``
  a heatmap overlayed with a scatter plot (see [#scatteroverlay])

Note that `` filenames `` is a non-optional argument used to specify the files to read the variable from. These can be specified as a comma seperated list of the following possibilities:

  #. A single filename - this should be the full path to the file
  #. A single directory - all files in this directory will be read
  #. A wildcarded filename - A filename with any wildcards compatible with the python module glob, so that *, ? and [] can all be used. E.g. /path/to/my/test*file_[0-9].

Note that when using option 2, the filenames in the directory will be automatically sorted into alphabetical order. When using option 3, the filenames matching the wildcard will also be sorted into alphabetical order. The order of the comma separated list will however remain as the user specified, e.g.::

  $ cis plot $var:filename1,filename2,wildc*rd,/my/dir/,filename3

would read filename1, then filename2, then all the files that match "wildc*rd" (in alphabetical order), then all the files in the directory "/my/dir/" (in alphabetical order) and then finally filename3.

There are a number of optional arguments, which should be entered as a comma separated list after the mandatory arguments, for example ``variable:filename:product=CisCol,edgecolor=black``. The options are:

`` color ``
  colour of markers, e.g. for scatter plot points or contour lines (see [#colours])

`` cmap ``
  colour map to use, e.g. for contour lines or heatmap (see [#colours])

`` cmin ``
  the minimum value for the colourmap

`` cmax``
  the maximum value for the colourmap

`` edgecolor ``
  colour of scatter marker edges (can be used to differentiate scatter markers with a colourmap from the background plot)

`` itemstyle ``
  shape of scatter marker

`` label ``
  name of datagroup for the legend

`` product ``
  the data product to use for the plot

Additional datagroup options for contour plots only:

``contnlevels``
  the number of levels for the contour plot

``contlevels``
  a list of levels for the contour plot, e.g. ``contlevels=[0,1,3,10]``

``contlabel``
  options are ``true`` or ``false``, if true then contour labels are shown

``contwidth``
  width of the contour lines

``contfontsize``
  size for labels on contour plot

Note that `` label `` refers to the label the plot will have on the legend, for example if a multi-series line graph or scatter plot is plotted. To set the labels of the axes, use ``--xlabel`` and ``--ylabel``. ``--cbarlabel`` can be used to set the label on the colour bar.

The axes can be specified with ``--xaxis`` and ``--yaxis``. Gridded data supports any coordinate axes available in the file, while ungridded data supports the following coordinate options (if available in the data):

  * `` latitude ``
  * `` longitude ``
  * `` time ``
  * `` altitude ``
  * `` air_pressure ``
  * `` $var `` - the variable being plotted

If the product is not specified, the program will attempt to figure out which product should be used based on the filename.  Click CommunityIntercomparisonSuite/DataProduct to see a list of available products and their file signatures, or run ``cis plot -h``.


Saving to a File
================

By default a plot will be displayed on screen. To save it to an image file instead, use the ``--output`` option. Available output types are png, pdf, ps, eps and svg, which can be selected using the appropriate filename extension, for example ``--output plot.svg``.


Plot Formatting
===============

There are a number of plot formatting options available:

`` --xlabel ``
  The label for the x axis

`` --ylabel ``
  The label for the y axis

`` --cbarlabel ``
  The label for the colorbar

`` --xtickangle ``
  The angle for the ticks on the x axis

`` --ytickangle ``
  The angle for the ticks on the y axis

`` --title ``
  The title of the plot

`` --itemwidth ``
  The width of an item. Unit are points in the case of a line, and points squared in the case of a scatter point

`` --fontsize ``
  The size of the font in points

`` --cmap ``
  The colour map to be used when plotting a 3D plot. A list of available colour maps can be found at http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps.

`` --height ``
  The height of the plot, in inches

`` --width ``
  The width of the plot, in inches

`` --xbinwidth ``
  The width of the histogram bins on the x axis

`` --ybinwidth ``
  The width of the histogram bins on the y axis

`` --cbarorient ``
  The orientation of the colour bar, either horizontal or vertical

`` --nocolourbar ``
  Hides the colour bar on a 3D plot 

`` --grid ``
  Shows grid lines

`` --plotwidth ``
  width of the plot in inches

`` --plotheight ``
  height of the plot in inches

`` --cbarscale ``
  this can be used to change the size of the colourbar when plotting, use --cbarscale 0.5 for lat-lon plots of the entire Earth (this is a temporary fix)

`` --coastlinescolour ``
  The colour of the coastlines on a map (see [#colours])

`` --nasabluemarble ``
  Use the NASA Blue Marble for the background, instead of coastlines, when doing lat-lon plots


Plotting a Specific Range of Values
===================================

The arguments `` --xmin, --xmax, --xstep, --ymin, --ymax, --ystep, --vmin, --vmax, --vstep`` can be used to specify the range of values to plot, where x and y correspond to the axes and v corresponds to the colours.

When the arguments refer to dates/times, they should be in the format `` "YYYY-MM-DD hh:mm:ss"``, where the time is optional. Note: The double quotes are necessary.

The `` step `` arguments are used to specify the tick spacing on the axes and `` vstep `` is used to specify the tick spacing on the colorbar.

When the `` step `` arguments refer to an amount of time, they should be in the format `` "$y$m$d$H$M$S" ``. 

E.g. To specify a tick spacing of one month and six seconds on the x axis, the following argument should be given:
`` --xstep 1m6S `` 

Note: If a value is negative, then an equals sign must be used, e.g.
`` --xmin=-5``.


Overlaying Multiple Plots
=========================

Using ``--type overlay`` allows multiple files to be specified on the command line to be plotted, each with its own type, which is specified as e.g. ``type=heatmap``, along with the other datagroup options. Currently supported plot types are ``heatmap``, ``contour``, ``contourf`` and ``scatter``. An additional datagroup option available is ``alpha``, which allows the transparency for a layer to be set. ``alpha`` take a value between 0 and 1, where 0 is completely transparent and 1 full opaque.

For example, to plot a heatmap and a contour plot the following options can be used::

  cis plot var1:file1:type=heatmap var2:file2:type=contour,color=white --type overlay --plotwidth 20 --plotheight 15 --cbarscale 0.5 -o overlay.png

Note that the first file specified is treated in a special way, from this the default plot dimensions are deduced, and the colorbar displayed will be for this datagroup only.

.. todo:: [CommunityIntercomparisonSuite/OverlayPlotExamples Overlay Plot Examples]


Scatter Overlay Plots
=====================

.. note::

   Note that scatteroverlay is to be depreciated, as the overlay option will allow a more general method for overlaying multiple datasets

Three types of plot overlay are currently available:

  * Overlaying several line graphs
  * Overlaying several scatter plots
  * Overlaying a heatmap with several scatter graphs

To overlay several line graphs or scatter plots, simply use the plot command as before, but simply specify multiple files and variables, e.g.::

  $ cis plot $var1:$filename1:edgecolor=black $var2:$filename2:edgecolor=red

To plot two variables from the same file, simply use the above command with `` $filename1 `` in place of `` $filename2 ``.

To overlay a heatmap with several scatter graphs, use the following command::

  $ cis plot $var1:$filename1:label=label1 $var2:$filename2:color=colour2,itemstyle=style2,label=label2 $var3:$filename3:color=colour3,itemstyle=style3,label=label3 --type scatteroverlay

Where `` $filename1 `` refers to the file containing the heatmap data and the other two filenames refer to the files containing the scatter data.
For a list of available scatter point styles, see [http://matplotlib.org/api/markers_api.html#module-matplotlib.markers this] website.
If the scatter data is 3 dimensional, then the colour argument can be omitted and the data will be plotted using the same colour map as the heatmap. This can be overridden by explicitly including the colour argument.

Plot Using a Log Scale
======================

A log scale can be plotted using the following commands:

  * `` --logx `` - The x axis will be plotted using a log scale of base 10
  * `` --logy `` - The y axis will be plotted using a log scale of base 10
  * `` --logv `` - The values (colours) will be plotted using a log scale of base 10

Available Colours
=================

`` cis `` recognises any valid  `html colour`_, specified using its name e.g. "red" (as opposed to its hex code) for options such as item colour (line/scatter colour) and the colour of the coast lines.

A list of available colour maps for 3D plots (e.g. heatmaps, contours, contourfs) can be found `here <http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps here>`_.

.. _`html colour`: http://www.w3schools.com/html/html_colornames.asp