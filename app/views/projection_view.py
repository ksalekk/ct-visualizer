import pyqtgraph as pg
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QSlider, QWidget, QHBoxLayout

from app.helpers.enums import Location


class ProjectionWidget(QWidget):
    """
    Widget to display projection image and enable user to interact with projection model.

      Attributes
    ----------
        histogram_is_visible:
            flag that informs whether the histogram item is enabled/disabled
        roi_is_visible:
            as above
        __graphics_widget: pyqtgraph.GraphicsLayoutWidget
            widget to displaying pyqtgraph plot item
        image_area: ImageArea
            represents image area (viewbox, image item, roi and all related to displayed image)
        histogram: pyqtgraph.HistogramLUTItem
        slicing_slider:
            slider that allows to change slices in projection
    """
    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.histogram_is_visible = False
        self.roi_is_visible = False

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.__graphics_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.__graphics_widget)

        self.image_area = ImageArea()
        self.histogram = self.__create_histogram()
        self.__graphics_widget.ci.addItem(row=0, col=0, item=self.image_area)

        self.slicing_slider = self.__create_slider()
        layout.addWidget(self.slicing_slider)

    def __create_slider(self):
        """Create vertical slider. Changing slider value event emits ROI changed signal."""
        slider = QSlider(orientation=Qt.Orientation.Vertical)
        slider.valueChanged.connect(lambda x: self.image_area.roi.sigRegionChanged.emit(self.image_area.roi))
        return slider

    def __create_histogram(self):
        """Create vertical histogram (L=2000, W=2000)"""
        histogram = pg.HistogramLUTItem(orientation='vertical')
        histogram.setImageItem(self.image_area.image_item)
        histogram.setLevels(min=0, max=4000)
        return histogram

    def connect_signals(self, slider_changed_callback, roi_changed_callback, histogram_changed_callback):
        """Get callbacks that will be invoked when specified event occurs (slider value changed,
        roi changed, histogram changed)."""
        self.slicing_slider.valueChanged.connect(slider_changed_callback)
        self.image_area.roi.sigRegionChanged.connect(roi_changed_callback)
        self.histogram.sigLevelsChanged.connect(histogram_changed_callback)

    def update_image(self, image):
        """Get 2D numpy array and display it on widget"""
        prev_min, prev_max = self.histogram.getLevels()
        self.image_area.image_item.setImage(image)
        self.histogram.setLevels(prev_min, prev_max)

    def get_metadata_item(self, position):
        """Return metadata item for specified position: TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT
        (helpers.enums.Location)"""
        if position == Location.TOP_LEFT:
            return self.image_area.top_left_label
        elif position == Location.TOP_RIGHT:
            return self.image_area.top_right_label
        elif position == Location.BOTTOM_LEFT:
            return self.image_area.bottom_left_label
        elif position == Location.BOTTOM_RIGHT:
            return self.image_area.bottom_right_label
        else:
            raise ValueError(f"Unexpected position value: {position}")

    def get_image_item(self):
        """Return image item"""
        return self.image_area.image_item

    def reset_roi(self, position, size):
        """Display ROI window, set on specified position and with specified size"""
        self.image_area.set_roi_visibility(True)
        self.image_area.roi.setPos(position)
        self.image_area.roi.setSize(size)

    def set_histogram_visibility(self, visible):
        """Display (visible==True) or hide (visible==False) histogram."""
        if self.histogram_is_visible == visible:
            return

        self.histogram_is_visible = visible
        if visible:
            self.__graphics_widget.ci.addItem(row=0, col=1, item=self.histogram)
        else:
            self.__graphics_widget.ci.removeItem(self.histogram)

    def set_roi_visibility(self, visible):
        """Display (visible==True) or hide (visible==False) ROI window."""
        if self.roi_is_visible == visible:
            return

        self.roi_is_visible = visible
        if visible:
            self.image_area.addItem(self.image_area.roi)
            self.image_area.roi.sigRegionChanged.emit(self.image_area.roi)
        else:
            self.image_area.removeItem(self.image_area.roi)

    def set_slider(self, position=None, max_val=None):
        """Set slider on specified position and set specified max value"""
        if max_val is not None:
            self.slicing_slider.setMaximum(max_val)

        if position is not None:
            self.slicing_slider.setSliderPosition(position)

    def set_projection_orientation(self, up="", bottom="", left="", right=""):
        """Set orientation strings to specify image orientation"""
        (pg.LabelItem(text=up, size='16pt', parent=self.image_area)
            .anchor(itemPos=(0, 0), parentPos=(0.5, 0), offset=(0, 20)))
        (pg.LabelItem(text=bottom, size='16pt', parent=self.image_area)
            .anchor(itemPos=(0, 0), parentPos=(0.5, 1), offset=(0, -30)))
        (pg.LabelItem(text=left, size='16pt', parent=self.image_area)
            .anchor(itemPos=(0, 0), parentPos=(0, 0.5), offset=(10, 0)))
        (pg.LabelItem(text=right, size='16pt', parent=self.image_area)
            .anchor(itemPos=(0, 0), parentPos=(1, 0.5), offset=(-30, 0)))


