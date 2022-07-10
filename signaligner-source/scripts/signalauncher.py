import ctypes, json, os, platform, re, requests, sys, threading, time
import _root
import _folder, _helper
sys.path.append(_root.root_abspath('mdcas-python'))



# UI size constants
BUTTON_WIDTH = 15
DROPDOWN_ALGO_WIDTH = 12
DROPDOWN_DATASET_WIDTH = 50
NO_DATASET_WIDTH = 53

# UI strings
ALGORITHMS = ['MUSS', 'SWaN', 'QC']
MESSAGE_WORK_DONE = 'Work Done'
MESSAGE_HELP = 'Help'
MESSAGE_ERROR = 'Error'
MESSAGE_NEED_DATASET = 'Please import a dataset.'
MESSAGE_NEED_ALGO_FOLDER = 'Algorithm folder not found. Algorithms cannot be run.'


# globals
logger = None
server_thread_ident = 0



# determine data folder
frozen = getattr(sys, 'frozen', False)
mac_ver = platform.mac_ver()[0] if hasattr(platform, 'mac_ver') else None

if frozen:
    _folder.file_folder = _root.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'signaligner'))
_folder.data_folder = _root.abspath(os.path.join(os.path.expanduser('~'), 'Documents', 'SignalignerData'))


# https://bugs.python.org/issue37833
if mac_ver == '10.14.6':
    if frozen:
        input('macOS 10.14.6 not supported. Press enter to exit.')
        sys.exit(0)
    else:
        print('WARNING: macOS 10.14.6 not supported.')


# set up logging to files
class Logger:
    def __init__(self):
        self.main_file = None
        self.main_filename = None
        self.main_widget = None
        self.main_str = ''
        self.server_file = None
        self.server_filename = None
        self.server_widget = None
        self.server_str = ''

    def get(self):
        if threading.get_ident() == server_thread_ident:
            return self.server_file, self.server_widget, self.server_str
        else:
            return self.main_file, self.main_widget, self.main_str

    def set(self, s):
        if threading.get_ident() == server_thread_ident:
            self.server_str = s
        else:
            self.main_str = s

    def write(self, data):
        sys.__stdout__.write(data)
        f, w, s = self.get()
        if f:
            f.write(data)
            f.flush()
        if w:
            MAX_LEN = 8000
            s += data
            if len(s) > MAX_LEN:
                s = s[len(s) - MAX_LEN:]
            self.set(s)

            w.config(state=tk.NORMAL)
            w.delete('1.0', tk.END)
            w.insert(tk.END, s)
            w.config(state=tk.DISABLED)
            w.see(tk.END)
            w.update_idletasks()

    def flush(self):
        sys.__stdout__.flush()
        f, w, s = self.get()
        if f:
            f.flush()

def setuplogging():
    global logger

    if logger is None:
        logger = Logger()
        sys.stdout = logger
        sys.stderr = logger

    time_string =  _helper.timeConvertMillisecondToString(int(1000 * time.time())) + '\n'
    start_string = 'Started logging ' + time_string
    stop_string = 'Stopped logging ' + time_string

    if logger.main_file is not None:
        logger.main_file.write(stop_string)
        logger.main_file.close()

    if logger.server_file is not None:
        logger.server_file.write(stop_string)
        logger.server_file.close()

    logger.main_filename = _folder.data_abspath('log', 'signalauncher.main.txt')
    logger.main_file = open(_helper.ensureDirExists(logger.main_filename, True), 'wt')
    logger.main_file.write(start_string)
    logger.main_file.flush()

    logger.server_filename = _folder.data_abspath('log', 'signalauncher.server.txt')
    logger.server_file = open(_helper.ensureDirExists(logger.server_filename, True), 'wt')
    logger.server_file.write(start_string)
    logger.server_file.flush()



# utility functions
def datasetexists(dataset):
    out_folder = _helper.datasetDir(dataset)
    return os.path.exists(out_folder)

def mhealthfolder(dataset, sensor):
    return _folder.data_abspath('algo', dataset, 'mhealth', sensor)

def algofolder(dataset, sensor):
    return _folder.data_abspath('algo', dataset, 'output', sensor)

def get_dataset_raw_file_paths(dataset):
    origin_file = _helper.datasetOriginFilename(dataset)
    if os.path.exists(origin_file):
        with open(origin_file, 'rt') as origin:
            origin_json = json.load(origin)
            return origin_json['origin']
    return []



