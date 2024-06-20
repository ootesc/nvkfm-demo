import streamlit as st
import os
import io
import tempfile
from datetime import datetime

import pydicom
import numpy as np
import pandas as pd
from pylinac import WinstonLutz

st.title('WinstonLutz demo')

# Upload files
dicom_files = st.file_uploader("Select DICOMs to be analysed", accept_multiple_files=True)
dicom_files.sort(key=lambda x: x.name)

# Read files as Dicom
dicom_datasets = []
for i in dicom_files:
    dicom_datasets.append(pydicom.read_file(i))

# Show how many images are uploaded
st.write(f"{len(dicom_datasets)} images uploaded")   

# Stop streamlit when no files are uploaded
if len(dicom_datasets) == 0:
    st.stop()

# Add gantry angles
st.divider()
option = st.selectbox(
    'Select setup option',
    ('Do not add angles', 'Elekta 4mm with kV Flexmaps Stored Beam'))

bb_size_mm = 0
if option == 'Do not add angles':
    pass
elif option == 'Elekta 4mm with kV Flexmaps Stored Beam':
    if len(dicom_datasets) != 8:
        st.warning('Please upload 8 images!')
        st.stop()
    else:
        dicom_datasets[0].GantryAngle = 180.0
        dicom_datasets[0].BeamLimitingDeviceAngle = 270.0
        dicom_datasets[1].GantryAngle = 180.0
        dicom_datasets[1].BeamLimitingDeviceAngle = 90.0
        dicom_datasets[2].GantryAngle = 270.0
        dicom_datasets[2].BeamLimitingDeviceAngle = 90.0
        dicom_datasets[3].GantryAngle = 270.0
        dicom_datasets[3].BeamLimitingDeviceAngle = 270.0
        dicom_datasets[4].GantryAngle = 0.0
        dicom_datasets[4].BeamLimitingDeviceAngle = 270.0
        dicom_datasets[5].GantryAngle = 0.0
        dicom_datasets[5].BeamLimitingDeviceAngle = 90.0
        dicom_datasets[6].GantryAngle = 90.0
        dicom_datasets[6].BeamLimitingDeviceAngle = 90.0
        dicom_datasets[7].GantryAngle = 90.0
        dicom_datasets[7].BeamLimitingDeviceAngle = 270.0
        bb_size_mm = 4

# TODO other setups
else:
    pass

# Overview
st.write('Overview DICOMs:')

# Create overview table
columns=['filename', 'date', 'gantryangle', 'collimatorangle']
overview_dataframe = pd.DataFrame(columns=columns)
for index, image in enumerate(dicom_datasets):
    overview_year = int(dicom_datasets[index].StudyDate[0:4])
    overview_month = int(dicom_datasets[index].StudyDate[4:6])
    overview_day = int(dicom_datasets[index].StudyDate[6:8])
    overview_hour = int(dicom_datasets[index].StudyTime[0:2])
    overview_minute = int(dicom_datasets[index].StudyTime[2:4])
    overview_second = int(dicom_datasets[index].StudyTime[4:6])
    overview_datetime = datetime(overview_year, overview_month, overview_day, overview_hour, overview_minute, overview_second)

    overview_filename = str(dicom_files[index].name)
    overview_gantryangle = str(dicom_datasets[index].GantryAngle)
    overview_collimatorangle = str(dicom_datasets[index].BeamLimitingDeviceAngle)
    overview_dataframe.loc[len(overview_dataframe)] = [overview_filename, overview_datetime, overview_gantryangle, overview_collimatorangle]

st.dataframe(overview_dataframe)

# Save DICOMs in temp folder and analyze with pylinac WinstonLutz
wl = None
with tempfile.TemporaryDirectory() as tmp_dir_path:   
    for index, image in enumerate(dicom_datasets):
        tmp_file_path = tmp_dir_path + "/" + str(image.SOPInstanceUID) + ".dcm"
        pydicom.filewriter.write_file(tmp_file_path, image) 

    # Analyze DICOMs
    wl = pylinac.WinstonLutz(tmp_dir_path) 

st.divider()

# Analyze
wl.analyze(bb_size_mm=bb_size_mm)

# Default analyse rapport
st.header('Default analyse rapport') 
st.code(wl.results())

# 
wl_results = wl.results_data()
