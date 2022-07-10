import argparse, calendar, collections, datetime, csv, gzip, json, math, pkgutil, re, os, sys, enum
import _root
import _folder, _helper

has_cv2 = False
if pkgutil.find_loader('cv2'):
    # TODO: get opencv working with pyinstaller
    try:
        import cv2
        has_cv2 = True
    except ImportError as error:
        pass



SUBSAMPLE = 4
TILE_SIZE = 1024
IMAGE_HEIGHT = 32

DEFAULT_RANGE_MAGNITUDE = 8

FILL_STEP = 'step'
FILL_LINEAR = 'linear'
FILL_OPTIONS = [FILL_STEP, FILL_LINEAR]



# Check if range arg was given in the correct format and extract indices
def parseRange(what, rng):
    groups = re.match(r'(\d*)(-?)(\d*)', rng).groups()

    if groups[0] == '' and groups[1] == '' and groups[2] == '':
        _helper.errorExit('Argument for ' + what + ' range has invalid form. Valid forms include: "1" or "1-3" or "-3" or "1-"')
    elif groups[0] != '' and groups[1] == '' and groups[2] == '':
        start = int(groups[0])
        end = start
    else:
        start = int(groups[0]) if groups[0] != '' else None
        end = int(groups[2]) if groups[2] != '' else None

    if start is not None and end is not None:
        if end < start:
            _helper.errorExit('End ' + what + ' index must be >= than start ' + what + ' index')

    return start, end

def strRange(what, start, end):
    if start == end:
        return '__' + what + '_' + str(start)
    else:
        return '__' + what + '_' + (str(start) if start else '') + 'to' + (str(end) if end else '')

def rangesample(sample, slen):
    ret = [None] * slen

    for s in sample:
        for ii in range(slen):
            if s[ii] == None:
                pass
            elif type(s[ii]) == type(''):
                if ret[ii] == None:
                    ret[ii] = s[ii]
            else: #number
                if ret[ii] == None:
                    ret[ii] = (s[ii], s[ii])
                else:
                    ret[ii] = (min(s[ii], ret[ii][0]),  max(s[ii], ret[ii][1]))

    return ret

def write_startfile(f, ss, fn):
    f.write('{')
    f.write('"meta":{"subsample":%d,"file":[\"%s\"]},' % (ss, fn))
    f.write('"data":[')

def write_sample(f, smp, prev, slen):
    if prev:
        f.write(',')

    f.write('[' + ','.join([('null' if s == None else ('"' + s + '"' if type(s) == type('') else ('[%0.3f,%0.3f]' % s))) for s in smp]) + ']')

def write_endfile(f):
    f.write(']')
    f.write('}')

class InputFormat(enum.Enum):
    WITH_TIMESTAMP_NO_HEADER = enum.auto(),
    WITH_TIMESTAMP_WITH_HEADER = enum.auto(),
    NO_TIMESTAMP_NO_HEADER = enum.auto(),
    NO_TIMESTAMP_WITH_HEADER = enum.auto(),
    NOT_SUPPORTED = enum.auto()

def data_type_found(name):
    SUPPORT_DATA_TYPES = ["Accelerometer", "Magnetometer", "Temperature", "Gyroscope"]
    for support_type in SUPPORT_DATA_TYPES:
        if support_type in name:
            return True
    return False

def check_input_format(firstrow):
    tokens = firstrow
    first_col = tokens[0]
    second_col = tokens[1] if len(tokens) > 1 else None
    if 'Timestamp' in first_col:
        if data_type_found(second_col) and len(tokens) <= 4:
            return InputFormat.WITH_TIMESTAMP_WITH_HEADER
        else:
            return InputFormat.NOT_SUPPORTED
    elif 'Timestamp' not in first_col and data_type_found(first_col):
        if len(tokens) <= 3:
            return InputFormat.NO_TIMESTAMP_WITH_HEADER
        else:
            return InputFormat.NOT_SUPPORTED
    elif is_float(first_col) or len(tokens) == 1 or len(first_col) == 0:
        # no timestamp column, no header
        if len(tokens) > 3:
            return InputFormat.NOT_SUPPORTED
        else:
            return InputFormat.NO_TIMESTAMP_NO_HEADER
    else:
        # with timestamp column, no header
        if len(tokens) > 4:
            return InputFormat.NOT_SUPPORTED
        else:
            return InputFormat.WITH_TIMESTAMP_NO_HEADER