# import UI elements
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import tkinter.scrolledtext as tkst



class StandardOptionMenu:
    def __init__(self, parent, row, column, width, options, msg_empty):
        self.options = options
        if len(options) == 0:
            options = [msg_empty]
            self.is_empty = True
        else:
            self.is_empty = False

        self.selected = tk.StringVar(parent)
        self.selected.set(options[0])
        self.menu = tk.OptionMenu(parent, self.selected, *options)
        self.menu.config(width=width)
        self.menu.grid(row=row, column=column, sticky="w")

        if self.is_empty:
            self.menu.config(state=tk.DISABLED)

    def update_menu(self, cmd, preferred, options, msg_empty):
        def wrap_cmd(opt):
            def use_cmd():
                self.selected.set(opt)
                if cmd:
                    cmd()
            return use_cmd

        self.options = options

        self.menu.config(state=tk.NORMAL)

        # https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
        m = self.menu['menu']
        m.delete(0, 'end')
        if len(options) > 0:
            for option in options:
                m.add_command(label=option, command=wrap_cmd(option))
            if preferred and preferred in options:
                self.selected.set(preferred)
            else:
                self.selected.set(options[0])
            self.is_empty = False
            return True
        else:
            m.add_command(label=msg_empty)
            self.selected.set(msg_empty)
            self.menu.config(state=tk.DISABLED)
            self.is_empty = True
            return False


