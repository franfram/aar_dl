import argparse, collections, colorsys, csv, hashlib, json, os, sys
import _root
import _helper



VALID_SOURCES = ['Algo', 'Expert', 'Mturk', 'Notes', 'Player', 'Truth']



def trimActivity(activity, trim, lo, hi):
    if trim:
        activity[0] = max(activity[0], lo)
        activity[1] = min(activity[1], hi)

    return activity[1] > activity[0]



def main(dataset, filename, *, source=None, labelset=None, stdout=False, trim=False, createlabels=False, permissive=False, qcfix=False):
    dataset_config_filename = _helper.datasetConfigFilename(dataset)

    if not os.path.exists(dataset_config_filename):
        _helper.errorExit('could not find dataset config file: ' + dataset_config_filename)

    with open(dataset_config_filename, 'rt') as configfile:
        config = json.load(configfile)

    sample_rate = config['sample_rate']
    length = config['length']

    start_millisecond = config['start_time_ms']
    print('start time:', _helper.timeConvertMillisecondToString(start_millisecond))

    if permissive:
        convert_strictness = _helper.CONVERT_PERMISSIVE
    else:
        convert_strictness = _helper.CONVERT_RELAXED

    FORMAT_NOTES = 'NOTES'
    FORMAT_NOTES_TIME_FORMAT = '%a %b %d %H:%M:%S %Z %Y'
    FORMAT_NOTES_LENGTH_SECONDS = 10 # how long a note label should try to be
    FORMAT_ACTIVITY_GROUP = 'ACTIVITY_GROUP'
    FORMAT_PREDICTION = 'PREDICTION'
    FORMAT_PREDICTED = 'PREDICTED'
    FORMAT_PREDICTED_LABEL_SECONDS = 30

    with open(filename, 'rt') as csvfile:
        reader = csv.DictReader(csvfile)

        # check if file contains labelset and source columns
        if 'LABELSET' in reader.fieldnames and 'SOURCE' in reader.fieldnames and (labelset or source):
            _helper.errorExit('Labelset and source info detected in file, will be used instead of given arguments.')
        elif ('LABELSET' in reader.fieldnames or 'SOURCE' in reader.fieldnames) and ('LABELSET' not in reader.fieldnames or 'SOURCE' not in reader.fieldnames):
            _helper.errorExit('Must provide both labelset and source fields in file or neither.')
        elif (labelset is None or source is None) and (labelset or source):
            _helper.errorExit('Must provide both labelset and source arguments or neither.')

        if labelset is None and 'LABELSET' not in reader.fieldnames:
            _helper.errorExit("No labelset argument provided and no labelset info in file. Cannot import labels.")
        if source is None and 'SOURCE' not in reader.fieldnames:
            _helper.errorExit('No source argument provided and no source info in file. Cannot import labels.')

        use_source_labelset_from_file = ('LABELSET' in reader.fieldnames and 'SOURCE' in reader.fieldnames)

        # figure out format
        format = None
        format_meta = None
        if ('TIME' in reader.fieldnames) and ('TAG' in reader.fieldnames) and ('NOTE' in reader.fieldnames):
            format = FORMAT_NOTES
        elif ('START_TIME' in reader.fieldnames) and ('STOP_TIME' in reader.fieldnames) and ('ACTIVITY_GROUP.y' in reader.fieldnames):
            format = FORMAT_ACTIVITY_GROUP
        elif ('START_TIME' in reader.fieldnames) and ('STOP_TIME' in reader.fieldnames) and ('PREDICTION' in reader.fieldnames):
            format = FORMAT_PREDICTION
        elif ('HEADER_START_TIME' in reader.fieldnames) and ('PREDICTED' in reader.fieldnames):
            format = FORMAT_PREDICTED
            # get label names from header
            format_meta = []
            for field in reader.fieldnames[2:]:
                label = field.split('_')
                if label[0] != 'PROB' or len(label) < 2:
                    sys.stderr.write('unrecognized field in header: expected PROB_...\n')
                    sys.exit(-1)
                label = ' '.join([word.capitalize() for word in label[1:]])
                format_meta.append(label)
        else:
            sys.stderr.write('could not determine format from header fields\n')
            sys.exit(-1)

        sys.stderr.write('detected %s format\n' % format)
        if use_source_labelset_from_file:
            sys.stderr.write('reading source and labelset from file\n')
        else:
            sys.stderr.write('using source %s and labelset %s\n' % (source, labelset))



        # process rows
        labelsets = set()
        labelset_labels = {}
        labelset_sources = {}
        all_label_names = set()

        # this will keep track of the time the last label started to make sure they are sorted
        last_label_start_millisecond = {}

        for row in reader:
            # figure out sample range
            if format == FORMAT_NOTES:
                label_start_millisecond = _helper.timeConvertStringToMillisecond(row['TIME'], FORMAT_NOTES_TIME_FORMAT)
                label_stop_millisecond = label_start_millisecond + FORMAT_NOTES_LENGTH_SECONDS * 1000
                label_name = row['TAG']
                label_detail = row['NOTE']
            elif format == FORMAT_ACTIVITY_GROUP:
                label_start_millisecond = _helper.timeConvertStringToMillisecond(row['START_TIME'], _helper.DATE_FORMAT_YMD)
                label_stop_millisecond = _helper.timeConvertStringToMillisecond(row['STOP_TIME'], _helper.DATE_FORMAT_YMD)
                label_name = row['ACTIVITY_GROUP.y']
                label_detail = None
            elif format == FORMAT_PREDICTION:
                label_start_millisecond = _helper.timeConvertStringToMillisecond(row['START_TIME'], _helper.DATE_FORMAT_YMD)
                label_stop_millisecond = _helper.timeConvertStringToMillisecond(row['STOP_TIME'], _helper.DATE_FORMAT_YMD)
                label_name = row['PREDICTION']
                label_detail = None
            elif format == FORMAT_PREDICTED:
                if int(row['PREDICTED']) >= len(format_meta):
                    sys.stderr.write('PREDICTED index out of range')
                    sys.exit(-1)
                label_start_millisecond = _helper.timeConvertStringToMillisecond(row['HEADER_START_TIME'], _helper.DATE_FORMAT_YMD)
                label_stop_millisecond = label_start_millisecond + 1000 * FORMAT_PREDICTED_LABEL_SECONDS
                label_name = format_meta[int(row['PREDICTED'])]
                label_detail = None
            else:
                _helper.errorExit('unknown format error. Please check documentation for the correct label format')

            # Ignore empty labels
            if label_start_millisecond == label_stop_millisecond:
                _helper.warning("Empty label found. Ignoring it ...")
                continue

            # apply fix for QC end times, if needed
            if qcfix:
                if label_stop_millisecond % 100 == 88:
                    label_stop_millisecond += 12

            # convert from ms to sample
            label_start_sample = _helper.timeConvertMillisecondToSample(label_start_millisecond, start_millisecond, sample_rate, convert_strictness)
            label_stop_sample = _helper.timeConvertMillisecondToSample(label_stop_millisecond, start_millisecond, sample_rate, convert_strictness)

            # figure out source and labelset
            if use_source_labelset_from_file:
                current_labelset = row['LABELSET']
                current_source = row['SOURCE']
            else:
                current_labelset = labelset
                current_source = source

            if current_source not in VALID_SOURCES:
                _helper.errorExit('unrecognized source: ' + current_source + '\nExpecting: ' + ','.join(VALID_SOURCES))

            # check labels are in order
            if current_labelset in last_label_start_millisecond and label_start_millisecond < last_label_start_millisecond[current_labelset]:
                print('label_start_millisecond: ' + str(label_start_millisecond) + '; last_label_start_millisecond for ' + current_labelset + ' is ' + str(last_label_start_millisecond[current_labelset]))
                _helper.errorExit('label start times not sorted')
            last_label_start_millisecond[current_labelset] = label_start_millisecond

            # for notes, go back and make sure any previous note doesn't overlap this one
            if format == FORMAT_NOTES:
                if current_labelset in labelsets and len(labelset_labels[current_labelset]) > 0:
                    labelset_labels[current_labelset][-1][1] = min(labelset_labels[current_labelset][-1][1], label_start_sample)

            # append this label to the labelset
            if current_labelset not in labelsets:
                labelsets.add(current_labelset)
                labelset_labels[current_labelset] = []
                labelset_sources[current_labelset] = current_source

            if labelset_sources[current_labelset] != current_source:
                _helper.errorExit('Labelset with multiple sources detected.')

            labelset_labels[current_labelset].append([label_start_sample, label_stop_sample, label_name, label_detail])
            all_label_names.add(label_name)



        # write labels out
        for labelset in labelsets:
            labels = labelset_labels[labelset]
            source = labelset_sources[labelset]

            # this will be used to merge adjacent time windows that have the same label
            last_activity = None

            # keep track of information about labels output
            was_prev = False
            any_outside = False
            any_far_outside = False

            output = ''
            output += '{"labelset":"%s", "source": "%s", "labels":[' % (labelset, source)

            for label_start_sample, label_stop_sample, label_name, label_detail in labelset_labels[labelset]:
                # see if the label extends beyond the dataset time
                if label_start_sample < 0 or length < label_stop_sample:
                    any_outside = True
                if label_start_sample < 0 - 0.1 * length or length + 0.1 * length < label_stop_sample:
                    any_far_outside = True

                # merge adjacent labels that match
                if not last_activity:
                    last_activity = [label_start_sample, label_stop_sample, label_name, label_detail]
                elif last_activity[1] == label_start_sample and last_activity[2] == label_name and last_activity[3] == label_detail:
                    last_activity[1] = label_stop_sample
                else:
                    if trimActivity(last_activity, trim, 0, length):
                        output += _helper.activityJSON(last_activity, was_prev)
                        was_prev = True
                    last_activity = [label_start_sample, label_stop_sample, label_name, label_detail]

            # account for any remaining label
            if last_activity:
                if trimActivity(last_activity, trim, 0, length):
                    output += _helper.activityJSON(last_activity, was_prev)
                    was_prev = True

            output += ']}\n'

            # display warnings about labels
            if any_far_outside:
                _helper.warning('label found FAR OUTSIDE signal in ' + labelset)
            elif any_outside:
                _helper.warning('label found outside signal in ' + labelset)

            # do output
            if stdout:
                sys.stdout.write(output)

            else:
                # write labels
                labels_filename = _helper.latestLabelsFilename(dataset, labelset)
                with open(_helper.ensureDirExists(labels_filename, True), 'wt') as labelsfile:
                    labelsfile.write(output)

                print('labels added to', labels_filename)

                # update dataset config to account for any new labels, if needed
                if createlabels:
                    dataset_config = _helper.loadConfig(dataset)

                    missing_label_names = set(all_label_names)
                    for label in dataset_config['labels']:
                        missing_label_names.discard(label['lname'])

                    if len(missing_label_names) > 0:
                        missing_label_names = sorted(missing_label_names)
                        for label_name in missing_label_names:
                            digest = hashlib.md5(label_name.encode()).digest()
                            hh = digest[0] / 255.0
                            ss = digest[1] / 255.0 * 0.5 + 0.5
                            vv = digest[2] / 255.0 * 0.5 + 0.5
                            rr, gg, bb = [round(cc, 2) for cc in colorsys.hsv_to_rgb(hh, ss, vv)]

                            label = collections.OrderedDict()
                            label['lname'] = label_name
                            label['color'] = [ rr, gg, bb ]
                            dataset_config['labels'].append(label)

                        _helper.writeConfig(dataset, dataset_config)
                        print('added labels to config: ' + ','.join(missing_label_names))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import algorithm labels.')
    parser.add_argument('dataset', type=str, help='Name of dataset to use.')
    parser.add_argument('filename', type=str, help='CSV file to read from.')
    parser.add_argument('--source', type=str, help='Label source (' + (', '.join(VALID_SOURCES)) + ')', default=None)
    parser.add_argument('--labelset', type=str, help='Labelset ID.', default=None)
    parser.add_argument('--stdout', action='store_true', help='Write output to stdout.')
    parser.add_argument('--trim', action='store_true', help='Trim labels to signal duration.')
    parser.add_argument('--createlabels', action='store_true', help='Create entries for any labels missing from dataset config.')
    parser.add_argument('--permissive', action='store_true', help='Allow permissive conversions for sample times.')
    parser.add_argument('--qcfix', action='store_true', help='Fix for QC output.')
    args = parser.parse_args()

    main(args.dataset, args.filename, source=args.source, labelset=args.labelset, stdout=args.stdout, trim=args.trim, createlabels=args.createlabels, permissive=args.permissive, qcfix=args.qcfix)
