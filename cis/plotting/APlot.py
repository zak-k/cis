import logging
from abc import abstractmethod, ABCMeta

from matplotlib.ticker import MaxNLocator, AutoMinorLocator

from cis.utils import find_longitude_wrap_start


class APlot(object):

    __metaclass__ = ABCMeta

    # TODO: Reorder these into roughly the order they are most commonly used
    # @initializer
    def __init__(self, packed_data_items, ax=None, datagroup=0,
                 datagroups=None, logx=False, logy=False, xmin=None,
                 xmax=None, xstep=None, ymin=None, ymax=None, ystep=None,
                 grid=False, xlabel=None, ylabel=None, title=None, fontsize=None,
                 itemwidth=1, xtickangle=None, ytickangle=None,
                 xaxis=None, yaxis=None, *mplargs, **mplkwargs):
        """
        Constructor for Generic_Plot.
        Note: This also calls the plot method

        :param ax: The matplotlib axis on which to plot
        :param datagroup: The data group number in an overlay plot, 0 is the 'base' plot
        :param packed_data_items: A list of packed (i.e. Iris cubes or Ungridded data objects) data items
        :param plot_args: A dictionary of plot args that was created by plot.py
        :param mplargs: Any arguments to be passed directly into matplotlib
        :param mplkwargs: Any keyword arguments to be passed directly into matplotlib
        """
        import matplotlib.pyplot as plt

        self.packed_data_items = packed_data_items

        if ax is None:
            _, self.ax = plt.subplots()
        else:
            self.ax = ax

        self.datagroup = datagroup
        self.datagroups = datagroups
        self.logx = logx
        self.logy = logy
        self.xmin = xmin
        self.xmax = xmax
        self.xstep = xstep
        self.ymin = ymin
        self.ymax = ymax
        self.ystep = ystep
        self.grid = grid
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.fontsize = fontsize
        self.itemwidth = itemwidth
        self.xtickangle = xtickangle
        self.ytickangle = ytickangle
        self.xaxis = xaxis
        self.yaxis = yaxis

        self.mplargs = mplargs
        self.mplkwargs = mplkwargs

        self.color_axis = []

        self.assign_variables_to_x_and_y_axis()

        logging.debug("Unpacking the data items")
        self.set_x_wrap_start(xmin)
        self.offset_longitude = xmin != self.x_wrap_start
        self.unpacked_data_items = self.unpack_data_items()

        self.plot()


    @abstractmethod
    def plot(self):
        """
        The method that will do the plotting. To be implemented by each subclass of Generic_Plot.
        """
        pass

    @abstractmethod
    def format_plot(self):
        """
        The method that will format the plot. To be implemented by each subclass of Generic_Plot.
        """
        pass

    @abstractmethod
    def set_default_axis_label(self, axis):
        """
        The method that will set the default axis label. To be implemented by each subclass of Generic_Plot.
        :param axis: The axis of which to set the default label for. Either "x" or "y".
        """
        pass

    def format_units(self, units):
        """
        :param units: The units of a variable, as a string
        :return: The units surrounding brackets, or the empty string if no units given
        """
        if "since" in str(units):
            # Assume we are on a time if the units contain since.
            return ""
        elif units:
            return "(" + str(units) + ")"
        else:
            return ""


    def assign_variables_to_x_and_y_axis(self):
        """
        Overwrites which variable to used for the x and y axis
        Does not work for Iris Cubes
        :param main_arguments: The arguments received from the parser
        :param data: A list of packed data objects
        """
        import logging
        from cis.exceptions import NotEnoughAxesSpecifiedError

        x_variable = self.get_variable_name("x")

        if x_variable.lower().endswith('time') and len(self.packed_data_items) > 1:
            y_variable = 'default'
        else:
            y_variable = self.get_variable_name("y")

        if x_variable == y_variable:
            specified_axis = "x" if self.xaxis is not None else "y"
            not_specified_axis = "y" if specified_axis == "x" else "y"
            raise NotEnoughAxesSpecifiedError("-- {0} axis must also be specified if assigning the current {0} axis "
                                              "coordinate to the {1} axis".format(not_specified_axis, specified_axis))

        if "search" in x_variable:
            logging.info("Plotting unknown on the x axis")
        else:
            logging.info("Plotting " + x_variable + " on the x axis")

        if "search" in y_variable:
            logging.info("Plotting unknown on the y axis")
        else:
            logging.info("Plotting " + y_variable + " on the y axis")

        self.xaxis = x_variable
        self.yaxis = y_variable


    @staticmethod
    def name_preferring_standard(coord_item):
        for name in [coord_item.standard_name, coord_item.var_name, coord_item.long_name]:
            if name:
                return name
        return ''


    def get_variable_name(self, axis):
        import iris.exceptions as iris_ex
        import cis.exceptions as cis_ex

        # If the user has explicitly specified what variable they want plotting on the axis
        if getattr(self, axis + 'axis') is None:
            try:
                return self.name_preferring_standard(self.packed_data_items[0].coord(axis=axis.upper()))
            except (iris_ex.CoordinateNotFoundError, cis_ex.CoordinateNotFoundError):
                if axis == "x":
                    number_of_points_in_dimension = self.packed_data_items[0].shape[0]
                elif axis == "y":
                    if len(self.packed_data_items[0].shape) > 1:
                        number_of_points_in_dimension = self.packed_data_items[0].shape[1]
                    else:
                        return "default"

                for coord in self.packed_data_items[0].coords():
                    if coord.shape[0] == number_of_points_in_dimension:
                        return "search:" + str(number_of_points_in_dimension)
                return "default"
        else:
            return getattr(self, axis + 'axis')

    def auto_set_ticks(self):
        """
        Use the matplotlib.ticker class to automatically set nice values for the major and minor ticks.
        Log axes generally come out nicely spaced without needing manual intervention. For particularly narrow latitude
        vs longitude plots the ticks can come out overlapped, so an exception is included to deal with this.
        """
        from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

        y_variable = self.yaxis.lower()
        x_variable = self.yaxis.lower()

        ymin, ymax = self.matplotlib.get_ylim()

        # Matplotlib xlim doesn't work with cartopy plots
        xmin, xmax = self.xmin, self.xmax
        # xmin, xmax = self.matplotlib.xlim()

        max_x_bins = 9
        max_y_bins = 9

        xsteps = self.xstep
        ysteps = self.ystep

        lon_steps = [1, 3, 6, 9, 10]
        lat_steps = [1, 3, 6, 9, 10]
        variable_step = [1, 2, 4, 5, 10]

        if (xmax - xmin) < 5:
            lon_steps = variable_step
        if (ymax - ymin) < 5:
            lat_steps = variable_step

        # We need to make a special exception for particularly narrow and wide plots, which will be lat vs lon
        # preserving the aspect ratio. This gives more options for the spacing to try and find something that can use
        # the maximum number of bins.
        if x_variable.startswith('lon') and y_variable.startswith('lat'):
            max_y_bins = 7  # as plots are wider rather than taller
            if (ymax - ymin) > 2.2 * (xmax - xmin):
                max_x_bins = 4
                max_y_bins = 11
            elif (xmax - xmin) > 2.2 * (ymax - ymin):
                max_x_bins = 14
                max_y_bins = 4

        lat_or_lon = 'lat', 'lon'

        if xsteps is None and not self.logx:
            if self.xaxis.lower().startswith(lat_or_lon):
                lon_locator = MaxNLocator(nbins=max_x_bins, steps=lon_steps)
                if self.is_map():
                    self.cartopy_axis.set_xticks(lon_locator.tick_values(xmin, xmax), crs=self.transform)
                    self.cartopy_axis.xaxis.set_major_formatter(LongitudeFormatter())
                else:
                    self.matplotlib.axes().xaxis.set_major_locator(lon_locator)
            else:
                self.matplotlib.axes().xaxis.set_major_locator(MaxNLocator(nbins=max_x_bins, steps=variable_step))

            if not self.is_map():
                self.matplotlib.axes().xaxis.set_minor_locator(AutoMinorLocator())
                self.matplotlib.axes().xaxis.grid(False, which='minor')

        if ysteps is None and not self.logy:
            if y_variable.startswith(lat_or_lon):
                lat_locator = MaxNLocator(nbins=max_y_bins, steps=lat_steps)
                if self.is_map():
                    self.cartopy_axis.set_yticks(lat_locator.tick_values(ymin, ymax), crs=self.transform)
                    self.cartopy_axis.yaxis.set_major_formatter(LatitudeFormatter())
                else:
                    self.matplotlib.axes().yaxis.set_major_locator(lat_locator)
            else:
                self.matplotlib.axes().yaxis.set_major_locator(MaxNLocator(nbins=max_y_bins, steps=variable_step))

            if not self.is_map():
                self.matplotlib.axes().yaxis.set_minor_locator(AutoMinorLocator())
                self.matplotlib.axes().yaxis.grid(False, which='minor')


    def set_x_wrap_start(self, user_xmin):
        # FIND THE WRAP START OF THE DATA
        data_wrap_start = find_longitude_wrap_start(self.xaxis, self.packed_data_items)

        # NOW find the wrap start of the user specified range
        if user_xmin is not None:
            self.x_wrap_start = -180 if user_xmin < 0 else 0
        else:
            self.x_wrap_start = data_wrap_start


    def get_data_items_max(self):
        import numpy as np
        data_max = np.nanmax(self.unpacked_data_items[0]['x'])
        for i in self.unpacked_data_items:
            data_max = max([np.nanmax(i["x"]), data_max])
        return data_max


    def unpack_data_items(self):
        def __get_data(axis):
            variable = getattr(self, axis + 'axis')
            if variable == "default" or variable == self.packed_data_items[0].name() \
                    or variable == self.packed_data_items[0].standard_name \
                    or variable == self.packed_data_items[0].long_name:
                return self.packed_data_items[0].data
            else:
                if variable.startswith("search"):
                    number_of_points = float(variable.split(":")[1])
                    for coord in self.packed_data_items[0].coords():
                        if coord.shape[0] == number_of_points:
                            break
                else:
                    coord = self.packed_data_items[0].coord(variable)
                return coord.points if isinstance(self.packed_data_items[0], Cube) else coord.data

        def __set_variable_as_data(axis):
            old_variable = getattr(self, axis + 'axis')
            setattr(self, axis + '_axis', self.packed_data_items[0].name())
            logging.info("Plotting " + getattr(self,
                                               axis + 'axis') + " on the " + axis + " axis as " + old_variable + " has length 1")

        def __swap_x_and_y_variables():
            temp = self.xaxis
            self.xaxis = self.yaxis
            self.yaxis = temp

        from cis.utils import unpack_data_object
        from iris.cube import Cube
        import logging
        if len(self.packed_data_items[0].shape) == 1:
            x_data = __get_data("x")
            y_data = __get_data("y")

            if len(x_data) == 1 and len(y_data) == len(self.packed_data_items[0].data):
                __set_variable_as_data("x")
            elif len(y_data) == 1 and len(x_data) == len(self.packed_data_items[0].data):
                __set_variable_as_data("y")
            else:
                try:
                    if (x_data == y_data).all():
                        __swap_x_and_y_variables()
                except AttributeError:
                    if x_data == y_data:
                        __swap_x_and_y_variables()

        return [unpack_data_object(packed_data_item, self.xaxis, self.yaxis,
                                   self.x_wrap_start) for packed_data_item in self.packed_data_items]

    def unpack_comparative_data(self):
        return [{"data": packed_data_item.data} for packed_data_item in self.packed_data_items]


    def calculate_axis_limits(self, axis, min_val, max_val):
        """
        Calculates the axis limits for a given axis
        :param axis: The axis for the limits to be calculated
        :return: A dictionary containing the min and max values of an array along a given axis
        """
        c_min, c_max = self.calc_min_and_max_vals_of_array_incl_log(axis,
                                                                    self.unpacked_data_items[
                                                                        0][axis])

        new_min = c_min if min_val is None else min_val
        new_max = c_max if max_val is None else max_val

        # If we are plotting air pressure we want to reverse it, as it is vertical coordinate decreasing with altitude
        if axis == "y" and self.yaxis == "air_pressure" and min_val is None and max_val is None:
            new_min, new_max = new_max, new_min

        return new_min, new_max


    def apply_axis_limits(self):
        """
        Applies the limits to the specified axis if given, or calculates them otherwise
        """

        self.xmin, self.xmax = self.calculate_axis_limits('x', self.xmin, self.xmax)
        ymin, ymax = self.calculate_axis_limits('y', self.ymin, self.ymax)

        if self.is_map():
            try:
                self.cartopy_axis.set_extent([self.xmin, self.xmax, ymin, ymax], crs=self.transform)
            except ValueError:
                self.cartopy_axis.set_extent([self.xmin, self.xmax, ymin, ymax], crs=self.projection)
        else:
            self.matplotlib.set_xlim(xmin=self.xmin, xmax=self.xmax)
            self.matplotlib.set_ylim(ymin=ymin, ymax=ymax)

    def create_legend(self):
        """
        Creates a draggable legend in the "best" location for the plot.
        Works out legend labels unless explicitly given to the parser in the datagroups argument.
        """
        legend_titles = []
        datagroups = self.datagroups
        for i, item in enumerate(self.packed_data_items):
            if datagroups is not None and datagroups[i]["label"]:
                legend_titles.append(datagroups[i]["label"])
            else:
                legend_titles.append(item.long_name)
        legend = self.matplotlib.legend(legend_titles, loc="best")
        legend.draggable(state=True)


    def set_axis_ticks(self, axis, no_of_dims):
        from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
        from numpy import arange

        tick_kwargs = {}

        if self.is_map():
            if axis == "x":
                coord_axis = "x"
                tick_method = self.cartopy_axis.set_xticks
                self.cartopy_axis.xaxis.set_major_formatter(LongitudeFormatter())
            elif axis == "y":
                coord_axis = "data" if no_of_dims == 2 else "y"
                tick_method = self.cartopy_axis.set_yticks
                self.cartopy_axis.yaxis.set_major_formatter(LatitudeFormatter())

            tick_kwargs['crs'] = self.transform
        else:
            if axis == "x":
                coord_axis = "x"
                tick_method = self.matplotlib.set_xticks
            elif axis == "y":
                coord_axis = "data" if no_of_dims == 2 else "y"
                tick_method = self.matplotlib.set_yticks

            #TODO: These other kwargs are going to be broken, I think I'll need to ask for the labels using get_labels, then use l.update(kwarg).

            # if self.plot_args.get(axis + "tickangle", None) is None:
            #     angle = None
                # tick_kwargs['ha'] = "center" if axis == "x" else "right"
            # else:
                # tick_kwargs['rotation'] = self.plot_args[axis + "tickangle"]
                # tick_kwargs['ha'] = "right"

        if getattr(self, axis + 'step') is not None:
            step = getattr(self, axis + 'step')

            if getattr(self, axis + "min") is None:
                min_val = min(unpacked_data_item[coord_axis].min() for unpacked_data_item in self.unpacked_data_items)
            else:
                min_val = getattr(self, axis + "min")

            if getattr(self, axis + "max") is None:
                max_val = max(unpacked_data_item[coord_axis].max() for unpacked_data_item in self.unpacked_data_items)
            else:
                max_val = getattr(self, axis + "max")

            ticks = arange(min_val, max_val + step, step)

            tick_method(ticks, **tick_kwargs)
        elif not self.is_map() and tick_kwargs:
            tick_method(**tick_kwargs)

    def format_time_axis(self):
        from cis.time_util import cis_standard_time_unit

        coords = self.packed_data_items[0].coords(standard_name=self.xaxis)
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(name_or_coord=self.xaxis)
        if len(coords) == 0:
            coords = self.packed_data_items[0].coords(long_name=self.xaxis)

        if len(coords) == 1:
            if coords[0].units == str(cis_standard_time_unit):
                self.matplotlib.xaxis_date()
                # self.set_x_axis_as_time()


    def calc_min_and_max_vals_of_array_incl_log(self, axis, array):
        """
        Calculates the min and max values of a given array.
        If a log scale is being used on the given axis, only positive values are taken into account
        :param axis: The axis to check if a log scale is being used for
        :param array: The array to calculate the min and max values of
        :return: The min and max values of the array
        """
        log_axis = getattr(self, "log" + axis)

        if log_axis:
            import numpy.ma as ma
            positive_array = ma.array(array, mask=array <= 0)
            min_val = positive_array.min()
            max_val = positive_array.max()
        else:
            min_val = array.min()
            max_val = array.max()
        return min_val, max_val


    def set_x_axis_as_time(self):
        from matplotlib import ticker
        from cis.time_util import convert_std_time_to_datetime

        ax = self.matplotlib.gca()

        def format_date(x, pos=None):
            return convert_std_time_to_datetime(x).strftime('%Y-%m-%d')

        def format_datetime(x, pos=None):
            # use iosformat rather than strftime as strftime can't handle dates before 1900 - the output is the same
            date_time = convert_std_time_to_datetime(x)
            day_range = self.matplotlib.gcf().axes[0].viewLim.x1 - self.matplotlib.gcf().axes[0].viewLim.x0
            if day_range < 1 and date_time.second == 0:
                return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute
            elif day_range < 1:
                return "%02d" % date_time.hour + ':' + "%02d" % date_time.minute + ':' + "%02d" % date_time.second
            elif day_range > 5:
                return str(date_time.date())
            else:
                return date_time.isoformat(' ')

        def format_time(x, pos=None):
            return convert_std_time_to_datetime(x).strftime('%H:%M:%S')

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_datetime))
        tick_angle = self.xtickangle
        if tick_angle is None:
            self.xtickangle = 45
        self.matplotlib.xticks(rotation=self.xtickangle, ha="right")
        # Give extra spacing at bottom of plot due to rotated labels
        self.matplotlib.gcf().subplots_adjust(bottom=0.3)

        # ax.xaxis.set_minor_formatter(ticker.FuncFormatter(format_time))


    def set_font_size(self):
        """
        Converts the fontsize argument (if specified) from a float into a dictionary that matplotlib can recognise.
        Could be further extended to allow specifying bold, and other font formatting
        """
        if self.fontsize is not None:
            self.mplkwargs["fontsize"] = {"font.size": float(self.fontsize)}


    def is_map(self):
        """
        :return: A boolean saying if the first packed data item contains lat and lon coordinates
        """
        from iris.exceptions import CoordinateNotFoundError as irisNotFoundError
        from cis.exceptions import CoordinateNotFoundError as cisNotFoundError
        try:
            x = self.packed_data_items[0].coord(self.xaxis)
            y = self.packed_data_items[0].coord(self.yaxis)
        except (cisNotFoundError, irisNotFoundError):
            return False

        if x.name().lower().startswith("lon") and y.name().lower().startswith("lat"):
            return True
        else:
            return False


    def set_log_scale(self, logx, logy):
        """
        Sets a log (base 10) scale (if specified) on the axes
        :param logx: A boolean specifying whether or not to apply a log scale to the x axis
        :param logy: A boolean specifying whether or not to apply a log scale to the y axis
        """
        if logx:
            self.matplotlib.set_xscale("log")
        if logy:
            self.matplotlib.set_yscale("log")


    def set_axes_ticks(self, no_of_dims):
        self.set_axis_ticks("x", no_of_dims)
        self.set_axis_ticks("y", no_of_dims)

