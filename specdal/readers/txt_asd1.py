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


def read_txt_asd1(filepath, read_data=True, read_metadata=True, verbose=False):
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

        primary_desc = next(reader)
        intrument_no = next(reader)[0]
        program_version = next(reader)[0]
        datetime_saved = next(reader)[0]
        integration_time = next(reader)[0]
        # read wavelength info
        wave_config_one = next(reader)[0]
        assert("Channel 1 wavelength" in wave_config_one)
        wave_config_one = wave_config_one.split(' ')
        wavestart = wave_config_one[4]
        wavestep = wave_config_one[8]
        no_samples = next(reader)[0]
        wave_config_two = next(reader)[0]
        assert("xmin =" in wave_config_two)
        wavestop = wave_config_two.split(' ')[-1]
        y_axis_config = next(reader)[0]
        assert("ymin=" in y_axis_config)
        bit_length = next(reader)[0]
        assert("The instrument digitizes spectral values to" in bit_length)
        # Dark current
        dark_current_status_one = next(reader)[0]
        dark_current_status_two = next(reader)[0]
        dcc_value = next(reader)[0]
        white_reference = next(reader)[0]
        input_optics = next(reader)[0]
        data_type = next(reader)[0]
        gps_latitude = next(reader)[0]
        gps_longitude = next(reader)[0]
        gps_altitude = next(reader)[0]
        gps_datetime = next(reader)[0]

        # Read secondary description until spectrum data
        secondary_desc = []
        for r, row in enumerate(reader):
            secondary_desc += row
            if len(row) == 2 and "Wavelength" in row:
                break

        # read spectrum type
        # spectrum_type_index = struct.unpack('B', binconts[186:(186 + 1)])[0]
        # spectrum_type = list(ASD_DATA_TYPES.keys())[spectrum_type_index]
        spectrum_type = 'tgt_count'

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
            # integration time
            integration_time = integration_time.split(' ')[-1]
            # gps info
            gps_true_heading = None
            gps_speed = None
            gps_latitude = gps_latitude.split(' ')[-1]
            gps_longitude = gps_longitude.split(' ')[-1]
            gps_altitude = gps_altitude.split(' ')[-1]
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
            metadata['wavelength_range'] = (wavestart, wavestop)
            # metadata['splice'] = (splice1, splice2)
            # metadata['resolution'] = wavestep
    return data, metadata
