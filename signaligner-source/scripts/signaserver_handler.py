import http.server, argparse, cgi, json, os, re, subprocess, sys, time, urllib.parse
import _root
import _folder, _helper



class SignaserverHandler(http.server.BaseHTTPRequestHandler):
    RE_ALNUMUN = re.compile(r'(\w+)')
    RE_PNG = re.compile(r'/(\w+)\.png')
    RE_HTML = re.compile(r'/(\w+)\.html')
    RE_JS = re.compile(r'/(\w+)\.js')
    RE_CSS = re.compile(r'/(\w+)\.css')



    CTYPE_PLAIN='text/plain'
    CTYPE_HTML='text/html'
    CTYPE_JS='text/javascript'
    CTYPE_PNG='image/png'
    CTYPE_JPEG='image/jpeg'
    CTYPE_CSS = 'text/css'


    LABELSET_ERROR = 'NOLABELSET'



    _labelsets = set()

    _debug_delay = None
    _disable_logging = False



    ## overrides
    def setup(self):
        self.timeout = 10
        http.server.BaseHTTPRequestHandler.setup(self)



    ## utility functions
    def _gen_labelset(self):
        while True:
            sess = _helper.makeId()

            if sess not in SignaserverHandler._labelsets:
                SignaserverHandler._labelsets.add(sess)
                return sess


    def _extension_var_name(self):
        return ''

    def _extension_var_js_script(self):
        return ''

    def _extension_var_css_style(self):
        return ''

    def _extension_var_html_body(self):
        return ''

    def _replace_vars(self, data, labelset, can_gen_labelset):
        data = data.replace('{{LABELSET}}', labelset)

        if '{{GITREV}}' in data:
            rev = 'NONE'

            try:
                gitrev = subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
                if gitrev != '':
                    try:
                        gittag = subprocess.check_output(['git', 'describe', '--tags', '--exact-match', '--abbrev=0'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
                        if gittag != '':
                            gitrev = gittag + ' (' + gitrev + ')'
                    except:
                        pass

                    try:
                        modified = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
                        if modified != '':
                            gitrev = gitrev + '+'
                    except:
                        gitrev = gitrev + '?'

                    rev = gitrev
            except:
                pass

            data = data.replace('{{GITREV}}', rev)

        if can_gen_labelset and data.find('{{GENLABELSET}}') != -1:
            data = data.replace('{{GENLABELSET}}', self._gen_labelset())
        else:
            data = data.replace('{{GENLABELSET}}', SignaserverHandler.LABELSET_ERROR)

        data = data.replace('{{EXTENSION-NAME}}', self._extension_var_name())
        data = data.replace('{{EXTENSION-JS-SCRIPT}}', self._extension_var_js_script())
        data = data.replace('{{EXTENSION-CSS-STYLE}}', self._extension_var_css_style())
        data = data.replace('{{EXTENSION-HTML-BODY}}', self._extension_var_html_body())

        return data




    ## request handlers

    def _send_header(self, code, ctype, additional={}):
        self.send_response(code)
        self.send_header('Content-type', ctype)
        for key, val in additional.items():
            self.send_header(key, val)
        self.end_headers()

    def _send_data(self, data, binary):
        if not binary:
            data = data.encode('utf-8')

        # Python 3, until 3.6, may not write all the data to wfile in one call
        toWrite = len(data)
        writtenSoFar = 0
        while writtenSoFar < toWrite:
            writtenSoFar += self.wfile.write(data[writtenSoFar:])

    def _send_header_and_file_data(self, filename, binary, ctype, data_cb=None):
        if not os.path.exists(filename):
            self._send_header(404, ctype)
            return

        data = self._file_contents(filename, binary)

        if data_cb:
            data = data_cb(data)
        self._send_header(200, ctype)
        self._send_data(data, binary)

    def _file_contents(self, filename, binary):
        if binary:
            flags = 'rb'
        else:
            flags = 'rt'

        with open(filename, flags) as dfile:
            return dfile.read()

    def _is_static_file(self, path, vars, static_folder):
        for re_check in [SignaserverHandler.RE_HTML, SignaserverHandler.RE_PNG, SignaserverHandler.RE_JS, SignaserverHandler.RE_CSS]:
            if re_check.match(path) and os.path.exists(_folder.file_abspath(static_folder, *path.split('/'))):
                return True
        return False

    def _send_static_file(self, path, vars, static_folder):
        if SignaserverHandler.RE_HTML.match(path):
            if 'labelset' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['labelset']):
                labelset = vars['labelset']
            else:
                labelset = SignaserverHandler.LABELSET_ERROR

            def replace_data(data):
                return self._replace_vars(data, labelset, True)

            self._send_header_and_file_data(_folder.file_abspath(static_folder, *path.split('/')), False, SignaserverHandler.CTYPE_HTML, replace_data)

        elif SignaserverHandler.RE_PNG.match(path):
            self._send_header_and_file_data(_folder.file_abspath(static_folder, *path.split('/')), True, SignaserverHandler.CTYPE_PNG)

        elif SignaserverHandler.RE_JS.match(path):
            self._send_header_and_file_data(_folder.file_abspath(static_folder, *path.split('/')), False, SignaserverHandler.CTYPE_JS)

        elif SignaserverHandler.RE_CSS.match(path):
            self._send_header_and_file_data(_folder.file_abspath(static_folder, *path.split('/')), False, SignaserverHandler.CTYPE_CSS)

        else:
            self._send_header(404, SignaserverHandler.CTYPE_PLAIN)

    def _process_request_extension(self, path, vars):
        self._send_header(404, SignaserverHandler.CTYPE_PLAIN)

    def _process_request(self, path, vars):
        if SignaserverHandler._debug_delay:
            time.sleep(SignaserverHandler._debug_delay)

        if path == '/signaclient.html':
            if 'labelset' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['labelset']):
                labelset = vars['labelset']
            else:
                labelset = SignaserverHandler.LABELSET_ERROR

            def replace_data(data):
                data = self._replace_vars(data, labelset, False)
                return data

            self._send_header_and_file_data(_folder.file_abspath('signaclient', 'signaclient.html'), False, SignaserverHandler.CTYPE_HTML, replace_data)

        elif path == '/signaclient.js':
            if 'labelset' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['labelset']):
                labelset = vars['labelset']
            else:
                labelset = SignaserverHandler.LABELSET_ERROR

            def replace_data(data):
                data = self._replace_vars(data, labelset, False)
                return data

            self._send_header_and_file_data(_folder.file_abspath('signaclient', 'signaclient.js'), False, SignaserverHandler.CTYPE_JS, replace_data)

        elif path == '/favicon.png':
            self._send_header_and_file_data(_folder.file_abspath('signaclient', 'favicon.png'), True, SignaserverHandler.CTYPE_PNG)

        elif path == '/fetchdatasetlist':
            datasets = _helper.getDatasetList()
            self._send_header(200, SignaserverHandler.CTYPE_PLAIN)
            self._send_data(json.dumps(datasets), False)

        elif path == '/fetchdataset':
            if 'dataset' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['dataset']):
                dataset_name = vars['dataset']

                if 'type' in vars and vars['type'] == 'config':
                    file_path = _helper.datasetConfigFilename(dataset_name)
                    file_binary = False
                    file_type = SignaserverHandler.CTYPE_PLAIN
                elif 'type' in vars and vars['type'] == 'tile' and 'id' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['id']):
                    file_path = os.path.join(_helper.datasetTileDir(dataset_name), vars['id'] + '.json')
                    file_binary = False
                    file_type = SignaserverHandler.CTYPE_PLAIN
                elif 'type' in vars and vars['type'] == 'image' and 'sensor' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['sensor']) and 'id' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['id']):
                    file_path = _helper.imageFilename(dataset_name, vars['sensor'], vars['id'])
                    file_binary = True
                    file_type = SignaserverHandler.CTYPE_JPEG
                else:
                    self._send_header(404, SignaserverHandler.CTYPE_PLAIN)
                    return

                if not os.path.exists(file_path):
                    self._send_header(404, SignaserverHandler.CTYPE_PLAIN)
                    return

                self._send_header_and_file_data(file_path, file_binary, file_type)
            else:
                self._send_header(404, SignaserverHandler.CTYPE_PLAIN)

        elif path == '/fetchlabels':
            if 'dataset' in vars and SignaserverHandler.RE_ALNUMUN.match(vars['dataset']):
                dataset = vars['dataset']

                self._send_header(200, SignaserverHandler.CTYPE_PLAIN)
                labels = _helper.getLabelsLatest(dataset)
                if labels:
                    self._send_data(json.dumps(labels), False)
            else:
                self._send_header(404, SignaserverHandler.CTYPE_PLAIN)

        elif path == '/reportlabels':
            if 'data' in vars:
                data = json.loads(vars['data'])

                if 'dataset' in data and SignaserverHandler.RE_ALNUMUN.match(data['dataset']) and 'labelset' in data and SignaserverHandler.RE_ALNUMUN.match(data['labelset']):
                    dataset = data['dataset']
                    labelset = data['labelset']

                    if not SignaserverHandler._disable_logging:
                        with open(_helper.ensureDirExists(_helper.logLabelsFilename(dataset, labelset), True), 'at') as dfile:
                            dfile.write(json.dumps(data) + '\n')

                    with open(_helper.ensureDirExists(_helper.latestLabelsFilename(dataset, labelset), True), 'wt') as dfile:
                        dfile.write(json.dumps(data) + '\n')

                    with open(_helper.ensureDirExists(_helper.latestLabelsFilename(dataset, labelset), True), 'rt') as dfile:
                        response = json.loads(dfile.read())

                    self._send_header(200, SignaserverHandler.CTYPE_PLAIN)
                    self._send_data(json.dumps(response), False)

                else:
                    self._send_header(404, SignaserverHandler.CTYPE_PLAIN)

            else:
                self._send_header(404, SignaserverHandler.CTYPE_PLAIN)

        elif path == '/log':
            if not SignaserverHandler._disable_logging:
                if 'data' in vars:
                    with open(_helper.ensureDirExists(_folder.data_abspath('playlog'), True), 'at') as dfile:
                        dfile.write(vars['data'] + '\n')

            self._send_header(200, SignaserverHandler.CTYPE_PLAIN)

        elif self._is_static_file(path, vars, 'static'):
            self._send_static_file(path, vars, 'static')

        else:
            self._process_request_extension(path, vars)

    def _extractvars(self, vars):
        newvars = {}
        for key, val in vars.items():
            usekey = key
            if type(usekey) != type(''):
                usekey = usekey.decode('utf-8')

            useval = val[0]
            if type(useval) != type(''):
                useval = useval.decode('utf-8')

            newvars[usekey] = useval

        return newvars

    def do_HEAD(self):
        self._send_header(200, SignaserverHandler.CTYPE_PLAIN)

    def do_GET(self):
        parse = urllib.parse.urlparse(self.path)
        path = parse.path

        # process GET arguments
        getvars = urllib.parse.parse_qs(parse.query)

        self._process_request(path, self._extractvars(getvars))

    def do_POST(self):
        parse = urllib.parse.urlparse(self.path)
        path = parse.path

        # process POST data into dict
        postvars = {}
        if 'content-type' in self.headers:
            content_type_header = self.headers['content-type']
            ctype, pdict = cgi.parse_header(content_type_header)
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                if 'content-length' in self.headers:
                    length = int(self.headers['content-length'])
                else:
                    length = 0
                postvars = urllib.parse.parse_qs(self.rfile.read(length), keep_blank_values=1)

        self._process_request(path, self._extractvars(postvars))