class ImageArea(pg.PlotItem):
    """
    Represents the area, when user can interact with image. Allows to analyse ROIs and display metadata

    Attributes
    ----------
        image_item:
            image item in plot
        roi:
            roi item in plot
        __is_roi_hidden:
            flag that informs whether the roi item is enabled/disabled
        top_left_label:
            labels to displaying metadata in image area corners
        top_right_label
        bottom_left_label
        bottom_right_label
    """

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.getViewBox().setAspectLocked(True)
        self.hideAxis('bottom')
        self.hideAxis('left')

        self.image_item = self.__create_image_item()
        self.roi = self.__create_roi()

        self.__is_roi_hidden = True

        self.top_left_label = self.__create_metadata_item(Location.TOP_LEFT)
        self.top_right_label = self.__create_metadata_item(Location.TOP_RIGHT)
        self.bottom_left_label = self.__create_metadata_item(Location.BOTTOM_LEFT)
        self.bottom_right_label = self.__create_metadata_item(Location.BOTTOM_RIGHT)

    def __create_image_item(self):
        image_item = pg.ImageItem()
        self.addItem(image_item)
        return image_item

    def __create_roi(self):
        roi = pg.ROI(pos=[0, 0])
        roi.removable = True
        roi.setZValue(10)
        roi.addScaleHandle(pos=[1, 0], center=[0, 1])
        return roi

    def __create_metadata_item(self, position):
        md_item = MetadataItem(size='10pt')
        md_item.setParentItem(self)
        if position == Location.TOP_LEFT:
            md_item.anchor(itemPos=(0, 0), parentPos=(0, 0), offset=(10, 10))
        elif position == Location.TOP_RIGHT:
            md_item.anchor(itemPos=(1, 0), parentPos=(1, 0), offset=(-10, 10))
        elif position == Location.BOTTOM_LEFT:
            md_item.anchor(itemPos=(0, 1), parentPos=(0, 1), offset=(10, -10))
        elif position == Location.BOTTOM_RIGHT:
            md_item.anchor(itemPos=(1, 1), parentPos=(1, 1), offset=(-10, -10))
        else:
            raise ValueError(f"Unexpected position value: {position}")

        return md_item

    def update_roi_position(self, xy_position):
        """Move ROI window to specified position"""
        self.roi.setPos(xy_position)

    def set_roi_visibility(self, hide):
        """Hide or display roi window"""
        if self.__is_roi_hidden == hide:
            return

        if hide:
            self.roi.sigRegionChanged.disconnect(self.update_roi_position)
            self.removeItem(self.roi)
        else:
            self.roi.sigRegionChanged.connect(self.update_roi_position)
            self.addItem(self.roi)


class MetadataItem(pg.LabelItem):
    """
    ver 1.0
    Item that is displayed in plot as a metadata text.
    """
    def __init__(self, **args):
        super().__init__(**args)

    def set_metadata(self, metadata_dict, color=None, size='12pt', separator='<br>'):
        """Set metadata as dict. Entries are separated with <br> by default."""
        text = separator.join([f'{key}: {value}' for key, value in metadata_dict.items()])
        self.setText(text, color=color, size=size)

    def update(self, single_metadata: tuple, color, size, separator='<br>'):
        """Add single entry to metadata text."""
        md_key, md_value = single_metadata
        text = self.text
        text += f"{separator} {md_key}: {md_value}"
        self.setText(text, color=color, size=size)

    def clear(self):
        """Set metadata text as empty string."""
        self.setText("")

    def replace_line(self, line_number, new_line):
        """Replace line specified by his number in metadata dict and set new line."""
        text: str = self.text
        lines = text.split("<br>")
        lines[line_number] = new_line
        "<br>".join([line for line in lines])

    def r_align(self):
        """Set text right alignment in label. Not working in ver 1.0"""
        text: str = self.text
        # print(text)
        lines = text.split("<br>")
        max_length = max(len(line) for line in lines)
        # print(lines)
        aligned_lines = [line.rjust(max_length) for line in lines]
        result = "<br>".join(aligned_lines)
        result = result.replace(' ', '&nbsp;&nbsp;')
        # item: QtWidgets.QGraphicsTextItem = self.item
        # item.setFont(QtGui.QFont('Courier New'))
        # item.setHtml("<div style=\"color: blue\"></div>")
        self.setText(result)
