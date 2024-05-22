import numpy as np

from PySide6.QtWidgets import QApplication
from pyqtgraph import HistogramLUTItem, ROI

from app.helpers.interfaces import EventsHandler
from app.helpers import dcm_manager
from app.helpers.enums import Plain, Location
from app.model.model import Model
from app.views.main_window import MainWindow
from app.views.projection_view import ProjectionWidget, MetadataItem


class MainController(EventsHandler):
    """
    Class to represent app controller in MVC architecture.

    Controller assumes that:
        - model is placed in right-handed XYZ space
        - patient is fixed in front of the observer (observer see XY plain)
        - X-axis runs from left to right in observer perspective
        - Y-axis runs from front to back in observer perspective
        - Z-axis runs from bottom to top in observer perspective

    Attributes
    ----------
        app: QApplication
        model: Model
        xy_widget: ProjectionWidget
        xz_widget: ProjectionWidget
        yz_widget: ProjectionWidget
        projection_widgets: dict(ProjectionWidget)
            may be more useful if we would like to display "custom" slices in the future (not only orthogonal)
    """

    def __init__(self,
                 app: QApplication,
                 model: Model,
                 projections: tuple[ProjectionWidget, ProjectionWidget, ProjectionWidget]):

        """
        Injecting dependencies to controller.

        Arguments:
            app (QApplication): app core object
            model (Model): main model of app
            projections (tuple): "empty" orthogonal projections widgets (projections order is irrelevant)
        """

        self.app = app
        self.model = model
        self.main_window: MainWindow = None
        self.xy_widget, self.xz_widget, self.yz_widget = projections
        self.projection_widgets = {Plain.XY: self.xy_widget, Plain.XZ: self.xz_widget, Plain.YZ: self.yz_widget}

    def set_main_window(self, main_window):
        """Connect main window to controller. It is necessary to do it before app starting."""
        self.main_window = main_window

    def load_model_handle(self, data_path: str | list[str]):
        """Load model data, fill projections widgets with model data and set main window working area."""

        if not data_path:
            return

        dcm_files = dcm_manager.get_dcm_from_path(data_path)
        ct_slices = dcm_manager.extract_ct_from_dcm(dcm_files)

        self.__model_preset(ct_slices)

        self.__set_projection_view(Plain.XY)
        self.__set_projection_view(Plain.XZ)
        self.__set_projection_view(Plain.YZ)

        self.main_window.set_working_area(self.xy_widget, self.xz_widget, self.yz_widget)
        self.main_window.show_toolbar()

    def change_slice_handle(self, n, plain):
        """Extract n-th slice in specified plain. Update model and views."""

        proj_widget = self.__get_projection_widget(plain)
        proj_model = self.model.get_projection_model(plain)

        img = self.__orthogonal_slicing(n, plain)
        proj_model.set_current_slice(img, n)
        proj_widget.update_image(img)

        updated_md = proj_model.update_img_metadata({
            "Slice": f"{n + 1}/{proj_model.get_slices_count()}"
        })
        proj_widget.get_metadata_item(Location.BOTTOM_LEFT).set_metadata(updated_md)

    def histogram_mode_handle(self, visible):
        """Based on visible value, hide (False) or display (True) histogram in all projection widgets"""
        for projection in self.projection_widgets.values():
            projection.set_histogram_visibility(visible)

    def histogram_changed_handle(self, histogram: HistogramLUTItem, plain):
        """Update windowing metadata in specified plain and based on changed histogram."""

        proj_widget = self.__get_projection_widget(plain)
        proj_model = self.model.get_projection_model(plain)

        if not proj_widget.histogram_is_visible:
            return

        min_val, max_val = proj_widget.histogram.getLevels()
        width = int(max_val - min_val)
        center = int(min_val + width/2)
        proj_model.update_img_metadata({
            "Window Width": str(width),
            "Window Level": str(center)
        })
        proj_widget.get_metadata_item(Location.BOTTOM_LEFT).set_metadata(proj_model.get_img_metadata())

    def roi_mode_handle(self, visible):
        """Based on visible value, hide (False) or display (True) ROI in all projection widgets"""
        for projection in self.projection_widgets.values():
            projection.set_roi_visibility(visible)
            if not visible:
                projection.get_metadata_item(Location.BOTTOM_RIGHT).clear()

    def roi_changed_handle(self, roi: ROI, plain, changed_size=True):
        """Update ROI metadata in specified plain and based on changed ROI. If ROI size has not been changed,
        keep previous calculated area"""

        proj_widget = self.__get_projection_widget(plain)
        proj_model = self.model.get_projection_model(plain)

        if not proj_widget.roi_is_visible:
            return

        img_item = proj_widget.get_image_item()
        roi_matrix = roi.getArrayRegion(data=proj_model.get_current_slice_img(), img=img_item)

        pixel_width, pixel_height = np.shape(roi_matrix)
        col_spacing, row_spacing = proj_model.get_spacings()

        prev_roi_size = proj_model.prev_roi_pix_size
        if not (pixel_width, pixel_height) == prev_roi_size:
            proj_model.prev_roi_pix_size = pixel_width, pixel_height
            roi_mm_area = pixel_width * col_spacing * pixel_height * row_spacing
            proj_model.update_roi_metadata({"Area": f"{roi_mm_area:.2f} mm2"})

        roi_mean = np.mean(roi_matrix)
        roi_std = np.std(roi_matrix)

        md_item: MetadataItem = proj_widget.get_metadata_item(Location.BOTTOM_RIGHT)
        proj_model.update_roi_metadata({
            "Mean": f"{roi_mean:.2f}",
            "Std Dev": f"{roi_std:.2f}"
        })
        md_item.set_metadata(proj_model.get_roi_metadata(), color='yellow')

    def quit_app_handle(self):
        self.app.exit(0)

    def __model_preset(self, ct_slices):
        """Set main model and projections models based on source dcm files.
         Set basic metadata about patient, examination and image"""

        matrix_3d = dcm_manager.get_ct_model_as_matrix(ct_slices, rot_k=1)
        self.model.set_model_matrix(matrix_3d)

        x_size, y_size, z_size = matrix_3d.shape
        metadata_slice = ct_slices[z_size // 2]

        slice_thickness = dcm_manager.get_ct_thickness(metadata_slice)
        row_spacing, col_spacing = dcm_manager.get_ct_pixel_spacing(metadata_slice)

        xy_model = self.model.get_projection_model(Plain.XY)
        xy_model.set_spacings(col_spacing, row_spacing, slice_thickness)
        xy_model.set_anatomical_plane("Axial")
        xy_model.set_projection_orientation({
            'up': "P",
            'bottom': "A",
            'left': "R",
            'right': "L"
        })

        xz_model = self.model.get_projection_model(Plain.XZ)
        xz_model.set_spacings(col_spacing, slice_thickness, row_spacing)
        xz_model.set_anatomical_plane("Coronal")
        xz_model.set_projection_orientation({
            'up': "S",
            'bottom': "I",
            'left': "R",
            'right': "L"
        })

        yz_model = self.model.get_projection_model(Plain.YZ)
        yz_model.set_spacings(row_spacing, slice_thickness, col_spacing)
        yz_model.set_anatomical_plane("Sagittal")
        yz_model.set_projection_orientation({
            'up': "S",
            'bottom': "I",
            'left': "A",
            'right': "P"
        })

        patient_data = dcm_manager.get_patient_data(metadata_slice)
        examination_data = dcm_manager.get_examination_data(metadata_slice)
        self.model.set_patient_metadata(patient_data)
        self.model.set_examination_metadata(examination_data)

        for model in [xy_model, xz_model, yz_model]:
            width, height = model.get_img_size()
            model.set_img_metadata({
                "Plane": model.get_anatomical_plane(),
                "Slice": "unknown",
                "Window Width": "4000",
                "Window Level": "2000",
                "Size": f"{width}x{height}",
                "Slice Thickness": f"{model.get_slices_thickness()}mm"
            })

            model.set_roi_metadata({
                "Area": "",
                "Mean": "",
                "Std Dev": ""
            })

    def __set_projection_view(self, plain):
        """Fill projection widget (in specified plain) with model data."""

        projection = self.__get_projection_widget(plain)
        model = self.model.get_projection_model(plain)

        slices_count = model.get_slices_count()
        projection.connect_signals(
            lambda slider: self.change_slice_handle(slider, plain),
            lambda roi: self.roi_changed_handle(roi, plain),
            lambda histogram: self.histogram_changed_handle(histogram, plain)
        )
        projection.set_slider(position=slices_count // 2, max_val=slices_count - 1)

        x = projection.image_area.image_item.width()
        y = projection.image_area.image_item.height()
        roi_size = 0.3 * min(x, y)

        projection.image_area.roi.setSize(roi_size)
        projection.image_area.roi.setPos(pos=((x-roi_size)/2, (y-roi_size)/2))

        top_left_md = projection.get_metadata_item(Location.TOP_LEFT)
        top_left_md.set_metadata(self.model.get_patient_metadata())

        top_right_md = projection.get_metadata_item(Location.TOP_RIGHT)
        top_right_md.set_metadata(self.model.get_examination_metadata())

        bottom_left_md = projection.get_metadata_item(Location.BOTTOM_LEFT)
        bottom_left_md.set_metadata(model.get_img_metadata())

        orientation = model.get_projection_orientation()
        projection.set_projection_orientation(**orientation)

    def __get_projection_widget(self, plain):
        """Return specified orthogonal widget"""
        return self.projection_widgets[plain]

    def __orthogonal_slicing(self, n, plain):
        """
        Calculate n-th slice in specified plain.
        - matrix_3d[n] / matrix_3d[n, :, :] => n-th row for each height and col (YZ slice / slice normal to x-axis)
        - matrix_3d[:, n] / matrix_3d[:, n, :] => n-th  col for each height and row (XZ slice / slice normal to y-axis)
        - matrix_3d[:, :, n] => n-th height for each XY plain (XY slice / slice normal to z-axis)
        """

        if plain == Plain.XY:
            return self.model.get_model_matrix()[:, :, n]
        elif plain == Plain.XZ:
            return self.model.get_model_matrix()[:, n, :]
        elif plain == Plain.YZ:
            return self.model.get_model_matrix()[n, :, :]
        else:
            raise AssertionError("Cannot slicing in not orthogonal plains")
