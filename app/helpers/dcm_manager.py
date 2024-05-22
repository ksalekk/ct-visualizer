import glob
import os

import numpy as np
import pydicom


def get_dcm_from_path(src_path: str | list[str]):
    """Get dcm files source (directory path/file path/list of files paths)
    and return dcm data set / list of data sets"""

    if type(src_path) is list:
        if len(src_path) == 1:
            return pydicom.dcmread(src_path[0])
        else:
            return [pydicom.dcmread(f) for f in src_path]
    elif os.path.isdir(src_path):
        files = glob.glob(src_path + "/*.dcm", recursive=False)
        dcm_files = [pydicom.dcmread(f) for f in files]
        return dcm_files
    elif os.path.isfile(src_path):
        return pydicom.dcmread(src_path)
    else:
        raise ValueError(f"Expected a directory or files list, but {type(src_path)} has been provided")


def extract_ct_from_dcm(dcm_files):
    """Get list of dcm_files and extract CT dicom files. Return list of dcm_files sorted ascending by SliceLocation"""
    ct_slices = []
    for dcm_f in dcm_files:
        if hasattr(dcm_f, 'SliceLocation') or (hasattr(dcm_f, 'SliceThickness') and dcm_f.SliceThickness != 0):
            ct_slices.append(dcm_f)
    return sorted(ct_slices, key=lambda dcm_f: dcm_f.SliceLocation)


def get_ct_model_as_matrix(dcm_files: list[pydicom.FileDataset], rot_k=0):
    """Get list CT dcm files and create 3d matrix based on it. CT images are located in XY plane and along Z-axis.
    rot_k parameter allows to rotate CT images by rot_k*90 degrees (counterclockwise)."""

    z_size = len(dcm_files)
    x_size, y_size = dcm_files[z_size // 2].pixel_array.shape
    matrix_3d = np.zeros([x_size, y_size, z_size])

    if rot_k % 4 != 0:
        for z, ct_s in enumerate(dcm_files):
            matrix_3d[:, :, -z] = np.rot90(ct_s.pixel_array, k=rot_k)
    else:
        for z, ct_s in enumerate(dcm_files):
            matrix_3d[:, :, -z] = ct_s.pixel_array

    return matrix_3d


def get_ct_thickness(dcm_dataset):
    """Return SliceThickness data element from specified DICOM data set"""
    return dcm_dataset.get('SliceThickness')


def get_ct_pixel_spacing(dcm_dataset):
    """Return PixelSpacing data element ((row_spacing, col_spacing) tuple) from specified DICOM data set"""
    row_spacing, col_spacing = dcm_dataset.get('PixelSpacing')
    return row_spacing, col_spacing


def get_image_orientation_patient(dcm_dataset):
    """Return PixelSpacing data element from specified DICOM data set"""
    return dcm_dataset.get('ImageOrientationPatient')


def get_patient_data(dcm_dataset):
    """Return basic patient data elements from specified DICOM data set.
    Return dict of PatientID, PatientName, PatientAge, PatientSex data elements."""
    patient_id = dcm_dataset.get('PatientID')
    name = dcm_dataset.get('PatientName')
    age = dcm_dataset.get('PatientAge')
    sex = dcm_dataset.get('PatientSex')

    patient_data = {
        "Patient ID": patient_id,
        "Name": str(name).upper(),
        "Age": str(age),
        "Sex": str(sex).capitalize()
    }

    for key, value in patient_data.items():
        if not value:
            patient_data[key] = "unknown"

    return patient_data


def get_examination_data(dcm_dataset):
    """Return basic examination data elements from specified DICOM data set.
    Return dict of StudyID, Date, BodyPartExamined data elements."""
    study_id = dcm_dataset.get('StudyID')
    date = dcm_dataset.get('Date')
    body_part = dcm_dataset.get('BodyPartExamined')

    examination_data = {
        "Study ID": str(study_id),
        "Date": str(date),
        "Body Part Examined": str(body_part).capitalize()
    }

    for key, value in examination_data.items():
        if not value:
            examination_data[key] = "unknown"

    return examination_data