class Signalauncher(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        # menu widgets
        self.dataset_om = None

        self.copy_labels_from_om = None
        self.copy_labels_from_button = None

        self.algorithm_folder_exists = os.path.exists(_folder.file_abspath('mdcas-python'))
        self.algorithm_sensor_om = None
        self.algorithm_name_om = None
        self.algorithm_button = None
        self.data_folder_label = None
        self.data_folder_main_log_label = None
        self.data_folder_server_log_label = None

        # other widgets
        self.work_remember_state = []
        self.widgets_work_disable = []
        self.buttons_need_dataset = []
        self.button_cancel_work = None

        # misc vars
        self.import_labels_permissive = tk.BooleanVar()
        self.import_labels_permissive.set(False)
        self.import_labels_create_missing = tk.BooleanVar()
        self.import_labels_create_missing.set(True)

        # threads
        self.work_thread = None
        self.server_thread = None

        self.create_widgets()
        self.refresh()
        self.pack()

    def close_window(self):
        self.master.withdraw()
        self.master.update()
        self.master.destroy()

    def update_select_dataset_widget(self, preferred):
        datasets = _helper.getDatasetList()
        if preferred == None:
            preferred = None if self.dataset_om.is_empty else self.dataset_om.selected.get()

        enabled = self.dataset_om.update_menu(self.handle_select_dataset, preferred, datasets, MESSAGE_NEED_DATASET)

    def update_copy_labels_widget(self):
        datasets = self.dataset_om.options
        preferred = None if self.dataset_om.is_empty else self.dataset_om.selected.get()

        enabled = self.copy_labels_from_om.update_menu(None, preferred, datasets, MESSAGE_NEED_DATASET)

        if enabled:
            self.copy_labels_from_button.config(state=tk.NORMAL)
        else:
            self.copy_labels_from_button.config(state=tk.DISABLED)

    def create_label_and_help_button(self, row, name, message):
        frame = tk.Frame(self)
        tk.Label(frame, text=name).pack(side="left")
        tk.Button(frame, text='?', command=lambda: tk.messagebox.showinfo(MESSAGE_HELP, message), width=2).pack(side="left")
        frame.grid(row=row, column=0, sticky="w")
        #tk.Label(self, text=name).grid(row=row, column=0, sticky="w")
        #tk.Button(self, text='?', command=lambda: tk.messagebox.showinfo(MESSAGE_HELP, message), width=2).grid(row=row, column=1, sticky="w")

    START_COLUMN = 1

    def create_widgets(self):
        row = 0

        self.create_label_and_help_button(row, 'Open Test Dataset:', 'Open a pre-loaded example dataset in a web browser.')
        btn = tk.Button(self, text='Open', command=self.handle_opentest, width=BUTTON_WIDTH)
        btn.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.widgets_work_disable.append(btn)
        del btn
        row += 1

        tk.Label(self, text="").grid(row=row, sticky="w")
        row += 1

        self.create_label_and_help_button(row, 'Import Single Dataset:', 'Import file(s) into a single dataset. A single dataset belongs to data from only one participant.')
        btn = tk.Button(self, text='Select File/Folder', command=self.handle_import_dataset, width=BUTTON_WIDTH)
        btn.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.widgets_work_disable.append(btn)
        del btn
        row += 1

        self.create_label_and_help_button(row, 'Import Multiple Datasets:', 'Import files from different folders into multiple datasets. A single dataset belongs to data from only one participant.')
        btn = tk.Button(self, text='Select Folder', command=self.handle_import_all_dataset, width=BUTTON_WIDTH)
        btn.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.widgets_work_disable.append(btn)
        del btn
        row += 1

        tk.Label(self, text="").grid(row=row, sticky="w")
        row += 1

        self.create_label_and_help_button(row, 'Select Dataset:', 'Choose the dataset to work on.')
        self.dataset_om = StandardOptionMenu(self, row, self.START_COLUMN, DROPDOWN_DATASET_WIDTH, [], MESSAGE_NEED_DATASET)
        self.widgets_work_disable.append(self.dataset_om.menu)
        row += 1

        self.create_label_and_help_button(row, 'Open Selected Dataset:', 'Open the selected dataset in a web browser.')
        btn = tk.Button(self, text="Open", command=self.handle_load_dataset, width=BUTTON_WIDTH)
        btn.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.buttons_need_dataset.append(btn)
        self.widgets_work_disable.append(btn)
        del btn
        row += 1

        self.create_label_and_help_button(row, 'Delete Selected Dataset:', 'Delete files for the selected dataset. Removes algorithm output and existing labels for this dataset.')
        btn = tk.Button(self, text="Delete", command=self.handle_delete_dataset, width=BUTTON_WIDTH)
        btn.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.buttons_need_dataset.append(btn)
        self.widgets_work_disable.append(btn)
        del btn
        row += 1

        self.create_label_and_help_button(row, 'Import Dataset Labels:', 'Import labels into the selected dataset.')
        frame = tk.Frame(self)
        btn = tk.Button(frame, text='Select File', command=self.handle_import_labels, width=BUTTON_WIDTH)
        btn.pack(side='left')
        self.buttons_need_dataset.append(btn)
        self.widgets_work_disable.append(btn)
        del btn
        chk = tk.Checkbutton(frame, text='Create missing labels', variable=self.import_labels_create_missing)
        chk.pack(side='left', padx=[10, 0])
        self.buttons_need_dataset.append(chk)
        self.widgets_work_disable.append(chk)
        del chk
        chk = tk.Checkbutton(frame, text='Arbitrary rounding to sample', variable=self.import_labels_permissive)
        chk.pack(side='left', padx=[10, 0])
        self.buttons_need_dataset.append(chk)
        self.widgets_work_disable.append(chk)
        del chk
        lbl = tk.Label(frame, text="(Options also apply to algorithm label import)")
        lbl.pack(side='left', padx=[10, 0])
        self.buttons_need_dataset.append(lbl)
        self.widgets_work_disable.append(lbl)
        del lbl
        frame.grid(row=row, column=self.START_COLUMN, columnspan=3, sticky="w")
        del frame
        row += 1

        self.create_label_and_help_button(row, 'Export Dataset Labels:', 'Export labels from the selected dataset in .csv format.')
        btn = tk.Button(self, text="Export", command=self.handle_export_labels, width=BUTTON_WIDTH)
        btn.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.buttons_need_dataset.append(btn)
        self.widgets_work_disable.append(btn)
        del btn
        row += 1

        self.create_label_and_help_button(row, 'Run Algorithm on Sensor:', 'Run a labeling algorithm on a sensor from the selected dataset.  Choose the sensor within the dataset and the algorithm to run on it.')
        if self.algorithm_folder_exists:
            self.algorithm_sensor_om = StandardOptionMenu(self, row, self.START_COLUMN, DROPDOWN_DATASET_WIDTH, [], MESSAGE_NEED_DATASET)
            self.algorithm_name_om = StandardOptionMenu(self, row, self.START_COLUMN+1, DROPDOWN_ALGO_WIDTH, ALGORITHMS, 'None')
            self.algorithm_button = tk.Button(self, text="Run", command=self.handle_run_algo, width=BUTTON_WIDTH)
            self.algorithm_button.grid(row=row, column=self.START_COLUMN+2, sticky="w")
            self.widgets_work_disable.append(self.algorithm_sensor_om.menu)
            self.widgets_work_disable.append(self.algorithm_name_om.menu)
            self.widgets_work_disable.append(self.algorithm_button)
        else:
            lbl = tk.Label(self, text=MESSAGE_NEED_ALGO_FOLDER)
            lbl.grid(row=row, column=self.START_COLUMN, sticky="w")
            lbl.config(state=tk.DISABLED)
        row += 1

        self.create_label_and_help_button(row, 'Copy Labels from Dataset:', 'Copy labels from another dataset into the selected dataset.')
        self.copy_labels_from_om = StandardOptionMenu(self, row, self.START_COLUMN, DROPDOWN_DATASET_WIDTH, [], MESSAGE_NEED_DATASET)
        self.copy_labels_from_button = tk.Button(self, text="Copy", command=self.handle_copy_labels, width=BUTTON_WIDTH)
        self.copy_labels_from_button.grid(row=row, column=self.START_COLUMN+1, sticky="w")
        self.widgets_work_disable.append(self.copy_labels_from_om.menu)
        self.widgets_work_disable.append(self.copy_labels_from_button)
        row += 1

        tk.Label(self, text="").grid(row=row, sticky="w")
        row += 1

        self.create_label_and_help_button(row, 'Cancel Work:', 'Cancel any currently running work.')
        self.button_cancel_work = tk.Button(self, text='Cancel', command=self.handle_cancel, width=BUTTON_WIDTH)
        self.button_cancel_work.grid(row=row, column=self.START_COLUMN, sticky="w")
        self.button_cancel_work.config(state=tk.DISABLED)
        row += 1

        self.create_label_and_help_button(row, 'Quit Signalauncher:', 'Quit the program.')
        tk.Button(self, text='Quit', command=self.handle_quit, width=BUTTON_WIDTH).grid(row=row, column=self.START_COLUMN, sticky="w")
        row += 1

        tk.Label(self, text="").grid(row=row, sticky="w")
        row += 1

        self.create_label_and_help_button(row, 'Data Folder:', 'The location of the data files the program uses.')
        self.data_folder_label = tk.Label(self, text=_folder.data_folder)
        self.data_folder_label.grid(row=row, column=self.START_COLUMN, columnspan=3, sticky="w")
        btn = tk.Button(self, text='Select Data Folder', command=self.handle_select_data_folder, width=BUTTON_WIDTH).grid(row=row, column=self.START_COLUMN+1, sticky="w")
        row += 1

        self.create_label_and_help_button(row, 'Main Log:', 'Log file for the program and any work it does.')
        self.data_folder_main_log_label = tk.Label(self, text=logger.main_filename)
        self.data_folder_main_log_label.grid(row=row, column=self.START_COLUMN, columnspan=3, sticky="w")
        row += 1

        main_text = tkst.ScrolledText(self, wrap=tk.NONE, state=tk.DISABLED, background='#DDDDDD', width=150, height=15)
        main_text.grid(row=row, column=0, columnspan=4, sticky="w")
        logger.main_widget = main_text
        row += 1

        self.create_label_and_help_button(row, 'Server Log:', 'Location for the log file for the web server.')
        self.data_folder_server_log_label = tk.Label(self, text=logger.server_filename)
        self.data_folder_server_log_label.grid(row=row, column=self.START_COLUMN, columnspan=3, sticky="w")
        row += 1

        server_text = tkst.ScrolledText(self, wrap=tk.NONE, state=tk.DISABLED, background='#DDDDDD', width=150, height=5)
        server_text.grid(row=row, column=0, columnspan=4, sticky="w")
        logger.server_widget = server_text
        row += 1

    def start_work(self, target, kwargs, done_callback, success_message):
        if self.work_thread != None:
            messagebox.showerror(MESSAGE_ERROR, "Wait for the current work to finish.")
            return

        self.button_cancel_work.config(state=tk.NORMAL)

        self.work_remember_state = []
        for child in self.widgets_work_disable:
            self.work_remember_state.append((child, child.cget('state')))
            child.config(state=tk.DISABLED)

        print('Starting work.')

        self.work_thread = threading.Thread(target=self.run_work, args=(target, kwargs, done_callback, success_message), daemon=True)
        self.work_thread.start()

    def run_work(self, target, kwargs, done_callback, success_message):
        target_success = False
        try:
            target(**kwargs)
            target_success = True
        except Exception as e:
            print('An error occurred: ' + str(e))
        except:
            print('An unspecified error occurred.')

        self.button_cancel_work.config(state=tk.DISABLED)

        for child, restore in self.work_remember_state:
            child.config(state=restore)
        self.work_remember_state = []

        done_success = True
        try:
            if (done_callback):
                done_success = False
                done_callback()
                done_success = True
        except Exception as e:
            print('An error occurred: ' + str(e))

        print('Work done!')

        if success_message:
            if target_success and done_success:
                tk.messagebox.showinfo(MESSAGE_WORK_DONE, success_message)
            else:
                tk.messagebox.showerror(MESSAGE_ERROR, 'An error occurred. Check the log for more information.')

        self.work_thread = None

    def start_server(self):
        print('Starting server.')

        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def run_server(self):
        global server_thread_ident
        server_thread_ident = threading.get_ident()

        import signaserver
        signaserver.main(disable_logging=True)

    def handle_opentest(self):
        import webbrowser
        webbrowser.open('http://localhost:3007/signaclient.html?labelset=DEFAULT')

    def handle_select_dataset(self):
        dataset = self.dataset_om.selected.get()

        # Update Copy From dataset dropdown list
        self.copy_labels_from_om.selected.set(dataset)

        # Update algo csv dropdown list
        self.update_algo_dropdown()

    def update_algo_dropdown(self):
        if not self.algorithm_folder_exists:
            return

        if self.dataset_om.is_empty:
            enabled = self.algorithm_sensor_om.update_menu(None, None, [], MESSAGE_NEED_DATASET)
        else:
            dataset = self.dataset_om.selected.get()
            raw_file_paths = get_dataset_raw_file_paths(dataset)

            sensor_names = []
            for filename in raw_file_paths:
                sensor_names.append(_helper.makeIdFromFilename(filename))
            if len(sensor_names) > 1:
                sensor_names.append("ALL")

            enabled = self.algorithm_sensor_om.update_menu(None, None, sensor_names, 'No sensors found in dataset.')

        if enabled:
            self.algorithm_name_om.menu.config(state=tk.NORMAL)
            self.algorithm_button.config(state=tk.NORMAL)
        else:
            self.algorithm_name_om.menu.config(state=tk.DISABLED)
            self.algorithm_button.config(state=tk.DISABLED)

    def select_raw_data(self, multi_sensor=False):
        data_path = filedialog.askdirectory() if multi_sensor else filedialog.askopenfilename()

        if data_path != '':
            dataset = _helper.makeIdFromFilename(data_path)
            return data_path, dataset, datasetexists(dataset)
        else:
            return None, None, None

    def refresh(self, select_dataset=None):
        self.update_select_dataset_widget(select_dataset)
        self.update_copy_labels_widget()
        self.update_algo_dropdown()

        self.data_folder_label.configure(text=_folder.data_folder)
        self.data_folder_main_log_label.configure(text=logger.main_filename)
        self.data_folder_server_log_label.configure(text=logger.server_filename)

        for btn in self.buttons_need_dataset:
            if self.dataset_om.is_empty:
                btn.config(state=tk.DISABLED)
            else:
                btn.config(state=tk.NORMAL)

    def handle_select_data_folder(self):
        folder_selected = filedialog.askdirectory(title='Select Data Folder');

        if not folder_selected:
            return

        _folder.data_folder = _root.abspath(folder_selected)
        setuplogging()

        self.refresh()

    def handle_import_dataset(self):
        msgBox = tk.messagebox.askyesnocancel("Import Dataset", "Does your dataset contain multiple sensors? Click No if your dataset has only one sensor.", default=messagebox.NO)
        if msgBox is None:
            return
        else:
            path, dataset, datasetex = self.select_raw_data(msgBox)

            # get list of files to import
            files_to_import = []
            if not msgBox:
                files_to_import.append(path)
            else:
                folder_contents = os.listdir(path)
                sensor_files = [os.path.join(path, item) for item in folder_contents if _helper.isFilenameDatasetImportable(item)]
                files_to_import += sensor_files

            # import and load dataset
            if path != None:
                if not datasetex:
                    labelfilenames = [_folder.file_abspath('common', labelfile) for labelfile in ['labels_SWaN.csv', 'labels_MUSS.csv', 'labels_ambsed.csv', 'labels_goodbad.csv', 'labels_unknown.csv']]
                    import import_dataset
                    self.start_work(import_dataset.main, { 'filenames':files_to_import, 'name':dataset, 'labelfilenames':labelfilenames }, lambda: self.refresh(dataset), 'The dataset has been successfully imported.')
                else:
                    print('dataset %s already imported' % dataset)

    def handle_import_all_dataset(self):
        #Handle multiple datasets.
        data_path = filedialog.askdirectory()

        if data_path != '':
            try:
                import import_all_datasets
                self.start_work(import_all_datasets.main, { 'foldername':data_path }, self.refresh, 'The datasets have been successfully imported.')
            except:
                print('An error occured with processing the folder')

    def handle_delete_dataset(self):
        # checks if there is anything to be removed
        if self.dataset_om.is_empty:
            tk.messagebox.showerror(MESSAGE_ERROR, MESSAGE_NEED_DATASET)
            return

        msgBox = tk.messagebox.askyesnocancel("Delete Dataset", "Would you also like to delete all files related to the dataset?")
        if msgBox is None:
            return
        else:
            dataset = self.dataset_om.selected.get()
            import delete_dataset
            self.start_work(delete_dataset.main, { 'dataset':dataset, 'allfiles':msgBox }, self.refresh, 'The dataset has been successfully deleted.')

    def handle_load_dataset(self):
        if self.dataset_om.is_empty:
            tk.messagebox.showerror(MESSAGE_ERROR, MESSAGE_NEED_DATASET)
            return

        dataset = self.dataset_om.selected.get()
        if (dataset != "Select Dataset"):
            import webbrowser
            webbrowser.open('http://localhost:3007/signaclient.html?labelset=DEFAULT&dataset=' + dataset)
        else:
            messagebox.showerror(MESSAGE_ERROR, 'No dataset has been selected.')

    def handle_import_labels(self):
        if self.dataset_om.is_empty:
            tk.messagebox.showerror(MESSAGE_ERROR, MESSAGE_NEED_DATASET)
            return

        dataset = self.dataset_om.selected.get()
        import_file_path = filedialog.askopenfilename()
        filename = import_file_path

        if import_file_path == '':
            return
        else:
            import import_labels
            self.start_work(self.run_import_labels, { 'dataset':dataset, 'filename':import_file_path }, None, None)

    def run_import_labels(self, dataset, filename, kwargs={}):
        createlabels = self.import_labels_create_missing.get()
        permissive = self.import_labels_permissive.get()

        import import_labels
        import_labels.main(dataset, filename, createlabels=createlabels, permissive=permissive, **kwargs)

    def handle_export_labels(self):
        if self.dataset_om.is_empty:
            tk.messagebox.showerror(MESSAGE_ERROR, MESSAGE_NEED_DATASET)
            return

        dataset = self.dataset_om.selected.get()
        import export_labels
        self.start_work(export_labels.main, { 'dataset':dataset }, None, None)

    def handle_copy_labels(self):
        from_dataset = self.copy_labels_from_om.selected.get()
        to_dataset = self.dataset_om.selected.get()

        if from_dataset == to_dataset:
            tk.messagebox.showerror(MESSAGE_ERROR, "The dataset to copy from must not be the selected dataset.")
            return
        else:
            trim = tk.messagebox.askyesnocancel("Copy Labels", "Trim the labels to the length of the selected dataset?")
            if trim is None:
                return
            else:
                import copy_labels
                self.start_work(copy_labels.main, { 'source_dataset':from_dataset, 'dest_dataset':to_dataset, 'notrim':not trim }, None, None)

    def handle_run_algo(self):
        if not self.algorithm_folder_exists:
            tk.messagebox.showerror(MESSAGE_ERROR, MESSAGE_NEED_ALGO_FOLDER)
            return

        if self.dataset_om.selected is None:
            tk.messagebox.showerror(MESSAGE_ERROR, "Please import a dataset first.")
            return

        algorithm = self.algorithm_name_om.selected.get()
        dataset = self.dataset_om.selected.get()
        csv_selected = self.algorithm_sensor_om.selected.get()

        self.start_work(self.run_algorithm, { 'algorithm':algorithm, 'dataset':dataset, 'csv_selected':csv_selected }, None, None)

    def run_algorithm(self, algorithm, dataset, csv_selected):
        swan = algorithm == 'SWaN'
        muss = algorithm == 'MUSS'
        qc = algorithm == 'QC'

        dataset_raw_csv_paths = get_dataset_raw_file_paths(dataset)

        error_messages = []
        success_algo_csv_list = []

        run_algo_csv_list = []
        for filepath in dataset_raw_csv_paths:
            if csv_selected == "ALL" or _helper.makeIdFromFilename(filepath) == csv_selected:
                run_algo_csv_list.append(filepath)

        for filepath in run_algo_csv_list:
            if not os.path.exists(filepath):
                error_messages.append('Algorithm not run on missing file; try moving back to its original location: %s' % filepath)
            else:
                sensor_name = _helper.makeIdFromFilename(filepath)
                mhealth_folder = mhealthfolder(dataset, sensor_name)
                algo_folder = algofolder(dataset, sensor_name)

                if not os.path.exists(mhealth_folder):
                    import import_mhealth
                    import_mhealth.main(filepath, mhealth_folder)

                old_cwd = _root.abspath(os.path.realpath(os.getcwd()))

                dataset_config = _helper.loadConfig(dataset)
                dataset_sample_rate = dataset_config['sample_rate']

                try:
                    import mdcas_main
                    os.chdir(_folder.file_abspath('mdcas-python'))
                    print('Start algorithm processing ...')
                    mdcas_main.main(os.path.join(mhealth_folder, 'default'), os.path.join(algo_folder, 'default'), dataset_sample_rate, profiling=False, swan=swan, muss=muss, qc=qc)
                except Exception as e:
                    error_messages.append('Error running algorithm in mdcas-python - maybe submodule needs to be set up? (%s)' % str(e))
                    break

                os.chdir(old_cwd)

                if swan:
                    print("Running SWaN algorithm...")
                    self.run_import_labels(dataset, os.path.join(algo_folder, 'default', 'SWaN_output.csv'), { 'source': 'Algo', 'labelset': 'SWaN_' + sensor_name })
                elif muss:
                    print("Running MUSS algorithm...")
                    self.run_import_labels(dataset, os.path.join(algo_folder, 'default', 'muss_output.csv'), { 'source': 'Algo', 'labelset': 'MUSS_' + sensor_name })
                elif qc:
                    print("Running QC algorithm...")
                    self.run_import_labels(dataset, os.path.join(algo_folder, 'default', 'qc_output.csv'), { 'source': 'Algo', 'labelset': 'QC_' + sensor_name, 'qcfix': True })

                success_algo_csv_list.append(filepath)

        if len(success_algo_csv_list) > 0:
            tk.messagebox.showinfo(MESSAGE_WORK_DONE, 'Algorithm labels successfully added for the following files: ' +
                                   ', '.join([_helper.makeIdFromFilename(filepath) for filepath in success_algo_csv_list]))

        if len(error_messages) > 0:
            if len(error_messages) > 4: # only show first 4 messages
                error_messages = error_messages[:4] + ['...']
            tk.messagebox.showerror(MESSAGE_ERROR, 'There were one or more errors running algorithms:\n' + '\n'.join(error_messages))

    def handle_cancel(self):
        if self.work_thread == None:
            tk.messagebox.showerror(MESSAGE_ERROR, 'No work is currently running.')
        else:
            # https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
            # http://tomerfiliba.com/recipes/Thread2/
            use_tid = None
            for tid, tobj in threading._active.items():
                if tobj is self.work_thread:
                    use_tid = tid
                    break
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(use_tid), ctypes.py_object(SystemExit))

    def handle_quit(self):
        self.close_window()



if __name__ == '__main__':
    # multiprocessing.freeze_support() # if using multiprocessing

    try:
        r = requests.get('http://localhost:3007')
    except OSError:
        r = None

    if not isinstance(r, requests.models.Response):
        setuplogging()
        root = tk.Tk()
        root.title('Signalauncher')
        root.resizable(0, 0)
        app = Signalauncher(master=root)
        root.protocol('WM_DELETE_WINDOW', app.handle_quit) # add event handler for window close
        app.start_server()
        app.mainloop()
    else:
        tk.Tk().withdraw()
        messagebox.showerror(MESSAGE_ERROR, 'It looks like the application is running already!')