def is_float(str_val):
    try:
        float(str_val)
        return True
    except ValueError:
        return False

def main(filenames, *,
         name=None, labelfilenames=None, zoom=None,
         range_min=None, range_max=DEFAULT_RANGE_MAGNITUDE,
         custom_fields=None, custom_start=None, custom_sample_rate=None,
         custom_video_frame_rate=None,
         time_field=None, fill=None, fill_limit=None,
         sample=None, day=None):

    if len(filenames) > 1 and not name:
        _helper.errorExit('Must specify a dataset --name when importing multiple files')

    if range_min == None:
        range_min = -range_max

    if range_max <= range_min:
        _helper.errorExit('--range-min must be less than --range-max')

    if (custom_start is not None and custom_sample_rate is None) or (custom_start is None and custom_sample_rate is not None):
        _helper.errorExit('--custom-start and --custom-sample-rate must be used together')

    if custom_sample_rate is not None and custom_sample_rate <= 0:
        _helper.errorExit('--custom-sample-rate must be positive')

    if custom_start is not None:
        custom_start_ms = _helper.timeConvertStringToMillisecond(custom_start, _helper.DATE_FORMAT_YMD)
    else:
        custom_start_ms = None

    if sample is not None and day is not None:
        _helper.errorExit('Can only provide one of --sample and --day')

    if fill is not None:
        if fill not in FILL_OPTIONS:
            _helper.errorExit('--fill must be one of %s' % (','.join(FILL_OPTIONS)))
        if time_field is None:
            _helper.errorExit('--fill only works with --time-field')
    if fill_limit is not None and fill is None:
        _helper.errorExit('--fill-limit only works with --fill')

    start_sample, end_sample = None, None
    if sample is not None:
        start_sample, end_sample = parseRange('sample', sample)

    start_day, end_day = None, None
    if day is not None:
        start_day, end_day = parseRange('day', day)



    # load labels
    if not labelfilenames:
        labelfilenames = [
            _folder.file_abspath('common', 'labels_test.csv'),
            _folder.file_abspath('common', 'labels_unknown.csv')
        ]

    labels = []
    labels_names = set()

    for labelfile in labelfilenames:
        print('Reading labels from %s...' % labelfile)

        with open(labelfile, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)

            if set(reader.fieldnames) != set(['label', 'red', 'green', 'blue']):
                _helper.errorExit('Incorrect label csv headers')

            for row in reader:
                label_name = row['label'].strip()
                rr = float(row['red'].strip())
                gg = float(row['green'].strip())
                bb = float(row['blue'].strip())

                if re.search('[^\w\- ]', label_name, re.ASCII):
                    _helper.errorExit('Only alphanumeric, underscore, dash, and space allowed in label names: ' + label_name)
                if label_name in labels_names:
                    _helper.errorExit('Duplicate label: ' + label_name)

                labels.append((label_name, rr, gg, bb))
                labels_names.add(label_name)



    # process arguments
    sensor_names = []
    for filename in filenames:
        sensor_names.append(_helper.makeIdFromFilename(filename))
    if len(sensor_names) != len(set(sensor_names)):
        _helper.errorExit('Duplicate sensor names')

    if name:
        if not _helper.checkId(name, False):
            _helper.errorExit('Only alphanumeric and underscore allowed in dataset names')
        dataset = name
    else:
        dataset = sensor_names[0]

    if start_sample is not None or end_sample is not None:
        dataset = dataset + strRange('sample', start_sample, end_sample)
    if start_day is not None or end_day is not None:
        dataset = dataset + strRange('day', start_day, end_day)

    out_folder = _helper.datasetDir(dataset)
    tile_folder = _helper.datasetTileDir(dataset)

    if os.path.exists(out_folder):
        _helper.errorExit('Please remove output folder ' + out_folder)

    print('Using output folder ' + out_folder)

    _helper.ensureDirExists(out_folder, False)
    _helper.ensureDirExists(tile_folder, False)



    # read in data
    print('reading header...')

    if not has_cv2:
        _helper.warning('Unable to load OpenCV, video import will be unavailable')



    # open files
    SENSOR_TYPE_DATA = 'data'
    SENSOR_TYPE_IMAGE = 'image'

    sensorfiles = []
    for filename in filenames:
        if filename.endswith('.csv.gz') or filename.endswith('.csv'):
            if filename.endswith('.csv.gz'):
                use_open = gzip.open
            else:
                use_open = open

            sensorfiles.append((SENSOR_TYPE_DATA, use_open(filename, 'rt')))

        elif filename.endswith('.mp4') or filename.endswith('.mov'):
            if not has_cv2:
                _helper.errorExit('Python OpenCV must be installed to import video')

            videofile = cv2.VideoCapture(filename)

            # check frame rate here for early exit
            if custom_video_frame_rate == None:
                frame_rate = videofile.get(cv2.CAP_PROP_FPS)
                if frame_rate < 0.001:
                    _helper.errorExit('Video has unusable frame rate: ' + str(frame_rate))

            sensorfiles.append((SENSOR_TYPE_IMAGE, videofile))
        else:
            _helper.errorExit('Unrecognized sensor file extension: ' + filename)

    if custom_video_frame_rate != None:
        print('Using custom video frame rate of %f.' % custom_video_frame_rate)


    # read headers
    files_start_ms = []
    dataset_rate = None

    for filename, (sensortype, sensorfile) in zip(filenames, sensorfiles):
        if sensortype == SENSOR_TYPE_DATA:
            if custom_sample_rate is None and custom_start_ms is None:
                header_rate, header_start_ms = _helper.processActigraphHeader(sensorfile)
            else:
                header_rate, header_start_ms = custom_sample_rate, custom_start_ms

            if dataset_rate == None:
                dataset_rate = int(header_rate)
            elif dataset_rate != int(header_rate):
                _helper.errorExit('Multiple sample rates found')

            files_start_ms.append(header_start_ms)

        elif sensortype == SENSOR_TYPE_IMAGE:
            files_start_ms.append(None) # TODO: figure out the video start time later

    # checking if the video is imported by itself
    if len(filenames) == 1:
        if (filenames[0].endswith(".mp4") or filenames[0].endswith(".mov")):
            _helper.errorExit('Video must be imported with a .csv file')

    if dataset_rate == None:
        _helper.errorExit('Unable to determine dataset sample rate')

    if dataset_rate > 250:
        _helper.errorExit('Dataset sample rate too high')



    # start videos at start of dataset
    # TODO: fix this
    files_start_ms_min = min(filter(lambda x: x != None, files_start_ms))
    files_start_ms = [(x if x != None else files_start_ms_min) for x in files_start_ms]



    # determine sample range
    dataset_start_ms = min(files_start_ms)
    dataset_start_date = _helper.timeConvertMillisecondToDateTime(dataset_start_ms).date()



    if start_sample is not None or end_sample is not None:
        pass

    if start_day is not None or end_day is not None:
        if start_day is not None:
            output_min_ms = 1000 * calendar.timegm((dataset_start_date + datetime.timedelta(days=(start_day - 1))).timetuple())
            start_sample = _helper.timeConvertMillisecondToSample(max(output_min_ms, dataset_start_ms), dataset_start_ms, dataset_rate, _helper.CONVERT_RELAXED)
        else:
            start_sample = None

        if end_day is not None:
            output_max_ms = 1000 * calendar.timegm((dataset_start_date + datetime.timedelta(days=(end_day))).timetuple())
            end_sample = _helper.timeConvertMillisecondToSample(output_max_ms, dataset_start_ms, dataset_rate, _helper.CONVERT_RELAXED)
        else:
            end_sample = None



    # determine starting day index
    start_day_index = 1
    if start_sample:
        start_day_index = 1 + (_helper.timeConvertMillisecondToDateTime(_helper.timeConvertSampleToMillisecond(start_sample, dataset_start_ms, dataset_rate, _helper.CONVERT_PERMISSIVE)).date() - dataset_start_date).days



    # print header summary
    if len(filenames) > 1:
        for filename, sensorname, file_start_ms in zip(filenames, sensor_names, files_start_ms):
            print('file start:   ', _helper.timeConvertMillisecondToString(file_start_ms), sensorname, filename)
    print('input start:  ', _helper.timeConvertMillisecondToString(dataset_start_ms), dataset)

    output_start_ms = dataset_start_ms
    if start_sample != None:
        output_start_ms = _helper.timeConvertSampleToMillisecond(start_sample, dataset_start_ms, dataset_rate, _helper.CONVERT_PERMISSIVE)

    # check dataset starts on a time that is a sample
    _helper.timeConvertMillisecondToSample(dataset_start_ms, 0, dataset_rate, _helper.CONVERT_STRICT, 'Dataset input does not start on a sample time.')
    _helper.timeConvertMillisecondToSample(output_start_ms, 0, dataset_rate, _helper.CONVERT_STRICT, 'Dataset output does not start on a sample time.')



    # read data
    sample_data = []
    sample_len = 0
    sample_data_element_offset = 0

    min_smp = 1e100
    max_smp = -1e100

    sensor_channel_names = {}
    all_channel_names = set()

    sensor_range_spans = []
    sensor_range_units = []

    for fileindex, (filename, sensor_name, file_start_ms, (sensortype, sensorfile)) in enumerate(zip(filenames, sensor_names, files_start_ms, sensorfiles)):
        print('reading ' + filename + '...')

        if sensortype == SENSOR_TYPE_DATA:
            # Checks if csv header is absent and adds the header if needed
            csvstartpos = sensorfile.tell()
            firstrow = csv.DictReader([next(sensorfile)]).fieldnames # uses csv reader to parse first row
            sensorfile.seek(csvstartpos)

            if custom_fields is None:
                DEFAULT_CHANNEL_NAMES = ['X', 'Y', 'Z']

                input_format = check_input_format(firstrow)
                n_of_fields = len(firstrow)
                if input_format == InputFormat.WITH_TIMESTAMP_WITH_HEADER:
                    field_names = firstrow[1:]
                    reader_field_names = firstrow
                    channel_names = DEFAULT_CHANNEL_NAMES[:(n_of_fields-1)]
                    if time_field != 'Timestamp':
                        _helper.warning('input file has Timestamp field, but it will be ignored')
                    reader = csv.DictReader(sensorfile, fieldnames=reader_field_names)
                    next(reader)
                elif input_format == InputFormat.WITH_TIMESTAMP_NO_HEADER:
                    field_names = DEFAULT_CHANNEL_NAMES[:(n_of_fields - 1)]
                    reader_field_names = ['Timestamp'] + field_names
                    channel_names = DEFAULT_CHANNEL_NAMES[:(n_of_fields-1)]
                    if time_field != 'Timestamp':
                        _helper.warning('input file has Timestamp field, but it will be ignored')
                    _helper.warning('input file missing field names, using ' + ','.join(reader_field_names))
                    reader = csv.DictReader(sensorfile, fieldnames=reader_field_names)
                elif input_format == InputFormat.NO_TIMESTAMP_WITH_HEADER:
                    field_names = firstrow
                    reader_field_names = firstrow
                    channel_names = DEFAULT_CHANNEL_NAMES[:n_of_fields]
                    reader = csv.DictReader(sensorfile, fieldnames=reader_field_names)
                    next(reader)
                elif input_format == InputFormat.NO_TIMESTAMP_NO_HEADER:
                    field_names = DEFAULT_CHANNEL_NAMES[:n_of_fields]
                    reader_field_names = field_names
                    channel_names = DEFAULT_CHANNEL_NAMES[:n_of_fields]
                    _helper.warning('input file missing field names, using ' + ','.join(reader_field_names))
                    reader = csv.DictReader(sensorfile, fieldnames=reader_field_names)
                else:
                    _helper.errorExit('input file format is not supported')

            else:
                reader = csv.DictReader(sensorfile)
                field_names = custom_fields
                reader_field_names = reader.fieldnames
                channel_names = custom_fields

            # remember channel names
            sensor_channel_names[sensor_name] = channel_names
            for channel_name in channel_names:
                all_channel_names.add(channel_name)

            # guess sensor units
            # TODO: improve this
            if 'Accelerometer X' in reader_field_names:
                sensor_unit = 'g'
            else:
                _helper.warning('input file has unknown sensor unit')
                sensor_unit = ''

            # process rows
            reader_sample_index = 0

            sample_offset = _helper.timeConvertMillisecondToSample(file_start_ms, dataset_start_ms, dataset_rate, _helper.CONVERT_RELAXED)
            if start_sample != None:
                sample_offset -= start_sample

            last_data_sample = None
            last_data_sample_index = None

            sensor_min_smp = 1e100
            sensor_max_smp = -1e100
            for row in reader:
                if time_field is not None:
                    time_field_str = row[time_field]
                    time_field_ms = _helper.timeConvertStringToMillisecond(time_field_str, _helper.DATE_FORMAT_YMD)
                    time_field_sample = _helper.timeConvertMillisecondToSample(time_field_ms, dataset_start_ms, dataset_rate, _helper.CONVERT_STRICT)

                    if time_field_sample < reader_sample_index:
                        _helper.errorExit('Overlapping sample time: ' + time_field_str)

                    reader_sample_index = time_field_sample

                data_sample_index = reader_sample_index + sample_offset
                reader_sample_index += 1

                if data_sample_index < 0:
                    continue
                if end_sample != None and data_sample_index >= end_sample - (start_sample if start_sample != None else 0):
                    break

                smp = []
                for field_name in field_names:
                    s = row[field_name]
                    if s == '':
                        smp.append(None)
                    else:
                        s = float(s)
                        smp.append(s)

                        min_smp = min(min_smp, s)
                        max_smp = max(max_smp, s)
                        sensor_min_smp = min(sensor_min_smp, s)
                        sensor_max_smp = max(sensor_max_smp, s)

                while data_sample_index >= len(sample_data):
                    sample_data.append([])

                for ei, elem in enumerate(smp):
                    elem_index = ei + sample_data_element_offset

                    # fill gaps
                    if fill is not None and last_data_sample_index is not None:
                        fill_gap = True

                        if fill_limit is not None:
                            gap_sta = _helper.timeConvertSampleToMillisecond(last_data_sample_index, dataset_start_ms, dataset_rate, _helper.CONVERT_PERMISSIVE)
                            gap_end = _helper.timeConvertSampleToMillisecond(data_sample_index, dataset_start_ms, dataset_rate, _helper.CONVERT_PERMISSIVE)
                            gap_dur = (gap_end - gap_sta) / 1000
                            if gap_dur > fill_limit:
                                fill_gap = False

                        if fill_gap:
                            fill_sample_index = last_data_sample_index + 1
                            while fill_sample_index != data_sample_index:
                                while elem_index >= len(sample_data[fill_sample_index]):
                                    sample_data[fill_sample_index].append(None)

                                if fill == FILL_STEP:
                                    sample_data[fill_sample_index][elem_index] = last_data_sample[ei]
                                else: # FILL_LINEAR
                                    t = (fill_sample_index - last_data_sample_index) / (data_sample_index - last_data_sample_index)
                                    sample_data[fill_sample_index][elem_index] = (1 - t) * last_data_sample[ei] + t * smp[ei]

                                fill_sample_index += 1

                    while elem_index >= len(sample_data[data_sample_index]):
                        sample_data[data_sample_index].append(None)
                    sample_data[data_sample_index][elem_index] = elem
                    sample_len = max(sample_len, elem_index + 1)

                last_data_sample = smp
                last_data_sample_index = data_sample_index

                if reader_sample_index % (60 * 60 * dataset_rate) == 0:
                    print('read %d hours...' % (reader_sample_index / (60 * 60 * dataset_rate)))

            if sensor_min_smp < range_min or range_max < sensor_max_smp:
                _helper.warning('%s sample exceeds dataset range; sample min/max is: %d/%d' % (sensor_name, sensor_min_smp, sensor_max_smp))


            # Range for each sensor
            sensor_range_spans.append((sensor_min_smp, sensor_max_smp))
            sensor_range_units.append(sensor_unit)

            sample_data_element_offset += len(channel_names)

        elif sensortype == SENSOR_TYPE_IMAGE:
            if custom_video_frame_rate == None:
                frame_rate = sensorfile.get(cv2.CAP_PROP_FPS)
            else:
                frame_rate = custom_video_frame_rate

            frame_count = 0

            sensor_channel_names[sensor_name] = ['image']
            all_channel_names.add('image')

            sensor_range_spans.append(None)
            sensor_range_units.append(None)

            while True:
                success, image = sensorfile.read()

                if success:
                    image_id = 'image_%010d' % frame_count

                    image_filename = _helper.imageFilename(dataset, sensor_name, image_id)
                    _helper.ensureDirExists(image_filename, True)

                    image = cv2.resize(image, (int(IMAGE_HEIGHT * image.shape[1] / image.shape[0]), IMAGE_HEIGHT), interpolation=cv2.INTER_AREA)
                    cv2.imwrite(image_filename, image)

                    # TODO: account for sample offset!!
                    frame_ms = int(1.0 / frame_rate * frame_count * 1000) + file_start_ms
                    data_sample_index = _helper.timeConvertMillisecondToSample(frame_ms, dataset_start_ms, dataset_rate, _helper.CONVERT_PERMISSIVE)

                    while data_sample_index >= len(sample_data):
                        sample_data.append([])

                    elem_index = sample_data_element_offset
                    while elem_index >= len(sample_data[data_sample_index]):
                        sample_data[data_sample_index].append(None)
                    sample_data[data_sample_index][elem_index] = image_id
                    sample_len = max(sample_len, elem_index + 1)

                    frame_count += 1

                    if frame_count % 1000 == 0:
                        print('read %d frames...' % frame_count)

                else:
                    break

            sample_data_element_offset += 1


    # fill in any trailing missing elements
    for si in range(len(sample_data)):
        while len(sample_data[si]) < sample_len:
            sample_data[si].append(None)


    # get end time
    output_end_ms = _helper.timeConvertSampleToMillisecond(len(sample_data) - 1, output_start_ms, dataset_rate, _helper.CONVERT_PERMISSIVE)



    # figure out max zoom level, if needed
    if zoom is None:
        zoom = max(0, min(10, math.ceil(math.log(len(sample_data) / (2.5 * TILE_SIZE), SUBSAMPLE))))



    # print summary
    print('length:       ', len(sample_data))
    print('rate:         ', dataset_rate)
    print('max zoom:     ', zoom)
    print('output start: ', _helper.timeConvertMillisecondToString(output_start_ms))
    print('output end:   ', _helper.timeConvertMillisecondToString(output_end_ms))



    # write tiles
    for zoom_level in range(zoom + 1):
        print('writing zoom %d...' % zoom_level)

        zoom_subsample = SUBSAMPLE ** zoom_level
        zoom_tile_size = TILE_SIZE * zoom_subsample

        ntiles = int(len(sample_data) / zoom_tile_size)
        if len(sample_data) % zoom_tile_size != 0:
            ntiles += 1

        for tt in range(ntiles):
            tile_id = 'z%02dt%06d' % (zoom_level, tt)

            outfilename = os.path.join(tile_folder, tile_id + '.json')

            with open(outfilename, 'wt') as outfile:
                write_startfile(outfile, zoom_subsample, dataset + ':' + tile_id)

                prev = False
                for ss in range(tt * TILE_SIZE, (tt + 1) * TILE_SIZE + 1):
                    rangesmp = sample_data[ss * zoom_subsample:(ss + 1) * zoom_subsample]
                    write_sample(outfile, rangesample(rangesmp, sample_len), prev, sample_len)
                    prev = True

                write_endfile(outfile)

            if (tt + 1) % 1000 == 0:
                print('wrote %d tiles...' % (tt + 1))



    print('writing origin...')

    outfilename = _helper.datasetOriginFilename(dataset)

    with open(outfilename, 'wt') as outfile:
        outfile.write("{\n")
        outfile.write('    "origin": %s\n' % json.dumps(filenames))
        outfile.write('}\n')



    print('writing config...')

    config = collections.OrderedDict()
    config['title'] = dataset
    config['tile_size'] = TILE_SIZE
    config['tile_subsample'] = SUBSAMPLE
    config['zoom_max'] = zoom
    config['length'] = len(sample_data)
    config['start_time_ms'] = output_start_ms
    config['sample_rate'] = dataset_rate
    config['start_day_idx'] = start_day_index
    config['range_span'] = [range_min, range_max]

    config['sensors'] = []
    color_count = 0
    for ii, (sname, range_span, range_unit, (sensortype, sensorfile)) in enumerate(zip(sensor_names, sensor_range_spans, sensor_range_units, sensorfiles)):
        sensor = collections.OrderedDict()
        sensor['sname'] = sname
        sensor['stype'] = sensortype
        sensor['channels'] = sensor_channel_names[sname]

        if sensortype == SENSOR_TYPE_DATA:
            rgb = 2.0 / (color_count + 2)
            color_count += 1
            rr, gg, bb = rgb, rgb, rgb

            sensor['color'] = [ rr, gg, bb ]
            sensor['range_span'] = range_span
            sensor['range_unit'] = range_unit

        config['sensors'].append(sensor)

    config['channels'] = []
    for ii, cname in enumerate(sorted(all_channel_names)):
        if ii % 3 == 0:
            rr, gg, bb = 0.80, 0.20, 0.20
        elif ii % 3 == 1:
            rr, gg, bb = 0.20, 0.80, 0.20
        else:
            rr, gg, bb = 0.20, 0.20, 0.80

        channel = collections.OrderedDict()
        channel['cname'] = cname
        channel['color'] = [ rr, gg, bb ]
        config['channels'].append(channel)

    config['labels'] = []
    for ii, (lname, rr, gg, bb) in enumerate(labels):
        label = collections.OrderedDict()
        label['lname'] = lname
        label['color'] = [ rr, gg, bb ]
        config['labels'].append(label)

    _helper.writeConfig(dataset, config)

    print('dataset written to ' + out_folder)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a csv file to a dataset.')
    parser.add_argument('filenames', type=str, help='CSV file(s) to read from.', nargs='+')
    parser.add_argument('--name', type=str, help='Custom dataset name.', default=None)
    parser.add_argument('--labelfilenames', type=str, help='Custom label csv(s).', default=None, nargs='+')
    parser.add_argument('--zoom', type=int, help='Maximum zoom level.', default=None)
    parser.add_argument('--range-min', type=int, help='Minimum for range axis (default -range-max).', default=None)
    parser.add_argument('--range-max', type=int, help='Maximum for range axis (default %d).' % DEFAULT_RANGE_MAGNITUDE, default=DEFAULT_RANGE_MAGNITUDE)
    parser.add_argument('--custom-fields', type=str, nargs='+', help='CSV fields to use for custom format', default=None)
    parser.add_argument('--custom-start', type=str, help='Start date/time for custom format', default=None)
    parser.add_argument('--custom-sample-rate', type=int, help='Sample rate for custom format (int)', default=None)
    parser.add_argument('--custom-video-frame-rate', type=float, help='Override frame rate for videos (float)', default=None)
    parser.add_argument('--time-field', type=str, help='Field to use for sample times.', default=None)
    parser.add_argument('--fill', type=str, help='How to fill gaps between samples, if any (options: %s; default: None).' % ','.join(FILL_OPTIONS), default=None)
    parser.add_argument('--fill-limit', type=int, help='Largest gap to fill, in seconds (default: None).', default=None)
    parser.add_argument('--sample', type=str, help='Sample index range to output.', default=None)
    parser.add_argument('--day', type=str, help='Day index range to output.', default=None)
    args = parser.parse_args()


    main(args.filenames,
         name=args.name, labelfilenames=args.labelfilenames, zoom=args.zoom,
         range_min=args.range_min, range_max=args.range_max,
         custom_fields=args.custom_fields, custom_start=args.custom_start, custom_sample_rate=args.custom_sample_rate,
         custom_video_frame_rate=args.custom_video_frame_rate,
         time_field=args.time_field, fill=args.fill, fill_limit=args.fill_limit,
         sample=args.sample, day=args.day)
