import struct
from os.path import abspath, expanduser, splitext, basename, join, split
import csv
import glob
from collections import OrderedDict
import pandas as pd
import numpy as np

ASD_VERSIONS = ['ASD', 'asd', 'as6', 'as7', 'as8']
ASD_HAS_REF = {'ASD': False, 'asd': False, 'as6': True, 'as7': True,
               'as8': True}
ASD_DATA_TYPES = OrderedDict([("RAW_TYPE", "tgt_count"),
                              ("REF_TYPE", "tgt_reflect"),
                              ("RAD_TYPE", "tgt_radiance"),
                              ("NOUNITS_TYPE", None),
                              ("IRRAD_TYPE", "tgt_irradiance"),
                              ("QI_TYPE", None),
                              ("TRANS_TYPE", None),
                              ("UNKNOWN_TYPE", None),
                              ("ABS_TYPE", None)])


def read_txt_asd(filepath, read_data=True, read_metadata=True, verbose=False):
    """
    Read asd file for data and metadata

    Return
    ------
    2-tuple of (pd.DataFrame, OrderedDict) for data, metadata
    """
    data = None
    metadata = None
    if read_metadata:
        metadata = OrderedDict()

    with open(abspath(expanduser(filepath)), 'rU') as f:
        if verbose:
            print('reading {}'.format(filepath))

        # Get name without .txt
        metadata['file'] = splitext(f.name)[0]
        metadata['instrument_type'] = 'ASD'
        version = "ASD"

        # Filter out null bytes
        f = (line.replace('\0', '') for line in f)

        # Use csv reader to read the data file
        reader = csv.reader(f, delimiter='\t')

        # Skip first row which is blank
        next(reader)

        # Ensure this file is valid asd text data produced by ViewSpec
        assert("Text conversion of header file" in next(reader)[0])
        assert("-----" in next(reader)[0])

        # Primary description created during spectrum save.
        primary_desc = next(reader)

        # Instrument number of the spectrometer
        intrument_no = next(reader)[0].split(' ')[-1]

        # Program and file version
        version_info = next(reader)[0]
        assert("New ASD spectrum file:" in version_info)
        version_info = version_info.split(' ')
        program_ver = version_info[7]
        file_ver = version_info[-1]

        # Datetime spectrum was saved.
        datetime_saved = next(reader)[0]

        # Integration time of the spectrum
        # Note: some file version have "VNIR integration time" and other may
        # have !Integration time" so don't include "i" in assert.
        integration_time = next(reader)[0]
        assert("ntegration time" in integration_time)
        integration_time = integration_time.split(' ')[-1]

        # Read rest of header into a list until the spectrum data
        # There may be some  variation in this section between data files.
        # Check the size of the header list and use program, file version to
        # pick out needed informaiton
        header = []
        for r, row in enumerate(reader):
            header += row
            if len(row) == 2 and "Wavelength" in row:
                break

        # GPS TODO: how to find these GPS information in header list?
        # gps_latitude = next(reader)[0]
        # gps_longitude = next(reader)[0]
        # gps_altitude = next(reader)[0]
        # gps_datetime = next(reader)[0]

        # Read spectrum type TODO: investigate how to detect type from text
        spectrum_type = ASD_DATA_TYPES['RAW_TYPE']

        if read_data:
            # read data
            tgt_column = ASD_DATA_TYPES['RAW_TYPE']
            ref_column = tgt_column.replace('tgt', 'ref')

            # data to DataFrame
            waves = []
            spectrum = []
            for row in reader:
                waves += [int(row[0])]
                spectrum += [float(row[1].replace(" ", ""))]
            # reference = np.full(len(spectrum), np.nan)
            data = pd.DataFrame({tgt_column: spectrum}, index=waves)
            # data = pd.Series(spectrum, name=tgt_column, index=waves)
            data.index.name = 'wavelength'
            # data.dropna(axis=1, how='all')

        if read_metadata:
            # read splice wavelength
            splice1 = None
            splice2 = None
            # gps info
            gps_true_heading = None
            gps_speed = None
            gps_latitude = None
            gps_longitude = None
            gps_altitude = None
            gps_flags = None
            gps_hardware_mode = None
            gps_timestamp = None
            gps_flags2 = None
            gps_satellites = None
            gps_filler = None
            # metadata
            metadata['integration_time'] = integration_time
            metadata['measurement_type'] = spectrum_type
            metadata['gps_time_tgt'] = gps_timestamp
            metadata['gps_time_ref'] = None
            metadata['wavelength_range'] = (waves[0], waves[-1])
            # metadata['splice'] = (splice1, splice2)
            # metadata['resolution'] = wavestep
    return data, metadata
