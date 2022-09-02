import argparse, csv, os, sys, json, re
import _root
import _helper


def main(dataset):
    # Read start time from config
    with open(_helper.datasetConfigFilename(dataset), 'rt') as json_file:
        data = json.load(json_file)
        start_time_ms = data['start_time_ms']
        sample_rate = data['sample_rate']

    # Read the last stored label of each unique player or labelset
    labelset_labels = _helper.getLabelsLatest(dataset)

    # Write to csv
    csvOutputPath = _helper.exportFilename(dataset)
    _helper.ensureDirExists(csvOutputPath, True)
    with open(csvOutputPath, 'wt', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['START_TIME', 'STOP_TIME', 'PREDICTION', 'SOURCE', 'LABELSET'])

        for labelset_data in labelset_labels:
            labelset = labelset_data['labelset']
            source = labelset_data['source']
            for label in labelset_data['labels']:
                start_time = _helper.timeConvertMillisecondToString(_helper.timeConvertSampleToMillisecond(label['lo'], start_time_ms, sample_rate, _helper.CONVERT_PERMISSIVE))
                stop_time = _helper.timeConvertMillisecondToString(_helper.timeConvertSampleToMillisecond(label['hi'], start_time_ms, sample_rate, _helper.CONVERT_PERMISSIVE))
                prediction = label['lname']
                writer.writerow([start_time, stop_time, prediction, source, labelset])

    print('output written to', csvOutputPath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a json labels file to a csv time stamps.')
    parser.add_argument('dataset', type=str, help='Name of the dataset')
    args = parser.parse_args()

    main(args.dataset)
