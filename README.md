# Computed Tomography Visualizer

### General
Python app that allows to visualize CT scan data in three anatomical planes: sagittal, coronal, and axial. Application provide an intuitive interface for exploring CT scan slices. The data source is directory with .dcm files (DICOM is a technical standard that specify storage and transmission of medical data, including .dcm format files).

### Functions
- User load CT serie by select the folder with CT data volumin (.dicom files that store CT slices); loading data lasts a while.
- After loading the data user can choose specified plane with tab bar (Axial, Coronal, Sagittal) and then navigate between slices of selected plane (slider). 
- Both histogram and ROI modes can be displayed/hidden with button in toolbar (global for all planes).
- Data about current seleced plane and slice is showed in corners of widget which display image.
- ROI mode allows to check basic statistics (mean and standard deviation for pixel values; real area in mm^2) of the selected ROI.

### Requirementes 
App use packages: **numpy, PySide6, PyQtGraph, pydicom** (all requirements are in reguirements.txt file).

App GUI is based on PySide6 (general widgets structure) and PyQtGraph (images displaying). Buisness logic is realised with numpy package (managing slices, computing) and pydicom (extract specified data from .dicom files).

Entrypoint of the app is main.py file which starts the app and display main window of the app.

***

### Example CT data
Example CT public data can be downloaded from the page: https://3dicomviewer.com/dicom-library/ (app demo is based on "CT Scan of COVID-19 Lung" data).

