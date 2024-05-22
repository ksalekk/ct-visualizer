import numpy as np

from app.helpers.enums import Plain


class Model:
    """
    A class that stores basic data about 3d object which has been scanned with computed tomography methods.
    It stores "sub-models" that represents projection along single axis. Orthogonal plains (XY, XZ, YZ) are default
    creating during model initialization. However, it allows to storage projections along any axis and add them to model
    during runtime.

    Naming convention of model assumes that:
        - model is placed in right-handed XYZ space
        - patient is fixed in front of the observer (observer see XY plain)
        - X-axis runs from left to right in observer perspective
        - Y-axis runs from front to back in observer perspective
        - Z-axis runs from bottom to top in observer perspective
    This convention must be compatible with controller convention.

     Attributes
    ----------
        __matrix_3d
            voxel representation of the model
        __patient_metadata: dict
            provided by controller class; e.g. patient name, age, sex, ...
        __examination_metadata: dict
            provided by controller class; e.g. body part examined, comments, descriptions, ...
        __projections_models: dict
            (default XY, XZ, YZ; possible customizing)
        __xy_projection
        __xz_projection
        __yz_projection
    """

    def __init__(self):
        super(Model, self).__init__()

        self.__matrix_3d = None

        self.__patient_metadata = None
        self.__examination_metadata = None

        self.__xy_projection = ProjectionModel(plain=Plain.XY)
        self.__xz_projection = ProjectionModel(plain=Plain.XZ)
        self.__yz_projection = ProjectionModel(plain=Plain.YZ)

        self.__projections_models = {
            Plain.XY: self.__xy_projection,
            Plain.XZ: self.__xz_projection,
            Plain.YZ: self.__yz_projection
        }

    def set_model_matrix(self, matrix_3d: np.matrix):
        """Set model as a 3d numpy array"""
        x_size, y_size, z_size = matrix_3d.shape
        self.__matrix_3d = matrix_3d
        self.__xy_projection.set_shape(x_size, y_size, z_size)
        self.__xz_projection.set_shape(x_size, z_size, y_size)
        self.__yz_projection.set_shape(y_size, z_size, x_size)

    def get_model_matrix(self):
        """Return model as a 3d numpy array"""
        return self.__matrix_3d

    def add_new_projection(self, plain_name):
        """Add new projection (along new axis). In current app version is probably useless."""
        if plain_name in self.__projections_models.keys():
            raise ValueError(f"Projection {plain_name} is already existing.")
        else:
            self.__projections_models[plain_name] = ProjectionModel(plain=plain_name)
            return self.__projections_models[plain_name]

    def get_projection_model(self, plain):
        """Return specified projection model"""
        return self.__projections_models[plain]

    def set_patient_metadata(self, patient_metadata: dict):
        """Set patient metadata"""
        self.__patient_metadata = patient_metadata

    def set_examination_metadata(self, examination_metadata: dict):
        """Set patient metadata"""
        self.__examination_metadata = examination_metadata

    def get_patient_metadata(self):
        """Return patient all metadata"""
        return self.__patient_metadata

    def get_examination_metadata(self):
        """Return examination all metadata"""
        return self.__examination_metadata

    def get_all_projections_models(self):
        """Return all projections models"""
        return self.__projections_models.values()


class ProjectionModel:
    """A "sub-model" class that represents projection along single axis. It stores basic data about
    current displayed image and images series, along single axis. It assumes that all projection images
    has the same size (all slices of projection create cuboid in the 3D space). It not stores whole 3d model
    but only current chosen slice and metadata for both current slice and all slices in this projection model.

     Attributes
    ----------
        __plain
            plain of slices; for non-orthogonal plains it may be name characterizing rotated plain
            in reference to XY plain (e.g. {x_rot}_{y_rot}_{z_rot})
        __anatomical_plane:
            name of anatomical_plane that correspond projection plane (e.g. Axial, Coronal, Sagittal)
        __projection_orientation: dict
            specify image orientation in reference to patient orientation (e.g. {'image_up': patient_left, ...})
        __slices_count: dict
            number of all slices for this projection (along single axis)
        __current_slice_num
            number of current slice
        __current_slice_image
            current displayed/chosen image in this projection; represented by 2D array
        __slices_width
            images pixel width
        __slices_height
            image pixel width
        __slice_thickness
            slice thickness in mm
        __col_spacing
            space between 2 pixels in one row (between cols) in mm
        __row_spacing
            space between 2 pixels in one col (between rows) in mm
        __image_metadata
            basic metadata about projection model and current displayed image (e.g. slice number, size, ...)
        __roi_metadata
            metadata about current chosen ROI (e.g. area, mean pixel intensity, ...)
        prev_roi_pix_size
            last size of ROI (allows to skip area calculating when ROI size has been not changed)
    """

    def __init__(self, plain=None, anatomical_plane=None):
        self.__plain = plain
        self.__anatomical_plane = anatomical_plane
        self.__projection_orientation = {}

        self.__slices_count = 0
        self.__current_slice_num = 0
        self.__current_slice_image = None

        self.__slices_width = 0
        self.__slices_height = 0

        self.__slice_thickness = 0
        self.__col_spacing = 0
        self.__row_spacing = 0

        self.__image_metadata = {}
        self.__roi_metadata = {}

        self.prev_roi_pix_size = 0, 0

    def set_shape(self, width, height, depth):
        """Set width_height_depth shape of the projection model"""
        self.__slices_width = width
        self.__slices_height = height
        self.__slices_count = depth

    def set_spacings(self, col_spacing, row_spacing, thickness):
        """Set voxels spacings"""
        self.__col_spacing = col_spacing
        self.__row_spacing = row_spacing
        self.__slice_thickness = thickness

    def get_spacings(self):
        """Return pixel spacing as a tuple (between col, between row)"""
        return self.__col_spacing, self.__row_spacing

    def get_slices_thickness(self):
        """Return slices thickness"""
        return self.__slice_thickness

    def get_slices_count(self):
        """Return count of all slices in projection model"""
        return self.__slices_count

    def get_img_size(self):
        """Return size of projection slices as a tuple (width, height)"""
        return self.__slices_width, self.__slices_height

    def get_current_slice_img(self):
        """Return current extracted slice as a 2d numpy array"""
        return self.__current_slice_image

    def set_current_slice(self, img, n):
        """Extract n-th slice from projection model and set it as the current slice"""
        self.__current_slice_image = img
        self.__current_slice_num = n

    def set_img_metadata(self, img_metadata: dict):
        """Set image metadata as dict"""
        self.__image_metadata = img_metadata

    def update_img_metadata(self, metadata: dict):
        """Update and add new attributes to existing image metadata"""
        for k, v in metadata.items():
            self.__image_metadata[k] = v
        return self.__image_metadata

    def get_img_metadata(self):
        """Return image metadata dict"""
        return self.__image_metadata

    def set_roi_metadata(self, roi_metadata):
        """Set roi metadata as dict"""
        self.__roi_metadata = roi_metadata

    def update_roi_metadata(self, data: dict):
        """Update and add new attributes to existing roi metadata"""
        for k, v in data.items():
            self.__roi_metadata[k] = v
        return self.__roi_metadata

    def get_roi_metadata(self):
        """Return roi metadata dict"""
        return self.__roi_metadata

    def set_anatomical_plane(self, anatomical_plane):
        self.__anatomical_plane = anatomical_plane

    def get_anatomical_plane(self):
        return self.__anatomical_plane

    def set_projection_orientation(self, orientation):
        self.__projection_orientation = orientation

    def get_projection_orientation(self):
        return self.__projection_orientation
