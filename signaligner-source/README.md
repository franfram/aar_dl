# Signaligner

Signaligner, the signal aligner tool, is a web-based utility for annotating multi-day raw accelerometer data for activity recognition.



## Getting Started

### Environment setup

You will need [Python 3.7](https://www.python.org/downloads/). To run properly on large (multi-day) datasets, the 64-bit version of Python3 is required; the 32-bit version can run out of memory.

#### Installing dependencies

Use pipenv to install necessary Python packages, e.g.:

`pip3 install pipenv`

`pipenv install`

On Linux, also install:

`sudo apt install python3-tk`

Run scripts in the pipenv shell with:

`pipenv shell`

#### Running algorithms in Signalauncher

For running labeling algorithms, this repository uses `mdcas-python` as a submodule. To clone, use: `git clone --recurse-submodules`.

If cloned without recursing submodules, you can use `git submodule init` then `git submodule update` to get the submodules.

### Overview and Usage

There are two ways to use Signaligner:
- The command line. There are various scripts for managing data, described below. You can start up the server by running this command from a terminal in the Signaligner directory: `python3 scripts/signaserver.py --http`. Then direct your web browser to: http://localhost:3007/signaclient.html . You should see an example signal loaded into the tool.
- A GUI, called Signalauncher. Run `python3 scripts/signalauncher.py` to start.

### Useful Files and Folders

As a user, the most important files and folders to know about are:

- `scripts/`: the folder containing scripts to process your data. Also contains scripts to run the test algorithms and import new labels.
    - `signaserver.py`: the script you run to boot up the server program
    - `signalauncher.py`: opens a GUI for running script functionality
- `signaclient/`: folder for the main files for the web-based client
    - `signaclient.html`: the main HTML file (the displayed webpage)
    - `signaclient.js`: the main JavaScript code file. Contains all the drawing code for data visualization and label drawing.
- `common/`: includes useful templates and example files



## Example command line workflow

Examples of useful scripts for data processing are given below.

### Start server

Run `python3 scripts/signaserver.py --http` to start the server.

**After running each of the example commands, you can check the dataset, while running the server, at: http://localhost:3007/signaclient.html?dataset=example_sin30min**

**You must import a dataset before importing and exporting labels for that dataset will work.***

### Sample test dataset

Please access a sample test dataset for testing purposes [here] (https://drive.google.com/open?id=1CSXkEh1asJO2L7TbVWZGcvfEa1pE4nXC)

### Importing Datasets

The dataset import script processes your raw accelerometer data into a Signaligner-ready dataset.

For usage information, run `python3 scripts/import_dataset.py --help`.

You will likely want to specify what labels the dataset will need (such as Ambulation/Sedenary or Wear/Non-wear/Sleep).
The `common/` folder has several files that start with `labels_` as example files for this purpose.

If the import was successful, there will be a new dataset in your `datasets/` folder. Each dataset contains a `config.json` file which has the meta-data of your dataset, and a `tiles/` folder which contains all of your data in a format Signaligner can read.

**To test dataset import, you can run `python3 scripts/import_dataset.py common/example_sin30min.csv`.**

### Importing Algorithm Output to Signaligner Labels

If you have the output of a prediction algorithm and you'd like to convert its output into Signaligner labels, use the algorithm label import script.

For usage information, run `python3 scripts/import_labels.py --help`.

**To test algorithm label import, you can run `python3 scripts/import_labels.py example_sin30min common/example_sin30min_algo.csv --source Algo --labelset ALGO`.**

### Importing video

A video needs to be imported along with a data sensor (`.csv` file). Supported video types are `.mp4` and `.mov`.

To import video via command line, import a video file in the same way as a `.csv` file: run `python3 scripts/import_dataset.py <csv_path> <video_path> --name <dataset_name> [--custom-frame-rate float]`.

### Exporting Signaligner Labels to CSV

To convert the Signaligner labels to a CSV, use the CSV export script. They will be written to the `export` folder.

For usage information, run `python3 scripts/export_labels.py --help`.

**To test label csv export, you can run `python3 scripts/export_labels.py example_sin30min`.**



## Notes

Signaligner represents time and sample intervals as half-open intervals that include the begin time/sample but not the end time/sample, i.e. [begin, end).
