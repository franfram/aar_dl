// The webgl rendering context and the main canvas
let G_glCanvas = null;
let G_glCtx = null;
let G_canvasWidth = null;
let G_canvasHeight = null;

// The 2D rendering context and the canvas over the main canvas
let G_overCtx = null;
let G_overCanvas = null;
let G_overCtxOffscreen = null;
let G_overCanvasOffscreen = null;

// The 2D rendering context and the canvas under the main canvas
let G_underCtx = null;
let G_underCanvas = null;
let G_underCtxOffscreen = null;
let G_underCanvasOffscreen = null;

// Shader information
let G_programInfo = null;
let G_uGlobalColor = null;
let G_uOffset = null;
let G_uScale = null;

// The current dataset, labelset, and run
let G_dataset = null;
let G_labelset = null;
let G_run = null;

// The buffer used by quads
let G_quadBuffer = null;

// Information about a tile of data's state
let G_tileData = null;
let G_imageData = null;

// G_labelset but specifically for labels
let G_sessLabelId = null;

// Whether some elements are currently being fetched
let G_fetchingLabels = false;
let G_fetchingLabelsLocal = false;
let G_fetchingConfig = false;

// Constant variables to track who is creating the labels
const SOURCE_PLAYER = 'Player';
const SOURCE_ALGO = 'Algo';
const SOURCE_NOTES = 'Notes';
const SOURCE_GROUND_TRUTH = 'Truth';

let G_source = SOURCE_PLAYER;

// sensor types
const SENSOR_TYPE_DATA = 'data';
const SENSOR_TYPE_IMAGE = 'image';

// TODO: get aspect ratio from channel
const IMAGE_HEIGHT = 32;
const IMAGE_ASPECT = 16./9.;



// show or hide UI elements
let G_showImportDataElements = true;
let G_showAdvancedElements = true;

// should ground truth be drawn?
let G_drawGroundTruth = false;

// sources to be fetched from server; if null, fetch all, otherwise, show those in the set
let G_sourcesToFetch = null;



// extension callbacks
let extension_getDefaultDataset = null;
let extension_onSetup = null;
let extension_onDraw = null;
let extension_onUpdateLabelsLocal = null;

// the following line will be relaced by extension config customizations, if any
{{EXTENSION-JS-SCRIPT}}



// Array of labels made by the player
let G_labelsLocalOld = [];
let G_labelsLocal = [];

// Array of labels from the server
let G_labelsRemoteYours = null;
let G_labelsRemoteOtherPlayer = [];
let G_labelsRemoteAlgo = [];
let G_labelsRemoteNotes = [];
let G_labelsRemoteGroundTruth = null;

// Array of names of all labelsets
let G_labelsets = [];

// Label cycle information
const MAX_REMOTE_LABEL_DISPLAY = 5; // max number of remote labelsets to display
const MAX_REMOTE_LABEL_ALGO_DISPLAY = MAX_REMOTE_LABEL_DISPLAY; // max number of remote labelsets that are algo to display
let G_labelsRemoteStartIndexPlayer = 0;
let G_labelsRemoteStartIndexAlgo = 0;

// The colors of each type
let G_sensorColors = null;
let G_channelColors = null;
let G_labelColors = null;

// The height and y position of the plot
let G_plotHeight = null;
let G_plotY = null;

// Mouse state variables
let G_mousePos = null;
let G_mouseDown = false;
let G_mouseMoved = false;
let G_mouseAction = null;
let G_mouseAdjust = null;

const MOUSE_CREATE_LABEL = "MOUSE_CREATE_LABEL";
const MOUSE_ADJUST_LABEL = "MOUSE_ADJUST_LABEL";
const MOUSE_PAN = "MOUSE_PAN";
const MOUSE_COPY_LABEL = "MOUSE_COPY_LABEL";
const MOUSE_COPY_LABEL_COMPLETE = "MOUSE_COPY_LABEL_COMPLETE";

// Keyboard state tracking
var G_shiftDown = false;
var G_controlDown = false;
var G_metaDown = false;
var G_altDown = false;
var G_slowPanZoomDown = false;
var G_pleftDown = false;
var G_prightDown = false;
var G_zoutDown = false;
var G_zinDown = false;

// range scaling
let G_rangeScaling = null; // current range scaling
const RANGE_SCALING_RANGE = 4; // maximum amount of change to range scaling allowed
let G_rangeInfo = null; // information about range given current scaling

// The cache max for the G_tileData map.
let G_cacheMax = 500;

// dataset configuration as downloaded for this dataset
// Should contain a definition for
//  - tile_size: the number of data points in a tile
//  - tile_subsample: the coefficient between zoom levels
//  - zoom_max: the maximum zoom level
//  - length: the total number of raw points in this dataset
//  - start_time_ms: the time data starts at, in milliseconds
//  - sample_rate: the Hertz the data is sampled at
//  - sensors: array of sensor information
//  - channels: the name and color of channels in this dataset
//  - labels: the name and color of labels in this dataset
let G_config = null;

// Tooltip information when hovering over a small gap indicator
const TT_SUMMARY_WITH_GAP = "Labels summarized, including gaps";
const TT_SUMMARY_WITHOUT_GAP = "Labels summarized";
const TT_DELAY_CHANNEL = 1000;
const TT_DELAY_SUMMARY = 0;
let G_tooltipInfo = null;
let G_tooltipDelayFromTime = 0;

// Colors for various elements
const COLOR_UNKNOWN     = [0.45, 0.45, 0.45];
const COLOR_SMALL_LABEL = [0.30, 0.30, 0.40];
const COLOR_SMALL_GAP   = [0.50, 0.30, 0.30];

const COLOR_TIMELINE    = [0.20, 0.20, 0.20];
const COLOR_TIMELINE_TEXT  = [0.47, 0.47, 0.47];
const COLORH_TIMELINE_TEXT = "#bbbbbb";
const COLORH_DURATION_TEXT = "#FFFF00"
const COLOR_TOOLTIP = "#555";

const COLOR_CANVAS_BACKGROUND = [0.0, 0.0, 0.0];

const FETCH_STATUS_PENDING   = "pending";
const FETCH_STATUS_ERROR     = "error";
const FETCH_STATUS_READY     = "ready";

const TILE_BUFFER_CONTIGUOUS = "contiguous";
const TILE_BUFFER_GAPS       = "gaps";

const LIGHT_MODE_COLOR_MAP = {
    border: [0.905, 0.905, 0.905],
    background: [0.900, 0.900, 0.900],
    midnight: [0.750, 0.750, 0.750],
    rangeAxis: [0.0, 0.0, 0.0],
    rangeAxisText: "#000000",
    xaxis: [0.5, 0.5, 0.5]
};

const DARK_MODE_COLOR_MAP = {
    border: [0.025, 0.025, 0.025],
    background: [0.050, 0.050, 0.050],
    midnight: [0.200, 0.200, 0.200],
    rangeAxis: [1.0, 1.0, 1.0],
    rangeAxisText: "#ffffff",
    xaxis: [0.5, 0.5, 0.5]
};

let G_modeColorMap = null;

// Saves the position from which the double click zoom-in happened.
let G_zoomInHistory = null;

// Defaults and constants
var ZOOM_INT_MAX_LEVEL = 99;
var XPAN_AMOUNT = 40;

var DEFAULT_ZOOM = null;
var DEFAULT_ZOOM_INTERMEDIATE = null;

var DEFAULT_XSCALE = null;

// Zoom/pan information
var G_zoomUI = null;
var G_zoomWheel = null;
var G_zoomLevel = null;
var G_zoomLevelIntermediate = null;

// The offset and scale of the x axis of the plot
var G_xOffset = null;
var G_xScale = null;

// Timeout for the most recent call to updateUrlParameters
var G_urlUpdateTimeout = null;

// Map for key events (in uppercase) and their actions
var G_keyMap = new Map();
G_keyMap.set("PAN_LEFT", ["ARROWLEFT", "A"]);
G_keyMap.set("PAN_RIGHT", ["ARROWRIGHT", "D"]);
G_keyMap.set("ZOOM_IN", ["ARROWUP", "W"]);
G_keyMap.set("ZOOM_OUT", ["ARROWDOWN", "S"]);
G_keyMap.set("PREVIOUS_LABEL", [","]);
G_keyMap.set("NEXT_LABEL", ["."]);
G_keyMap.set("CYCLE", ["C"]);
G_keyMap.set("DOUBLE_RANGE", ["J"]);
G_keyMap.set("RESET_RANGE", ["K"]);
G_keyMap.set("HALVE_RANGE", ["L"]);
G_keyMap.set("RETURN_BACK", ["B"]);

const KEY_SLOW_PANZOOM = ["`", "/"];

const TINY_SIZE = 0.001;
const REALLY_TINY_SIZE = 0.00025;

const TIMELINE_HEIGHT = 0.05;

const LABEL_HEIGHT = 0.04;
const LABEL_GAP = 0.005;
const LABEL_INDICATOR = 0.01;
const LABEL_INDICATOR_OVERHANG = 0.001;

const NAME_OFFSET = 0.01;
const NAME_WIDTH = 0.08;
const TEXT_INSET = 0.004;

const RANGE_AXIS_POS = NAME_WIDTH + NAME_OFFSET - REALLY_TINY_SIZE;
const RANGE_AXIS_TICK = 0.01;
const X_OFFSET = RANGE_AXIS_POS + 0.001;

const IS_FIREFOX = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;

const WEEKDAY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

let G_startDate = null;
let G_startDayIdx = null;

window.addEventListener('load', startup, false);

const VS_SOURCE = `
    uniform vec2 uOffset;
    uniform vec2 uScale;
    attribute vec2 aVertexPosition;
    void main() {
        gl_Position = vec4(((uOffset + uScale * aVertexPosition) - 0.5) * 2.0, 0.0, 1.0);
    }
`;

const FS_SOURCE = `
    #ifdef GL_ES
        precision highp float;
    #endif
    uniform vec4 uGlobalColor;
    void main() {
        gl_FragColor = uGlobalColor;
    }
`;

function getXScale() {
    return DEFAULT_XSCALE * Math.pow(Math.pow(G_config.tile_subsample, 1.0 / (ZOOM_INT_MAX_LEVEL + 1)), (ZOOM_INT_MAX_LEVEL - G_zoomLevelIntermediate) + 1);
}

function invertXScaleIntermediate(xScale) {
    return Math.round(0.5 + -1 * Math.log(xScale) / Math.log(Math.pow(G_config.tile_subsample, 1.0 / (ZOOM_INT_MAX_LEVEL + 1))) + ZOOM_INT_MAX_LEVEL + 1);
}

// Handle blur of window
function blurHandler(evt) {
    clearMouse();
    clearKeys();
}

// Handle when the mouse button is down
function mouseDownHandler(evt) {
    if (evt.target !== G_glCanvas) {
        // ignore events here that are not for the canvas (for example, the Channel checkboxes)
        return;
    }

    evt.preventDefault();

    if (G_fetchingLabelsLocal || G_fetchingConfig) {
        return;
    }

    var mpos = getWorldMousePos(evt, G_glCanvas);
    var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);

    if (mpos.x <= 0 || 1 <= mpos.x || mpos.y <= 0 || 1 <= mpos.y) {
        return;
    }

    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    G_mouseDown = smpx * zoom;
    G_mouseMoved = false;
    if (G_mouseAdjust) {
        G_mouseAction = MOUSE_ADJUST_LABEL;
    } else if (G_plotY[0] - G_plotHeight / 2 < mpos.y && mpos.y < G_plotY[0] + G_plotHeight / 2) {
        // mouse down on plot
        if (evt.which !== 1 || G_controlDown || G_metaDown) {
            // right/middle down or ctrl/cmd held
            G_mouseAction = MOUSE_CREATE_LABEL;
        } else {
            G_mouseAction = MOUSE_PAN;
        }
    } else if (G_plotY[0] - G_plotHeight / 2 - TIMELINE_HEIGHT < mpos.y && mpos.y < G_plotY[0] - G_plotHeight / 2) {
        // mouse down on timeline
        G_mouseAction = MOUSE_CREATE_LABEL;
    } else {
        if (evt.which !== 1 || G_controlDown || G_metaDown) {
            G_mouseAction = MOUSE_COPY_LABEL;
        } else {
            G_mouseAction = null;
        }
    }
}

// find the time difference
function durationStringFromSamples(samples) {
    var millisecondsDifference = 1000 * (samples / G_config.sample_rate);

    if (millisecondsDifference >= 1000 * 60 * 60 * 24) {
        return (millisecondsDifference / (1000 * 60 * 60 * 24)).toFixed(2) + ' d';
    } else if (millisecondsDifference >= 1000 * 60 * 60) {
        return (millisecondsDifference / (1000 * 60 * 60)).toFixed(1) + ' h';
    } else if (millisecondsDifference >= 1000 * 60) {
        return (millisecondsDifference / (1000 * 60)).toFixed(1) + ' m';
    } else if (millisecondsDifference >= 1000) {
        return (millisecondsDifference / (1000)).toFixed(1) + ' s';
    } else if (millisecondsDifference >= 0) {
        return (millisecondsDifference).toFixed(0) + ' ms';
    } else {
        return '';
    }
}

// Handle when the mouse moves
function mouseMoveHandler(evt) {
    var mpos = getWorldMousePos(evt, G_glCanvas);
    var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);

    if (G_mouseAction === MOUSE_PAN) {
        var dx = mpos.x - G_mousePos.x;
        setAndClampXOffset(G_xOffset + (dx / G_xScale));
    }

    G_mousePos = mpos;
    if (G_mouseDown !== false) {
        var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
        G_mouseMoved = smpx * zoom;
    } else {
        checkMouseOnLabelEdge();
    }
}

function sortLabels(labels) {
    labels.sort(function(a, b){return a.lo - b.lo});
}

function setCurrentLabel(label) {
    var radioButtons = document.getElementsByName("addlabel");
    for (var ii = 0; ii < radioButtons.length; ++ ii) {
        if (radioButtons[ii].id === "addlabel" + label) {
            radioButtons[ii].click();
            return;
        }
    }
}

function nextCurrentLabel() {
    var radioButtons = document.getElementsByName("addlabel");
    for (var ii = 0; ii < radioButtons.length; ++ ii) {
        if (radioButtons[ii].checked) {
            radioButtons[(ii + 1) % radioButtons.length].click();
            return;
        }
    }
}

function prevCurrentLabel() {
    var radioButtons = document.getElementsByName("addlabel");
    for (var ii = 0; ii < radioButtons.length; ++ ii) {
        if (radioButtons[ii].checked) {
            radioButtons[(ii + (radioButtons.length - 1)) % radioButtons.length].click();
            return;
        }
    }
}

function getCurrentLabel() {
    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        if (document.getElementById('addlabel' + label.lname).checked) {
            return label.lname;
        }
    }
    return "ERASE";
}

function undoRedoLabel() {
    updateLabelsLocal(true, G_labelsLocalOld);
    sendLog('label', {"labels":G_labelsLocal})
}

function updateLabelsLocal(andSend, newLabelsLocal) {
    var tmp = G_labelsLocal;
    G_labelsLocal = newLabelsLocal;
    G_labelsLocalOld = tmp;

    if (extension_onUpdateLabelsLocal !== null) {
        extension_onUpdateLabelsLocal();
    }

    if (andSend) {
        sendLabels();
    }
}

function cycleServerLabels() {
    G_labelsRemoteStartIndexAlgo = G_labelsRemoteAlgo.length ? ((G_labelsRemoteStartIndexAlgo + 1) % G_labelsRemoteAlgo.length) : 0;
    G_labelsRemoteStartIndexPlayer = G_labelsRemoteOtherPlayer.length ? ((G_labelsRemoteStartIndexPlayer + 1) % G_labelsRemoteOtherPlayer.length) : 0;
    updateUrlParameters();
}

function showAllSensors() {
    var checkboxes = document.getElementsByName('showsensor');
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        checkboxes[ii].checked = true;
    }
}

function toggleSensorVisibility(index) {
    var checkboxes = document.getElementsByName('showsensor');
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        if (ii === index) {
            checkboxes[ii].click();
        }
    }
}

function isSensorVisible(name) {
    if (G_config.sensors.length > 1) {
        if (!document.getElementById('showsensor' + name).checked) {
            return false;
        }
    }

    return true;
}

function isChannelVisible(name) {
    if (!document.getElementById('showchannel' + name).checked) {
        return false;
    }

    return true;
}

function showAllLabels() {
    var checkboxes = document.getElementsByName("showlabel");
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        checkboxes[ii].checked = true;
    }
}

function hideAllLabels() {
    var checkboxes = document.getElementsByName("showlabel");
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        checkboxes[ii].checked = false;
    }
}

function getVisibleLabels() {
    var visibleLabels = [];
    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        if (document.getElementById('showlabel' + label.lname).checked) {
            visibleLabels[label.lname] = true;
        }
    }
    if (document.getElementById('showlabelOTHER').checked) {
        visibleLabels['OTHER'] = true;
    }
    return visibleLabels;
}

function getPendingLabels() {
    var pendingLabels = [];
    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        if (G_mouseDown !== false && G_mouseMoved !== false) {
            pendingLabels.push({
                lo: Math.min(G_mouseDown, G_mouseMoved),
                hi: Math.max(G_mouseDown, G_mouseMoved),
                lname: getCurrentLabel()
            });
        }
    } else if (G_mouseAction === MOUSE_ADJUST_LABEL) {
        if (G_mouseDown !== false && G_mouseMoved !== false && G_mouseAdjust !== null) {
            if (G_mouseAdjust.left !== null) {
                if (G_mouseMoved > G_mouseAdjust.left.lo) {
                    pendingLabels.push({
                        lo: G_mouseAdjust.left.lo,
                        hi: G_mouseMoved,
                        lname: G_mouseAdjust.left.lname,
                        detail: G_mouseAdjust.left.detail
                    });
                }
            } else {
                if (G_mouseMoved > G_mouseAdjust.right.lo) {
                    pendingLabels.push({
                        lo: G_mouseAdjust.right.lo,
                        hi: G_mouseMoved,
                        lname: 'ERASE'
                    });
                }
            }
            if (G_mouseAdjust.right !== null) {
                if (G_mouseMoved < G_mouseAdjust.right.hi) {
                    pendingLabels.push({
                        lo: G_mouseMoved,
                        hi: G_mouseAdjust.right.hi,
                        lname: G_mouseAdjust.right.lname,
                        detail: G_mouseAdjust.right.detail
                    });
                }
            } else {
                if (G_mouseMoved < G_mouseAdjust.left.hi) {
                    pendingLabels.push({
                        lo: G_mouseMoved,
                        hi: G_mouseAdjust.left.hi,
                        lname: 'ERASE'
                    });
                }
            }
        }
    }
    return pendingLabels;
}

function updateColorMode() {
    G_modeColorMap = isDarkMode() ? DARK_MODE_COLOR_MAP : LIGHT_MODE_COLOR_MAP;
}

function isDarkMode() {
    return document.getElementById("darkmode").checked;
}

function isTileDebugging() {
    return document.getElementById("tiledebug").checked;
}

function maxZoom() {
    if (G_zoomLevel === 0 && G_zoomLevelIntermediate === 0) {
        zoomTo(true, G_config.zoom_max, ZOOM_INT_MAX_LEVEL);
    } else {
        zoomTo(true, 0, 0);
    }
}

function getRangeUnitOfVisibleSensors() {
    var unit = null;
    for (var ss = G_config.sensors.length - 1; ss >= 0; --ss) {
        if (G_config.sensors[ss].stype != SENSOR_TYPE_DATA) {
            continue;
        }

        if (isSensorVisible(G_config.sensors[ss].sname)) {
            if (unit === null || unit === G_config.sensors[ss].range_unit) {
                unit = G_config.sensors[ss].range_unit
            } else {
                return null;
            }
        }
    }
    return unit;
}

function getRangeSpanOfVisibleSensors() {
    var rangeMins = []
    var rangeMaxs = []
    var result = G_config.range_span;
    for (var ss = G_config.sensors.length - 1; ss >= 0; --ss) {
        if (isSensorVisible(G_config.sensors[ss].sname)) {
            rangeMins.push(G_config.sensors[ss].range_span[0])
            rangeMaxs.push(G_config.sensors[ss].range_span[1])
        }
    }
    if (rangeMins.length > 0 && rangeMaxs.length > 0) {
        result = Math.ceil(Math.max(Math.abs(Math.min(...rangeMins)), Math.abs(Math.max(...rangeMaxs))) * 1.1)
        result = [-result, result] // for now, we will tempararily use symmetric range
    }
    return result
}

// Functions to change the scaling on the range axis
function updateRangeInfo() {
    var rmin = Math.pow(2, G_rangeScaling);
    var rmax = Math.pow(2, G_rangeScaling);
    if (getUseSensorRanges()) {
        var sensorRange = getRangeSpanOfVisibleSensors();
        rmin *= sensorRange[0];
        rmax *= sensorRange[1];
    } else {
        rmin *= G_config.range_span[0];
        rmax *= G_config.range_span[1];
    }

    var rmid = 0.5 * (rmax + rmin);
    var rdiff = rmax - rmin;
    var plotOffset = -rmid / 4 / (rdiff / 2);
    var plotScale = 1.0 / (rdiff / 2);
    var unit = getRangeUnitOfVisibleSensors();

    G_rangeInfo = { rmin: rmin, rmax: rmax, plotOffset: plotOffset, plotScale: plotScale, unit: unit };
}

function increaseRangeScaling() {
    if (G_rangeScaling < RANGE_SCALING_RANGE) {
        G_rangeScaling += 1;
        updateRangeInfo();
    }
}

function decreaseRangeScaling() {
    if (G_rangeScaling > -RANGE_SCALING_RANGE) {
        G_rangeScaling -= 1;
        updateRangeInfo();
    }
}

function resetRangeScaling() {
    if (G_rangeScaling != 0) {
        G_rangeScaling = 0;
        updateRangeInfo();
    }
}

function addLabels(newLabels) {
    var labelsLocalNew = G_labelsLocal;

    for (var pl = 0; pl < newLabels.length; ++ pl) {
        const lbl = newLabels[pl];

        updated = true;

        var lo = lbl.lo;
        var hi = lbl.hi;
        var labelname = lbl.lname;

        if (labelname !== 'ERASE') {
            lo = Math.max(0, Math.min(G_config.length, lo));
            hi = Math.max(0, Math.min(G_config.length, hi));
            var showLabelElem = document.getElementById("showlabel" + labelname);
            if (showLabelElem) {
                showLabelElem.checked = true;
            }
        }

        // Only add non overlapping labels to the new list of labels, cutting off overlapping ends if necessary
        if (lo !== hi) {
            var newLocal = [];
            for (var ll = 0; ll < labelsLocalNew.length; ++ ll) {
                var label = labelsLocalNew[ll];
                if (label.hi <= lo) {
                    newLocal.push(label);
                } else if (label.lo >= hi) {
                    newLocal.push(label);
                } else if (label.lo >= lo && label.hi <= hi) {
                } else if (label.lo < lo && label.hi <= hi) {
                    newLocal.push({lo: label.lo, hi: lo, lname: label.lname, detail: label.detail});
                } else if (label.lo >= lo && label.hi > hi) {
                    newLocal.push({lo: hi, hi: label.hi, lname: label.lname, detail: label.detail});
                } else if (label.lo < lo && label.hi > hi) {
                    newLocal.push({lo: label.lo, hi: lo, lname: label.lname, detail: label.detail});
                    newLocal.push({lo: hi, hi: label.hi, lname: label.lname, detail: label.detail});
                }
            }
            labelsLocalNew = newLocal;

            // Add the new label
            if (labelname !== 'ERASE') {
                labelsLocalNew.push({lo: lo, hi: hi, lname: labelname, detail: lbl.detail});
            }
            sortLabels(labelsLocalNew);

            // Merge labels with the new one
            var anyMerged = true;
            while (anyMerged) {
                anyMerged = false;
                var newLocal = [];
                for (var ll = 0; ll < labelsLocalNew.length; ++ ll) {
                    if (ll + 1 === labelsLocalNew.length) {
                        var label = labelsLocalNew[ll];
                        newLocal.push(label);
                    } else {
                        var label0 = labelsLocalNew[ll + 0];
                        var label1 = labelsLocalNew[ll + 1];
                        if (label0.hi === label1.lo && label0.lname === label1.lname && label0.detail === label1.detail) {
                            newLocal.push({lo: label0.lo, hi: label1.hi, lname: label0.lname, detail: label0.detail});
                            ++ ll;
                            anyMerged = true;
                        } else {
                            newLocal.push(label0);
                        }
                    }
                }
                labelsLocalNew = newLocal;
            }
        }
    }

    updateLabelsLocal(true, labelsLocalNew);
}

// Handle when the mouse button is released after being held and moved
// Create new labels and merge/overwrite the old labels when necessary
function mouseUpHandler(evt) {
    G_zoomUI = null;
    var pendingLabels = getPendingLabels();
    if (pendingLabels.length > 0) {
        addLabels(pendingLabels);
        sendLog('label', {"labels":G_labelsLocal})
    }

    clearMouse();
    checkMouseOnLabelEdge();
}

function mouseWheelHandler(evt) {
    G_zoomUI = null;
    if (evt.deltaY < 0) {
        G_zoomWheel = "zin";
    } else {
        G_zoomWheel = "zout";
    }
    evt.preventDefault();
}

function mouseDoubleHandler(evt) {
    if (G_mouseAdjust !== null) {
        if (G_mouseAdjust.left !== null && G_mouseAdjust.right === null) {
            var newLabel = {
                lo: G_mouseAdjust.left.hi,
                hi: (G_mouseAdjust.left.index + 1 < G_labelsLocal.length) ? G_labelsLocal[G_mouseAdjust.left.index + 1].lo : G_config.length,
                lname: G_mouseAdjust.left.lname,
                detail: G_mouseAdjust.left.detail
            }
            addLabels([newLabel]);
        } else if (G_mouseAdjust.left === null && G_mouseAdjust.right !== null) {
            var newLabel = {
                lo: (G_mouseAdjust.right.index > 0) ? G_labelsLocal[G_mouseAdjust.right.index - 1].hi : 0,
                hi: G_mouseAdjust.right.lo,
                lname: G_mouseAdjust.right.lname,
                detail: G_mouseAdjust.right.detail
            }
            addLabels([newLabel]);
        }
    } else if (G_mousePos && G_plotY[0] - G_plotHeight / 2 < G_mousePos.y && G_mousePos.y < G_plotY[0] + G_plotHeight / 2) {
        if (G_zoomLevel === 0 && G_zoomLevelIntermediate === 0) {
            zoomTo(true, G_config.zoom_max, ZOOM_INT_MAX_LEVEL);
        } else {
            setZoomHistory();
            zoomTo(true, 0, 0);
        }
    }
    evt.preventDefault();
}

// Zoom by a given intermediate delta
function zoomDelta(useMouse, di) {
    var zoom = G_zoomLevel;
    var zoomIntermediate = G_zoomLevelIntermediate;

    zoomIntermediate += di;

    while (zoomIntermediate < 0) {
        if (zoom > 0) {
            zoom -= 1;
            zoomIntermediate += (ZOOM_INT_MAX_LEVEL + 1);
        } else {
            zoomIntermediate = 0;
        }
    }
    while (zoomIntermediate > ZOOM_INT_MAX_LEVEL) {
        if (zoom < G_config.zoom_max) {
            zoom += 1;
            zoomIntermediate -= (ZOOM_INT_MAX_LEVEL + 1);
        } else {
            zoomIntermediate = ZOOM_INT_MAX_LEVEL;
        }
    }

    zoomTo(useMouse, zoom, zoomIntermediate);
}

// Zoom to a given zoom level
function zoomTo(useMouse, zoom, zoomIntermediate) {
    if (G_zoomLevel === zoom && G_zoomLevelIntermediate === zoomIntermediate) {
        return;
    }

    var changedLevel = G_zoomLevel - zoom;

    G_zoomLevel = clamp(zoom, 0, G_config.zoom_max);
    G_zoomLevelIntermediate = clamp(zoomIntermediate, 0, ZOOM_INT_MAX_LEVEL);

    var oldXS = G_xScale;
    var newXS = getXScale();

    var factor = Math.pow(G_config.tile_subsample, changedLevel);

    var midsmp = (0.5 - X_OFFSET) / oldXS - G_xOffset;
    if (useMouse && G_mousePos) {
        midsmp = (G_mousePos.x - X_OFFSET) / oldXS - G_xOffset;
    }

    G_xScale = newXS;

    var dx = (((midsmp * oldXS) - (midsmp * newXS * factor)));
    setAndClampXOffset((G_xOffset * oldXS + dx) / newXS);
}

// Handle zooming in on the plot
function zinHandler(useMouse) {
    if (G_mouseDown !== false) {
        return;
    }

    // Increment intermediate zoom level and main zoom level if necessary
    var speed =  G_shiftDown ? 20 : (G_slowPanZoomDown ? 1 : 10);

    zoomDelta(useMouse, -speed);
}

// Handle zooming out on the plot
function zoutHandler(useMouse) {
    if (G_mouseDown !== false) {
        return;
    }

    // Increment intermediate zoom level and main zoom level if necessary
    var speed =  G_shiftDown ? 20 : (G_slowPanZoomDown ? 1 : 10);

    zoomDelta(useMouse, speed);
}

// Function to update the URL when zoom or pan change
// Updates are limited to once every 0.5 seconds
function updateUrlParameters(){
    updateMessageDisplay();

    if (G_urlUpdateTimeout === null) {
        // set timeout to update url parameter later if needed
        G_urlUpdateTimeout = setTimeout(function() {
            var searchParams = new URLSearchParams(G_urlBaseParam);
            searchParams.set("zoom", G_zoomLevel);
            searchParams.set("zoomi", G_zoomLevelIntermediate);
            searchParams.set("offset", Math.round(G_xOffset));
            searchParams.set("iplayer", Math.round(G_labelsRemoteStartIndexPlayer));
            searchParams.set("ialgo", Math.round(G_labelsRemoteStartIndexAlgo));
            history.replaceState(history.state, 'Signaligner', window.location.pathname + '?' + searchParams.toString());
            G_urlUpdateTimeout = null;
        }, 500);
    }
}

// Handle panning left on the plot
function pleftHandler() {
    var speed = (G_shiftDown ? 2.0 : (G_slowPanZoomDown ? 0.1 : 1.0));
    setAndClampXOffset(G_xOffset + speed * XPAN_AMOUNT / (G_xScale / DEFAULT_XSCALE));

    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        var mpos = G_mousePos;
        var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);
        var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
        G_mouseMoved = smpx * zoom;
    }
}

// Handle panning right on the plot
function prightHandler() {
    var speed = (G_shiftDown ? 2.0 : (G_slowPanZoomDown ? 0.1 : 1.0));
    setAndClampXOffset(G_xOffset - speed * XPAN_AMOUNT / (G_xScale / DEFAULT_XSCALE));

    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        var mpos = G_mousePos;
        var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);
        var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
        G_mouseMoved = smpx * zoom;
    }
}

// Update G_xOffset and keep the things in the window
function setAndClampXOffset(newXOffset) {
    G_xOffset = newXOffset;

    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
    G_xOffset = Math.max(G_xOffset, -(G_config.length / zoom) + (0.1 - X_OFFSET) / G_xScale);
    G_xOffset = Math.min(G_xOffset, (0.9 - X_OFFSET) / G_xScale);

    updateUrlParameters();
}

// Reset the zoom and position of the plot
function resetHandler() {
    if (G_mouseDown) {
        return;
    }

    resetRangeScaling();
    G_zoomLevel = DEFAULT_ZOOM;
    G_zoomLevelIntermediate = DEFAULT_ZOOM_INTERMEDIATE;
    G_xScale = getXScale();
    setAndClampXOffset(0);
}

// Handle when the "updatebutton" is clicked
function clickUpdateHandler() {
    sendLabels();
    fetchLabels(false);
}

function createLabelSetHandler() {
    const newLabelset = document.getElementById('newlabelset').value;
    const regex = /^([a-zA-Z0-9_]){3,15}$/;

    if (regex.test(newLabelset) === false) {
        alert('Please enter alphanumeric characters between 3 and 15 chars. ');
    } else {
        if (G_labelsets.includes(newLabelset)) {
            alert('The labelset already exists. Select from dropdown.');
        }
        else {
            loadDataset(G_dataset, newLabelset)
        }
    }
}

// Restore mouse to standard "up" state
function clearMouse() {
    G_mousePos = G_mousePos; // keep mouse pos
    G_mouseDown = false;
    G_mouseMoved = false;
    G_mouseAction = null;
    G_mouseAdjust = null;
}

// Restore all keys to standard "up" state
function clearKeys() {
    G_shiftDown = false;
    G_controlDown = false;
    G_metaDown = false;
    G_altDown = false;
    G_slowPanZoomDown = false;
    G_pleftDown = false;
    G_prightDown = false;
    G_zinDown = false;
    G_zoutDown = false;
}

// Handle when any key is pressed down
function keydownHandler(evt) {
    var keyUpper = evt.key.toUpperCase();

    if (keyUpper === "SHIFT") {
        G_shiftDown = true;
        evt.preventDefault();
        return;
    } else if (keyUpper === "CONTROL") {
        G_controlDown = true;
        evt.preventDefault();
        return;
    } else if (keyUpper === "META") {
        G_metaDown = true;
        evt.preventDefault();
        return;
    } else if (keyUpper === "ALT") {
        G_altDown = true;
        evt.preventDefault();
        return;
    } else if (KEY_SLOW_PANZOOM.includes(keyUpper)) {
        G_slowPanZoomDown = true;
        return;
    }

    if (keyUpper === "ESCAPE") {
        document.activeElement.blur();
        clearMouse();
        clearKeys();
        return;
    }

    if (document.activeElement !== document.body) {
        // something else has the focus
        return;
    }

    // undo
    if (keyUpper === "Z" && (G_controlDown || G_metaDown)) {
        undoRedoLabel();
        return;
    }

    // skip the rest of the key handlers if certain modifiers are down
    if (!G_controlDown && !G_metaDown && !G_altDown) {
        // since no modifier is pressed, it is safe to call the preventDefault method here
        event.preventDefault();

        // pan and zoom based on keyboard input when the main window is in focus
        if (G_keyMap.get("PAN_LEFT").includes(keyUpper)) {
            G_pleftDown = true;
        } else if (G_keyMap.get("PAN_RIGHT").includes(keyUpper)) {
            G_prightDown = true;
        } else if (G_keyMap.get("ZOOM_IN").includes(keyUpper)) {
            G_zinDown = true;
        } else if (G_keyMap.get("ZOOM_OUT").includes(keyUpper)) {
            G_zoutDown = true;
        }

        // toggle between previous/next label options
        if (G_keyMap.get("PREVIOUS_LABEL").includes(keyUpper)) {
            prevCurrentLabel();
        } else if (G_keyMap.get("NEXT_LABEL").includes(keyUpper)) {
            nextCurrentLabel();
        }

        // change label range
        else if (G_keyMap.get("CYCLE").includes(keyUpper)) {
            cycleServerLabels();
        }
        // Increase range-axis magnitude
        else if (G_keyMap.get("DOUBLE_RANGE").includes(keyUpper)) {
            increaseRangeScaling();
        }
        // Increase range-axis magnitude
        else if (G_keyMap.get("RESET_RANGE").includes(keyUpper)) {
            resetRangeScaling();
        }
        // Decrease range-axis magnitude
        else if (G_keyMap.get("HALVE_RANGE").includes(keyUpper)) {
            decreaseRangeScaling();
        }
        else if (keyUpper === " ") {
            resetHandler();
            evt.preventDefault();
        }
        else if (G_keyMap.get("RETURN_BACK").includes(keyUpper)) {
            restoreZoomHistory();
        }
        else {
            var digit = Number.parseInt(keyUpper);
            if (!isNaN(digit)) {
                if (digit === 0) {
                    showAllSensors();
                } else if (digit >= 1 && digit <= 9) {
                    toggleSensorVisibility(digit - 1);
                }
            }
        }
    }
}

// Handle when any key is released
function keyupHandler(evt) {
    var keyUpper = evt.key.toUpperCase();

    if (keyUpper === "SHIFT") {
        G_shiftDown = false;
        return;
    } else if (keyUpper === "CONTROL") {
        G_controlDown = false;
        return;
    } else if (keyUpper === "META") {
        G_metaDown = false;
        return;
    } else if (keyUpper === "ALT") {
        G_altDown = false;
        return;
    } else if (KEY_SLOW_PANZOOM.includes(keyUpper)) {
        G_slowPanZoomDown = false;
        return;
    } else if (G_keyMap.get("PAN_LEFT").includes(keyUpper)) {
        G_pleftDown = false;
        return;
    } else if (G_keyMap.get("PAN_RIGHT").includes(keyUpper)) {
        G_prightDown = false;
        return;
    } else if (G_keyMap.get("ZOOM_IN").includes(keyUpper)) {
        G_zinDown = false;
        return;
    }  if (G_keyMap.get("ZOOM_OUT").includes(keyUpper)) {
        G_zoutDown = false;
        return;
    }

}

// Saves and updates the zoom history.
function setZoomHistory() {
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
    G_zoomInHistory = {
        zoomLevel: G_zoomLevel,
        intermediateZoomLevel: G_zoomLevelIntermediate,
        xOffset: G_xOffset,
        smplo: Math.round((0.0 - X_OFFSET) / G_xScale - G_xOffset) * zoom,
        smphi: Math.round((1.0 - X_OFFSET) / G_xScale - G_xOffset) * zoom
    }
}

function restoreZoomHistory() {
    zoomTo(true, G_zoomInHistory.zoomLevel, G_zoomInHistory.intermediateZoomLevel);
    setAndClampXOffset(G_zoomInHistory.xOffset);
}

// Return the first dataset
function getDefaultDataset() {
    if (extension_getDefaultDataset !== null) {
        return extension_getDefaultDataset();
    }
    return 'test_sin30min';
}

// Initialize the program
function startup() {
    // Initialize the canvases
    G_glCanvas = document.getElementById('glcanvas');
    G_glCtx = G_glCanvas.getContext('webgl');

    G_canvasWidth = G_glCanvas.width;
    G_canvasHeight = G_glCanvas.height;

    G_overCanvas = document.getElementById('overcanvas');
    G_overCtx = G_overCanvas.getContext('2d');

    G_overCanvasOffscreen = document.createElement('canvas');
    G_overCanvasOffscreen.width = G_overCanvas.width;
    G_overCanvasOffscreen.height = G_overCanvas.height;
    G_overCtxOffscreen = G_overCanvasOffscreen.getContext('2d');

    G_underCanvas = document.getElementById('undercanvas');
    G_underCtx = G_underCanvas.getContext('2d');

    G_underCanvasOffscreen = document.createElement('canvas');
    G_underCanvasOffscreen.width = G_underCanvas.width;
    G_underCanvasOffscreen.height = G_underCanvas.height;
    G_underCtxOffscreen = G_underCanvasOffscreen.getContext('2d');

    // Set the labelset information based on the url
    var url_string = window.location.href;
    var url = new URL(url_string);
    G_dataset = url.searchParams.get("dataset");
    G_labelset = url.searchParams.get("labelset");
    G_run = makeId();

    if (!G_dataset || G_dataset.length === 0) {
        G_dataset = undefined;
    }
    if (!G_labelset || G_labelset.length === 0 || /^([a-zA-Z0-9_])+$/.test(G_labelset) === false) {
        G_labelset = undefined;
    }

    if (G_labelset === undefined || G_dataset === undefined) {
        var new_labelset = G_labelset;
        if (new_labelset === undefined) {
            new_labelset = makeId();
        }

        var new_dataset = G_dataset;
        if (new_dataset === undefined) {
            new_dataset = getDefaultDataset();
        }

        G_dataset = new_dataset;
        loadDataset(new_dataset, new_labelset);
        return;
    }

    if (extension_onSetup !== null) {
        extension_onSetup();
    }

    if (G_showAdvancedElements) {
        var advancedElements = document.getElementsByClassName('advancedbutton');
        for (let i = 0; i < advancedElements.length; i++) {
            advancedElements[i].style.display = 'table-cell';
        }
    }

    if (G_showImportDataElements) {
        importDatasetSetup();
    }

    // Initialize shader
    const shaderProgram = initShaderProgram();
    G_programInfo = {
        program: shaderProgram,
        attribLocations: {
            vertexPosition: G_glCtx.getAttribLocation(shaderProgram, 'aVertexPosition'),
        }
    };

    G_glCtx.useProgram(G_programInfo.program);
    G_uGlobalColor = G_glCtx.getUniformLocation(G_programInfo.program, "uGlobalColor");
    G_uOffset = G_glCtx.getUniformLocation(G_programInfo.program, "uOffset");
    G_uScale = G_glCtx.getUniformLocation(G_programInfo.program, "uScale");

    G_plotHeight = 0.5;
    G_plotY = [0.73];

    // Initialize the scene
    G_tileData = new Map();
    G_imageData = new Map();

    // Initialize the labelset label id
    G_sessLabelId = G_labelset;

    // Initialize the color mode map
    updateColorMode();

    initQuadBuffer();

    showText('message', 'Loading...');

    sendLog('start', {});

    // Start looping functions
    setInterval(drawScene, 30);
    setInterval(logTick, 10000);
    setInterval(handleZoomUI, 50);

    // Clear state
    clearMouse();
    clearKeys();

    // Event handlers
    window.addEventListener('blur', blurHandler);

    window.addEventListener('mousedown', mouseDownHandler);
    window.addEventListener('mousemove', mouseMoveHandler);
    window.addEventListener('mouseup', mouseUpHandler);
    G_glCanvas.addEventListener('wheel', mouseWheelHandler);
    G_glCanvas.addEventListener('dblclick', mouseDoubleHandler);

    window.addEventListener('keydown', keydownHandler);
    window.addEventListener('keyup', keyupHandler);

    document.getElementById('updatebutton').addEventListener('click', clickUpdateHandler);
    document.getElementById('createlabelset').addEventListener('click', createLabelSetHandler);

    document.getElementById('zinbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "zin"; });
    document.getElementById('zinbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('zoutbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "zout"; });
    document.getElementById('zoutbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('pleftbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "pleft"; });
    document.getElementById('pleftbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('prightbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "pright"; });
    document.getElementById('prightbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('resetbutton').addEventListener('click', function(){ G_zoomUI = null; resetHandler(); });

    document.getElementById('double-range-button').addEventListener('click', function(){ increaseRangeScaling(); });
    document.getElementById('reset-range-button').addEventListener('click', function(){ resetRangeScaling(); });
    document.getElementById('halve-range-button').addEventListener('click', function(){ decreaseRangeScaling(); });

    document.getElementById('maxzoombutton').addEventListener('click', function(evt) { maxZoom(); evt.preventDefault()});

    document.getElementById('undoredobutton').addEventListener('click', undoRedoLabel);
    document.getElementById('nextlabelbutton').addEventListener('click', nextCurrentLabel);
    document.getElementById('prevlabelbutton').addEventListener('click', prevCurrentLabel);

    document.getElementById('cycleserverlabels').addEventListener('click', cycleServerLabels);

    document.getElementById('darkmode').addEventListener('change', updateColorMode);

    // fetch dataset config
    fetchConfig();

    // Reset timer for tooltip
    for (var evtName of ['mousemove', 'mousedown', 'mousewheel', 'wheel', 'touchmove', 'keypress', 'keyup', 'keydown', 'DOMMouseScroll', 'MSPointerMove']) {
        window.addEventListener(evtName, resetTooltipTimer, false);
    }
}

// Change query param to fetch new dataset data
function changeDataset(evt) {
    var allFiles = evt.target.files;
    var relativePath = allFiles[0].webkitRelativePath;
    var folderName = relativePath.split("/");
    var datasetName = folderName[0];

    var searchParams = new URLSearchParams(window.location.search);
    searchParams.set("dataset", datasetName);
    window.location.search = searchParams.toString();
}

// Get the appropriate XMLHTTP request based on the browser
function getXHR() {
    if (window.XMLHttpRequest) {
        // Chrome, Firefox, IE7+, Opera, Safari
        return new XMLHttpRequest();
    }
    // IE6
    try {
        return new ActiveXObject('MSXML2.XMLHTTP.6.0');
    } catch (e) {
        try {
            return new ActiveXObject('MSXML2.XMLHTTP.3.0');
        } catch (e) {
            try {
                return new ActiveXObject('MSXML2.XMLHTTP');
            } catch (e) {
                return null;
            }
        }
    }
}

function requestToServer(url, postData, retries, successcallback, failurecallback) {
    var xhttp = getXHR();
    if (xhttp) {
        xhttp.onreadystatechange = function() {
            if (xhttp.readyState === 4) {
                if (xhttp.status === 200) {
                    if (successcallback) {
                        successcallback(xhttp.response);
                    }
                } else {
                    // anything other than 200 is an error
                    if (retries > 0) {
                        requestToServer(url, postData, retries - 1, successcallback, failurecallback);
                    } else {
                        if (failurecallback) {
                            failurecallback();
                        }
                    }
                }
            }
        };

        if (postData) {
            var postDataStr = encodeURI(JSON.stringify(postData));
            xhttp.open("POST", url, true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhttp.send("data=" + postDataStr);
        } else {
            xhttp.open("GET", url, true);
            xhttp.send("");
        }
    }
}

function onDatasetListError() {
    showText("message", "Error: no datasets available to import.");
}

function onDatasetListSuccess(response) {
    try {
        let importDatasets = JSON.parse(response);
        updateDatasetsListDropdown(importDatasets);
    }
    catch(e) {
        showText("message", "Error parsing list of datasets");
    }
}

function updateListDropdown(name, currentOption, importOptions, changeFunc) {
    var selectElement = document.getElementById(name);

    for (var i = 0; i < importOptions.length; i++) {
        selectElement.options[selectElement.options.length] = new Option(importOptions[i], importOptions[i]);
    }
    if (!importOptions.includes(currentOption)) {
        selectElement.options[selectElement.options.length] = new Option(currentOption, currentOption);
    }

    // Assign the selected option based on the current dataset
    var selectedIndex = 0;
    for (var j = 0; j < selectElement.options.length; j++) {
        if (currentOption === selectElement.options[j].value) {
            selectedIndex = j;
        }
    }
    selectElement.selectedIndex = selectedIndex;

    // Handle when selected element changes
    selectElement.addEventListener('change', function(e) {
        changeFunc(selectElement.options[selectElement.selectedIndex].value);
        document.activeElement.blur();
    });

}

function updateDatasetsListDropdown(importDatasets) {
    updateListDropdown('datasetsdropdown', G_dataset, importDatasets, function(value) { loadDataset(value, G_labelset); });
}

function updateLabelsetsListDropdown(importLabelsets) {
    updateListDropdown('labelsetsdropdown', G_labelset, importLabelsets, function(value) { loadDataset(G_dataset, value); });
}


function importDatasetSetup() {
    // Show import dataset elements
    document.getElementById('importdata').style.display = "block";

    // Add the dataset options to the select element
    requestToServer('fetchdatasetlist', null, 0, onDatasetListSuccess, onDatasetListError);
}

function getZoomAtMouse() {
    return document.getElementById("mousezoomlock").checked;
}

function getUseSensorRanges() {
    return document.getElementById("sensorrange").checked;
}

// Handle the the ui buttons that zoom and pan
function handleZoomUI() {
    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        if (G_mousePos.x <= 0.02) {
            G_zoomUI = "pleft";
        } else if (G_mousePos.x >= 0.98) {
            G_zoomUI = "pright";
        } else {
            G_zoomUI = null;
        }
    }

    if (G_zoomWheel === "zin") {
        zinHandler(getZoomAtMouse());
        G_zoomWheel = null;
    } else if (G_zoomWheel === "zout") {
        zoutHandler(getZoomAtMouse());
        G_zoomWheel = null;
    } else if (G_zoomUI === "pright" || G_prightDown) {
        prightHandler();
    } else if (G_zoomUI === "pleft" || G_pleftDown) {
        pleftHandler();
    } else if (G_zoomUI === "zin" || G_zinDown) {
        zinHandler(false);
    } else if (G_zoomUI === "zout" || G_zoutDown) {
        zoutHandler(false);
    }
}

// Get the dataset configuration from the server
function fetchConfig() {
    if (G_fetchingConfig) {
        return;
    }

    G_fetchingConfig = true;

    requestToServer("fetchdataset?dataset=" + G_dataset + "&type=config", null, 0, onConfigSuccess, onConfigError);
}

let G_urlBaseParam;

// Callback when the config file is loaded from the server
function onConfigError() {
    // TODO: handle error
    showText("message", "Error fetching config.");
    G_config = null;
}

function onConfigSuccess(response) {
    try {
        G_config = JSON.parse(response);

        let requiredFields = ["title", "tile_size", "tile_subsample", "zoom_max", "length", "start_time_ms", "sample_rate", "start_day_idx", "range_span", "sensors", "channels", "labels"];
        let missingFields = "";
        for (var ii = 0; ii < requiredFields.length; ++ ii) {
            if (G_config[requiredFields[ii]] === undefined) {
                missingFields += (" " + requiredFields[ii]);
            }
        }
        if (missingFields !== "") {
            debugLogMessage("Config missing fields:" + missingFields);
            showText("message", "Error in config data.");
            G_config = null;
            return;
        }
        if (G_config.range_span.length != 2 || !Number.isInteger(G_config.range_span[0]) || !Number.isInteger(G_config.range_span[1]) || G_config.range_span[1] <= G_config.range_span[0]) {
            debugLogMessage("Config range error.");
            showText("message", "Error in config data.");
            G_config = null;
            return;
        }

        showText("title", G_config.title);
    } catch(e) {
        G_config = null;
    }

    if (!G_config) {
        showText("message", "Error fetching or parsing config.");
        return;
    }

    G_fetchingConfig = false;
    G_urlBaseParam = window.location.search;

    // Set start date and start day index of output to display
    G_startDate = new Date(G_config.start_time_ms);
    G_startDayIdx = G_config.start_day_idx;



    // Set the defaults and initialize the plot
    DEFAULT_ZOOM = G_config.zoom_max;
    DEFAULT_ZOOM_INTERMEDIATE = ZOOM_INT_MAX_LEVEL;
    DEFAULT_XSCALE = 1.0 / G_config.tile_size / 3;

    // if the signal plot will be short, try to zoom in a bit
    const desiredInitialLength = 2500;
    const initialLength = G_config.length / Math.pow(G_config.tile_subsample, DEFAULT_ZOOM);
    if (initialLength < desiredInitialLength) {
        const initialXScale = desiredInitialLength / initialLength;
        DEFAULT_ZOOM_INTERMEDIATE = clamp(invertXScaleIntermediate(initialXScale), 0, ZOOM_INT_MAX_LEVEL);
    }

    G_zoomUI = null;

    var searchParams = new URLSearchParams(G_urlBaseParam);
    var urlZoom = Number.parseInt(searchParams.get("zoom"));
    var urlZoomInter = Number.parseInt(searchParams.get("zoomi"));
    var urlOffset = Number.parseInt(searchParams.get("offset"));
    var playerIndex = Number.parseInt(searchParams.get("iplayer"));
    var algoIndex = Number.parseInt(searchParams.get("ialgo"));

    G_labelsRemoteStartIndexPlayer = !isNaN(playerIndex) ? Math.max(0, playerIndex) : 0;
    G_labelsRemoteStartIndexAlgo = !isNaN(algoIndex) ? Math.max(0, algoIndex) : 0;
    if (isNaN(urlZoom)) {
        G_zoomLevel = DEFAULT_ZOOM;
        G_zoomLevelIntermediate = DEFAULT_ZOOM_INTERMEDIATE;
    } else {
        G_zoomLevel = clamp(urlZoom, 0, G_config.zoom_max);
        G_zoomLevelIntermediate = !isNaN(urlZoomInter) ? clamp(urlZoomInter, 0, ZOOM_INT_MAX_LEVEL) : ZOOM_INT_MAX_LEVEL;
    }
    G_xScale = getXScale();
    setAndClampXOffset(!isNaN(urlOffset) ? urlOffset : 0);

    G_sensorColors = [];
    for (var ii = 0; ii < G_config.sensors.length; ++ ii) {
        const sensor = G_config.sensors[ii];
        G_sensorColors[sensor.sname] = sensor.color;
    }

    G_channelColors = [];
    for (var ii = 0; ii < G_config.channels.length; ++ ii) {
        const channel = G_config.channels[ii];
        G_channelColors[channel.cname] = channel.color;
    }

    G_labelColors = [];
    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        G_labelColors[label.lname] = label.color;
    }

    createLabelInputs();
    createSensorInputs();
    createChannelInputs();

    // Set range parameters after creating sensor inputs
    resetRangeScaling();

    // Get the labels and create the timeline
    fetchLabels(true);
}

function clamp(x, min, max) {
    return Math.min(max, Math.max(min, x));
}

function createInput(labelname, bgColor, textColor, name, type, checked) {
    var id = name + labelname;

    var newDiv = document.createElement("div");
    newDiv.style.color = getColorString(textColor);
    newDiv.style.backgroundColor = getColorString(bgColor);
    newDiv.style.textAlign = "left";
    newDiv.style.height = "19px";
    newDiv.style.whiteSpace = "nowrap";

    var newLabel = document.createElement("label");
    newLabel.setAttribute("for", id);
    newLabel.setAttribute("title", labelname);
    newLabel.innerHTML = labelname;

    var newInput = document.createElement("input");
    newInput.setAttribute("type", type);
    newInput.setAttribute("id", id);
    newInput.setAttribute("name", name);
    newInput.setAttribute("title", labelname);
    if (checked) {
        newInput.setAttribute("checked", true);
    }

    newDiv.appendChild(newInput);
    newDiv.appendChild(newLabel);

    newDiv.onclick=(evt)=>{
        if (evt.target === newDiv) {
            newInput.click();
        }
    };

    return newDiv;
}

function createSensorInputs() {
    if (G_config.sensors.length > 1) {
        document.getElementById('showsensortitle').style.visibility = 'visible';
        document.getElementById('showsensordiv').style.display = 'block';
        var showSensorDiv = document.getElementById('showsensordiv');
        for (var ii = 0; ii < G_config.sensors.length; ++ ii) {
            showSensorDiv.appendChild(createInput(G_config.sensors[ii].sname, COLOR_UNKNOWN, [1, 1, 1], "showsensor", "checkbox", true));
        }
    } else {
      document.getElementById('showsensortitle').style.visibility = 'hidden';
      document.getElementById('showsensordiv').style.display = 'none';
    }
}

function createChannelInputs() {
    var showChannelDiv = document.getElementById('showchanneldiv');
    for (var ii = 0; ii < G_config.channels.length; ++ ii) {
        showChannelDiv.appendChild(createInput(G_config.channels[ii].cname, COLOR_UNKNOWN, G_config.channels[ii].color, "showchannel", "checkbox", true));
    }
}

function createLabelInputs() {
    var addLabelDiv = document.getElementById('addlabeldiv');
    var showLabelDiv = document.getElementById('showlabeldiv');

    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        addLabelDiv.appendChild(createInput(label.lname, label.color, [1, 1, 1], "addlabel", "radio", ii == 0));
        showLabelDiv.appendChild(createInput(label.lname, label.color, [1, 1, 1], "showlabel", "checkbox", true));
    }
    addLabelDiv.appendChild(createInput("ERASE", COLOR_UNKNOWN, [1, 1, 1], "addlabel", "radio", false));
    showLabelDiv.appendChild(createInput("OTHER", COLOR_UNKNOWN, [1, 1, 1], "showlabel", "checkbox", true));

    var allButton = document.createElement("button");
    allButton.innerHTML = "ALL";
    allButton.addEventListener('click', showAllLabels);
    showLabelDiv.appendChild(allButton);

    var noneButton = document.createElement("button");
    noneButton.innerHTML = "NONE";
    noneButton.addEventListener('click', hideAllLabels);
    showLabelDiv.appendChild(noneButton);
}

function shouldFetchSource(source) {
    if (G_sourcesToFetch === null) {
        return true;
    } else {
        return G_sourcesToFetch.has(source);
    }
}

// Get all of the labels from the server
function fetchLabels(fetchLocal) {
    if (G_fetchingLabels) {
        return;
    }

    G_fetchingLabels = true;
    G_fetchingLabelsLocal = fetchLocal;

    requestToServer("fetchlabels?dataset=" + G_dataset, null, 0, onLabelsSuccess, onLabelsError);
}

// Callback for when labels are received
function onLabelsError() {
    // TODO: handle error
}

function onLabelsSuccess(response) {
    var updateLocal = G_fetchingLabelsLocal;
    G_fetchingLabels = false;
    G_fetchingLabelsLocal = false;

    G_labelsRemoteYours = null;
    G_labelsRemoteNotes = [];
    G_labelsRemoteOtherPlayer = [];
    G_labelsRemoteAlgo = [];
    G_labelsRemoteGroundTruth = null;

    var useLocalLabels = G_labelsLocal;
    if (response.length > 0) {
        // Set remote labels to what was received
        var labelsResponse = JSON.parse(response);
        var initFrom = null;
        for (var ll = 0; ll < labelsResponse.length; ++ ll) {
            var lr = labelsResponse[ll];
            sortLabels(lr.labels);
            if (updateLocal) {
                if (lr.labelset === G_sessLabelId) {
                    useLocalLabels = lr.labels.slice();
                }
                if (G_config.initfrom && lr.labelset === G_config.initfrom) {
                    initFrom = lr.labels.slice();
                }
            }

            if (lr.labelset === G_sessLabelId) {
                G_labelsRemoteYours = lr;
                G_labelsets.push(lr.labelset)
            } else {
                if (shouldFetchSource(lr.source)) {
                    if (lr.source === SOURCE_ALGO) {
                        G_labelsRemoteAlgo.push(lr);
                    }
                    else if (lr.source === SOURCE_NOTES) {
                        G_labelsRemoteNotes.push(lr);
                    }
                    else if (lr.source === SOURCE_GROUND_TRUTH) {
                        if (G_labelsRemoteGroundTruth === null) {
                            G_labelsRemoteGroundTruth = lr;
                        } else {
                            G_labelsRemoteGroundTruth = 'ERROR';
                            debugLogMessage('Multiple labelsets with source Truth');
                        }
                    } else {
                        G_labelsRemoteOtherPlayer.push(lr);
                        G_labelsets.push(lr.labelset)
                    }
                }
            }
        }

        // Initialize local labels
        if (updateLocal && initFrom && useLocalLabels.length === 0 && G_labelsLocal.length === 0) {
            useLocalLabels = initFrom;
        }
    }

    updateLabelsLocal(false, useLocalLabels);

    updateLabelsetsListDropdown(G_labelsets);

    G_labelsRemoteStartIndexAlgo = G_labelsRemoteAlgo.length ? ((G_labelsRemoteStartIndexAlgo) % G_labelsRemoteAlgo.length) : 0;
    G_labelsRemoteStartIndexPlayer = G_labelsRemoteOtherPlayer.length ? ((G_labelsRemoteStartIndexPlayer) % G_labelsRemoteOtherPlayer.length) : 0;
}

// Figure out if a tile should be in the data set
function shouldTileBeInData(zoomLevel, tile) {
    var zoomScale = Math.pow(G_config.tile_subsample, zoomLevel);
    var tileLo = (tile + 0) * G_config.tile_size * zoomScale;
    var tileHi = (tile + 1) * G_config.tile_size * zoomScale;
    return tileHi > 0 && tileLo < G_config.length;
}

// Get the given tile from the server if it's not already present
function fetchTileIfNeeded(zoomLevel, tile) {
    if (!shouldTileBeInData(zoomLevel, tile)) {
        return;
    }

    var tileId = getTileId(zoomLevel, tile);
    var tileData = G_tileData.get(tileId);

    var needsFetch = false;
    if (tileData === undefined) {
        needsFetch = true;
    } else if (tileData.status === FETCH_STATUS_ERROR && Date.now() > tileData.errortime) {
        needsFetch = true;
    }

    if (needsFetch) {
        // Adds timestamp and clears cache if it has exceeded.
        G_tileData.set(tileId, { status: FETCH_STATUS_PENDING });
        updateAccess(tileId);

        requestToServer("fetchdataset?dataset=" + G_dataset + "&type=tile&id=" + tileId, null, 0,
                        function(response) { onTileSuccess(zoomLevel, tile, response); },
                        function() { onTileError(zoomLevel, tile); });
    }
}

// wait a few seconds before retrying tile fetch
function getTileErrorTime() {
    return Date.now() + 2000 + 3000 * Math.random();
}

// wait a few seconds before retrying image fetch
function getImageErrorTime() {
    return Date.now() + 5000 + 5000 * Math.random();
}

// Callback function to execute when the server returns a tile
function onTileError(zoomLevel, tile) {
    var tileId = getTileId(zoomLevel, tile);

    // Adds timestamp and clears cache if it has exceeded.
    G_tileData.set(tileId, { status: FETCH_STATUS_ERROR, errortime: getTileErrorTime() });
    updateAccess(tileId);
}

function onTileSuccess(zoomLevel, tile, response) {
    var tileId = getTileId(zoomLevel, tile);

    var tileConfig = undefined;
    try {
        tileConfig = JSON.parse(response);
    } catch(e) {
        tileConfig = undefined;
    }

    if (tileConfig === undefined) {
        G_tileData.set(tileId, { status: FETCH_STATUS_ERROR, errortime: getTileErrorTime() });
        return;
    }

    allocateTile(zoomLevel, tile, tileConfig);
}

// Converts the newly downloaded tile into a usuable data structure
function allocateTile(zoomLevel, tile, tileConfig) {
    var data = tileConfig.data;

    // Initialize a 2D array to store data in
    var sensordata = [];
    for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
        for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
            if (G_config.sensors[ss].stype == SENSOR_TYPE_DATA) {
                sensordata.push([]);
            } else {
                sensordata.push(undefined);
            }
        }
    }

    /*
      There are two ways the buffers can be organized for primitives.
      If a tile is not missing any samples, the vertices and triangles
      look like this (where A is a sample's lo value and B is it's hi
      value, etc):

      B - D - F - H - J
      | \ | \ | \ | \ |
      A - C - E - G - I

      Then the vertices can be organized in the buffer and the
      primitives arranged like this:

                 ABCDEFGHIJ
      TriStrip:  **********
      LineStrip: * * * * *
      LineStrip:  * * * * *

      If there is any missing data in the tile, the vertices and
      triangle may look like this (where X is a missing sample):

      B - D       H - J
      | \ |   X   | \ |
      A - C       G - I

      To make sure there is somthing to draw for the C-D sample we add some offset vertices:

      B - D-d     H - J
      | \ |\| X   | \ |
      A - C-c     G - I

      Then organize the buffer and the primitives like this:

             ABCCDBCDccdDGHIIJH
      Tris:  ******************
      Lines: *  *  *  *  *  *
      Lines:  *  *  *  *  *  *
    */

    var bufferType = TILE_BUFFER_CONTIGUOUS;

    for (var dd = 0; dd < data.length; ++ dd) {
        var dataIndex = 0;
        for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
            for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                if (G_config.sensors[ss].stype == SENSOR_TYPE_DATA) {
                    if (data[dd][dataIndex] === null) {
                        bufferType = TILE_BUFFER_GAPS;
                    }
                }
                ++ dataIndex;
            }
        }
    }

    // Put the data received into the 2D array
    if (bufferType === TILE_BUFFER_CONTIGUOUS) {
        for (var dd = 0; dd < data.length; ++ dd) {
            var dataIndex = 0;
            for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
                for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                    if (G_config.sensors[ss].stype == SENSOR_TYPE_DATA) {
                        var lo = data[dd][dataIndex][0];
                        var hi = data[dd][dataIndex][1];
                        sensordata[dataIndex].push(dd);
                        sensordata[dataIndex].push(lo);
                        sensordata[dataIndex].push(dd);
                        sensordata[dataIndex].push(hi);
                    }
                    ++ dataIndex;
                }
            }
        }
    } else if (bufferType === TILE_BUFFER_GAPS) {
        for (var dd = 0; dd < data.length - 1; ++ dd) {
            var dataIndex = 0;
            for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
                for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                    if (G_config.sensors[ss].stype == SENSOR_TYPE_DATA) {
                        if (data[dd + 0][dataIndex] !== null) {
                            if (data[dd + 1][dataIndex] !== null) {
                                var lo0 = data[dd + 0][dataIndex][0];
                                var hi0 = data[dd + 0][dataIndex][1];
                                var lo1 = data[dd + 1][dataIndex][0];
                                var hi1 = data[dd + 1][dataIndex][1];

                                sensordata[dataIndex].push(dd + 0);
                                sensordata[dataIndex].push(lo0);
                                sensordata[dataIndex].push(dd + 0);
                                sensordata[dataIndex].push(hi0);
                                sensordata[dataIndex].push(dd + 1);
                                sensordata[dataIndex].push(lo1);

                                sensordata[dataIndex].push(dd + 1);
                                sensordata[dataIndex].push(lo1);
                                sensordata[dataIndex].push(dd + 1);
                                sensordata[dataIndex].push(hi1);
                                sensordata[dataIndex].push(dd + 0);
                                sensordata[dataIndex].push(hi0);
                            } else {
                                var lo0 = data[dd + 0][dataIndex][0];
                                var hi0 = data[dd + 0][dataIndex][1];
                                var lo1 = lo0;
                                var hi1 = hi0;

                                sensordata[dataIndex].push(dd + 0);
                                sensordata[dataIndex].push(lo0);
                                sensordata[dataIndex].push(dd + 0);
                                sensordata[dataIndex].push(hi0);
                                sensordata[dataIndex].push(dd + 0.5);
                                sensordata[dataIndex].push(lo1);

                                sensordata[dataIndex].push(dd + 0.5);
                                sensordata[dataIndex].push(lo1);
                                sensordata[dataIndex].push(dd + 0.5);
                                sensordata[dataIndex].push(hi1);
                                sensordata[dataIndex].push(dd + 0);
                                sensordata[dataIndex].push(hi0);
                            }
                        }
                    }
                    ++ dataIndex;
                }
            }
        }
    } else {
        debugLogMessage("unrecognized tile buffer type: " + bufferType);
    }

    // Create the buffers for the data
    var dataIndex = 0;
    var sensorbuffers = [];
    var sensorbuffersizes = [];
    for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
        if (G_config.sensors[ss].stype == SENSOR_TYPE_DATA) {
            var channelbuffers = []
            var channelbuffersizes = []
            for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                const new_buffer = G_glCtx.createBuffer();
                G_glCtx.bindBuffer(G_glCtx.ARRAY_BUFFER, new_buffer);
                G_glCtx.bufferData(G_glCtx.ARRAY_BUFFER, new Float32Array(sensordata[dataIndex]), G_glCtx.STATIC_DRAW);
                channelbuffers.push(new_buffer);
                channelbuffersizes.push(sensordata[dataIndex].length / 2);
                ++ dataIndex;
            }
            sensorbuffers.push(channelbuffers);
            sensorbuffersizes.push(channelbuffersizes);
        } else {
            sensorbuffers.push(undefined);
            sensorbuffersizes.push(undefined);
            dataIndex += G_config.sensors[ss].channels.length;
        }
    }

    /*
    // start fetching images in the tile
    for (var dd = 0; dd < data.length; ++ dd) {
        var dataIndex = 0;
        for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
            for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                if (G_config.sensors[ss].stype == SENSOR_TYPE_IMAGE) {
                    if (data[dd][dataIndex] !== null) {
                        fetchImageIfNeeded(G_config.sensors[ss].sname, data[dd][dataIndex]);
                    }
                }
                ++ dataIndex;
            }
        }
    }
    */


    tileData = {
        status: FETCH_STATUS_READY,
        bufferType: bufferType,
        buffers: sensorbuffers,
        bufferSizes: sensorbuffersizes,
        data: data
    };

    let tileId = getTileId(zoomLevel, tile);
    G_tileData.set(tileId, tileData);

    // Adds timestamp and clears cache if it has exceeded.
    updateAccess(tileId);
}

function getImageKey(sensorName, imageId) {
    return G_dataset + '__' + sensorName + '__' + imageId;
}

// Get the given image from the server if it's not already present
function fetchImageIfNeeded(sensorName, imageId) {
    let imageKey = getImageKey(sensorName, imageId);
    let imageData = G_imageData.get(imageKey);

    // Checks if an image needs to be refetched
    var needsReFetch = false;

    if (imageData === undefined) {
        needsReFetch = true;
    } else if (imageData.status === FETCH_STATUS_ERROR && Date.now() > imageData.errortime) {
        needsReFetch = true;
    }

    // Fetching or refetching the current image
    if (needsReFetch) {
        let newImage = new Image(IMAGE_HEIGHT * IMAGE_ASPECT, IMAGE_HEIGHT);

        newImage.onload = () => {
            let imageKey = getImageKey(sensorName, imageId);
            G_imageData.set(imageKey, { status: FETCH_STATUS_READY, image: newImage });
            // TODO: update image access for cache
        }

        // Callback function to execute if there is image fetching error
        newImage.onerror = () => {
            let imageKey = getImageKey(sensorName, imageId);

            // Adds timestamp and clears cache if it has exceeded
            G_imageData.set(imageKey, { status: FETCH_STATUS_ERROR, errortime: getImageErrorTime() });

            // Warns that the image needs to be refetched
            //console.log("Error fetching image. Ready to refetch...");

            // TODO: update image access for cache
        }

        G_imageData.set(imageKey, { status: FETCH_STATUS_PENDING });
        newImage.src = "fetchdataset?dataset=" + G_dataset + "&type=image&sensor=" + sensorName + "&id=" + imageId;
    }
}


// Initialize the shader
function initShaderProgram() {
    const vertexShader = loadShader(G_glCtx.VERTEX_SHADER, VS_SOURCE);
    const fragmentShader = loadShader(G_glCtx.FRAGMENT_SHADER, FS_SOURCE);

    // Create the shader program
    const shaderProgram = G_glCtx.createProgram();
    G_glCtx.attachShader(shaderProgram, vertexShader);
    G_glCtx.attachShader(shaderProgram, fragmentShader);
    G_glCtx.linkProgram(shaderProgram);

    // If creating the shader program failed, alert
    if (!G_glCtx.getProgramParameter(shaderProgram, G_glCtx.LINK_STATUS)) {
        alert('Unable to initialize the shader program: ' + G_glCtx.getProgramInfoLog(shaderProgram));
        return null;
    }

    return shaderProgram;
}

// Compile, load, then return the given shader
function loadShader(type, source) {
    const shader = G_glCtx.createShader(type);
    G_glCtx.shaderSource(shader, source);
    G_glCtx.compileShader(shader);

    if (!G_glCtx.getShaderParameter(shader, G_glCtx.COMPILE_STATUS)) {
        alert('An error occurred compiling the shaders: ' + G_glCtx.getShaderInfoLog(shader));
        G_glCtx.deleteShader(shader);
        return null;
    }

    return shader;
}

// Initialize the quad buffers
function initQuadBuffer() {
    const new_buffer = G_glCtx.createBuffer();
    G_glCtx.bindBuffer(G_glCtx.ARRAY_BUFFER, new_buffer);
    G_glCtx.bufferData(G_glCtx.ARRAY_BUFFER, new Float32Array(getQuadBufferData()), G_glCtx.STATIC_DRAW);
    G_quadBuffer = new_buffer;
}

function measureTextWidth(text, fontSize) {
    G_overCtxOffscreen.font = fontSize.toString() + "px Arial, Helvetica, sans-serif";
    return G_overCtxOffscreen.measureText(text).width / G_canvasWidth;
}

function drawText(text, tx, ty, halign, valign, maxwidth, color, fontSize, outline) {
    // on Firefox, the text seems a little higher than on other browsers
    var yoffset = 0;
    if (IS_FIREFOX) {
        if (valign === "middle") {
            yoffset = Math.floor(fontSize / 8);
        }
    }

    G_overCtxOffscreen.font = fontSize.toString() + "px Arial, Helvetica, sans-serif";
    G_overCtxOffscreen.textAlign = halign;
    G_overCtxOffscreen.textBaseline = valign;

    var xp = Math.floor(tx * G_canvasWidth);
    var yp = Math.floor((1.0 - ty) * G_canvasHeight + yoffset);
    var mw = (maxwidth ? maxwidth * G_canvasWidth : undefined);

    if (outline) {
        G_overCtxOffscreen.fillStyle = "#444444";
        for (var dx = -1; dx <= 1; ++ dx) {
            for (var dy = -1; dy <= 1; ++ dy) {
                G_overCtxOffscreen.fillText(text, xp + dx, yp + dy, mw);
            }
        }
    }
    G_overCtxOffscreen.fillStyle = color;
    G_overCtxOffscreen.fillText(text, xp, yp, mw);
}

// Set the color of the webgl renderer
function setColor(clr, scale, alpha) {
    if (scale === undefined) {
        scale = 1.0;
    }
    if (alpha === undefined) {
        alpha = 1.0;
    }
    G_glCtx.uniform4fv(G_uGlobalColor, [scale * clr[0], scale * clr[1], scale * clr[2], alpha]);
}

// Set the uniform of the offset and scale
function setXform(xx, yy, ww, hh) {
    G_glCtx.uniform2fv(G_uOffset, [xx, yy]);
    G_glCtx.uniform2fv(G_uScale, [ww, hh]);
}

// Draw the given buffer
function drawBuffer(buffer, prim, start, size, stride=0, offset=0) {
    G_glCtx.bindBuffer(G_glCtx.ARRAY_BUFFER, buffer);
    G_glCtx.vertexAttribPointer(G_programInfo.attribLocations.vertexPosition, 2, G_glCtx.FLOAT, false, stride, offset);
    G_glCtx.enableVertexAttribArray(G_programInfo.attribLocations.vertexPosition);
    G_glCtx.drawArrays(prim, start, size);
}

// Draw a filled or "hollow" quad at the given x and y with the given width and height
function drawQuad(filled, xl, yc, ww, hh) {
    setXform(xl, yc, ww, hh);
    drawBuffer(G_quadBuffer, filled ? G_glCtx.TRIANGLE_FAN : G_glCtx.LINE_LOOP, 0, 4);
}

// Draw a tile of data
function drawTile(zoomLevel, tile, inactive) {
    if (!G_config) {
        return;
    }

    if (!shouldTileBeInData(zoomLevel, tile)) {
        return;
    }

    var tileId = getTileId(zoomLevel, tile);
    var tileData = G_tileData.get(tileId);

    // Adds timestamp and clears cache if it has exceeded.
    updateAccess(tileId);

    if (tileData) {
        if (isTileDebugging()) {
            setColor([0.3, 0.3, 0.3]);
            drawQuad(false,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_plotY[0],
                     G_xScale * (G_config.tile_size), G_plotHeight / 2);
        }

        if (tileData.status === FETCH_STATUS_READY) {
            setXform(G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_plotY[0] + G_rangeInfo.plotOffset,
                     G_xScale, G_plotHeight / 2 * G_rangeInfo.plotScale);

            var scale = 1.0;
            if (inactive) {
                scale = 0.2;
            }

            // draw back to front
            for (var ss = G_config.sensors.length - 1; ss >= 0; -- ss) {
                if (!isSensorVisible(G_config.sensors[ss].sname)) {
                    continue;
                }

                if (G_config.sensors[ss].stype != SENSOR_TYPE_DATA) {
                    continue;
                }

                // draw back to front
                for (var cc = G_config.sensors[ss].channels.length - 1; cc >= 0; -- cc) {
                    if (!isChannelVisible(G_config.sensors[ss].channels[cc])) {
                        continue;
                    }

                    var useColor = multiplyColors(getChannelColor(G_config.sensors[ss].channels[cc]), getSensorColor(G_config.sensors[ss].sname));
                    setColor(useColor, scale);

                    var buffer = tileData.buffers[ss][cc];
                    var bufferSize = tileData.bufferSizes[ss][cc];

                    //console.log("draw", ss, cc, buffer, bufferSize);

                    if (tileData.bufferType === TILE_BUFFER_CONTIGUOUS) {
                        // Fill in area
                        drawBuffer(buffer, G_glCtx.TRIANGLE_STRIP, 0, bufferSize);

                        // Draw outlines
                        drawBuffer(buffer, G_glCtx.LINE_STRIP, 0, bufferSize / 2, 16, 0);
                        drawBuffer(buffer, G_glCtx.LINE_STRIP, 0, bufferSize / 2, 16, 8);
                    } else if (tileData.bufferType === TILE_BUFFER_GAPS) {
                        // Fill in area
                        drawBuffer(buffer, G_glCtx.TRIANGLES, 0, bufferSize);

                        // Draw outlines
                        drawBuffer(buffer, G_glCtx.LINES, 0, bufferSize / 3, 24, 0);
                        drawBuffer(buffer, G_glCtx.LINES, 0, bufferSize / 3, 24, 8);
                    }
                }
            }
        } else {
            setColor([0.1, 0.1, 0.1]);
            drawQuad(true,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_plotY[0],
                     G_xScale * (G_config.tile_size), G_plotHeight / 16);

            if (tileData.status === FETCH_STATUS_ERROR) {
                var tileText = "Error loading.";
            } else {
                var tileText = "Loading...";
            }
            drawText(tileText, G_xScale * ((G_xOffset + X_OFFSET) + (tile + 0.5) * G_config.tile_size), G_plotY[0], "center", "middle", undefined, COLORH_TIMELINE_TEXT, 14);
        }
    } else {
        if (isTileDebugging()) {
            setColor([0.05, 0.0, 0.0]);
            drawQuad(true,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_plotY[0],
                     G_xScale * (G_config.tile_size), G_plotHeight / 2);
            setColor([0.5, 0.0, 0.0]);
            drawQuad(false,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_plotY[0],
                     G_xScale * (G_config.tile_size), G_plotHeight / 2);
        }
    }
}

// Draw a tile of data
function drawTileImages(zoomLevel, tile, inactive, lastImageEndX) {
    if (!G_config) {
        return;
    }

    if (!shouldTileBeInData(zoomLevel, tile)) {
        return;
    }

    var tileId = getTileId(zoomLevel, tile);
    var tileData = G_tileData.get(tileId);

    // Adds timestamp and clears cache if it has exceeded.
    updateAccess(tileId);

    if (tileData) {
        if (tileData.status === FETCH_STATUS_READY) {
            var zoomScale = Math.pow(G_config.tile_subsample, zoomLevel);

            var dataIndex = 0;
            var imageSensorChannelIndex = 0;

            for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
                if (!isSensorVisible(G_config.sensors[ss].sname)) {
                    dataIndex += G_config.sensors[ss].channels.length;
                    continue;
                }

                if (G_config.sensors[ss].stype != SENSOR_TYPE_IMAGE) {
                    dataIndex += G_config.sensors[ss].channels.length;
                    continue;
                }

                for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                    if (!isChannelVisible(G_config.sensors[ss].channels[cc])) {
                        dataIndex += 1;
                        continue;
                    }

                    for (var dd = 0; dd < tileData.data.length; ++ dd) {
                        var smp = dd + tile * G_config.tile_size;
                        var imageX = G_canvasWidth * (G_xScale * (G_xOffset + smp) + X_OFFSET);

                        var endKey = G_config.sensors[ss].sname + '__' + G_config.sensors[ss].channels[cc];
                        var endX = lastImageEndX.get(endKey);

                        if (endX !== undefined && endX + 1 >= imageX) {
                            continue;
                        }

                        var imageId = tileData.data[dd][dataIndex];
                        if (imageId === null) {
                            continue;
                        }

                        lastImageEndX.set(endKey, imageX + IMAGE_HEIGHT * IMAGE_ASPECT);

                        fetchImageIfNeeded(G_config.sensors[ss].sname, imageId);

                        var ix = imageX;
                        var iy = 250 - IMAGE_HEIGHT * 1.05 * (imageSensorChannelIndex + 1);
                        var iw = IMAGE_HEIGHT * IMAGE_ASPECT;
                        var ih = IMAGE_HEIGHT;

                        var imageKey = getImageKey(G_config.sensors[ss].sname, imageId);
                        var imageData = G_imageData.get(imageKey);

                        if (imageData.status == FETCH_STATUS_READY) {
                            G_underCtxOffscreen.drawImage(imageData.image, ix, iy, iw, ih);
                        } else {
                            G_underCtxOffscreen.fillStyle = "#444444";
                            G_underCtxOffscreen.fillRect(ix, iy, iw, ih);
                        }
                    }

                    ++ dataIndex;
                    ++ imageSensorChannelIndex;
                }
            }
        }
    }
}

// Add column label to indicate creator of the set of labels
function drawLabelName(labelsetName, ymid, backing) {
    var mouseOverPlayerLabelName = G_mousePos && NAME_OFFSET <= G_mousePos.x && G_mousePos.x <= NAME_OFFSET + NAME_WIDTH
        && ymid - (LABEL_HEIGHT / 2) <= G_mousePos.y && G_mousePos.y <= ymid + (LABEL_HEIGHT / 2);

    if (backing) {
        setColor(COLOR_TIMELINE);
        drawQuad(true,
                 NAME_OFFSET, ymid,
                 NAME_WIDTH, LABEL_HEIGHT / 2 * 0.9);
    }
    drawText(labelsetName, NAME_OFFSET + NAME_WIDTH - TEXT_INSET, ymid, "right", "middle", NAME_WIDTH - 2 * TEXT_INSET, mouseOverPlayerLabelName ? "#ffff88" : "#ffffff", 14);

    return mouseOverPlayerLabelName;
}

function formatChannel(val) {
    return val.toFixed(3);
}

function checkChannelTooltip() {
    if (!readyForTooltip(TT_DELAY_CHANNEL)) {
        return;
    }

    var mpos = G_mousePos;

    if (mpos !== null &&  G_plotY[0] - G_plotHeight / 2 < mpos.y && mpos.y < G_plotY[0] + G_plotHeight / 2) {
        var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);

        var tileIndex = Math.floor(smpx / G_config.tile_size);
        var tileId = getTileId(G_zoomLevel, tileIndex);
        var currentTile = G_tileData.get(tileId);

        // TODO: check not off the end of the signal

        if (currentTile && currentTile.status == FETCH_STATUS_READY) {
            var tileSampleIndex = smpx - tileIndex * G_config.tile_size;
            var currentSample = currentTile.data[tileSampleIndex];
            if (currentSample) {
                var text = [];
                var dataIndex = 0;
                for (var ss = 0; ss < G_config.sensors.length; ++ ss) {
                    if (!isSensorVisible(G_config.sensors[ss].sname)) {
                        dataIndex += G_config.sensors[ss].channels.length;
                        continue;
                    }

                    if (G_config.sensors[ss].stype != SENSOR_TYPE_DATA) {
                        dataIndex += G_config.sensors[ss].channels.length;
                        continue;
                    }

                    if (G_config.sensors.length !== 1) {
                        text.push(G_config.sensors[ss].sname);
                    }

                    for (var cc = 0; cc < G_config.sensors[ss].channels.length; ++ cc) {
                        if (!isChannelVisible(G_config.sensors[ss].channels[cc])) {
                            dataIndex += 1;
                            continue;
                        }

                        var channelText = '';
                        if (G_config.sensors.length !== 1) {
                            channelText += '  ';
                        }

                        var channelName = G_config.sensors[ss].channels[cc];
                        channelText += channelName;
                        channelText += ': ';

                        if (currentSample[dataIndex] === null) {
                            channelText += '--';
                        } else {
                            var lo = currentSample[dataIndex][0];
                            var hi = currentSample[dataIndex][1];

                            if (Math.abs(lo - hi) < 0.002) {
                                channelText += formatChannel(0.5 * (lo + hi));
                            } else {
                                channelText += formatChannel(lo);
                                channelText += ' to ';
                                channelText += formatChannel(hi);
                            }
                            if (G_config.sensors[ss].range_unit !== '') {
                                channelText += ' ' + G_config.sensors[ss].range_unit;
                            }
                        }

                        text.push(channelText);

                        ++ dataIndex;
                    }
                }

                if (text.length > 0) {
                    updateToolTip({ text: text });
                }
            }
        }
    }
}

function resetTooltipTimer(evt) {
    G_tooltipDelayFromTime = Date.now();
}

function readyForTooltip(delay) {
    return !G_tooltipInfo && (delay === 0 || Date.now() - G_tooltipDelayFromTime >= delay);
}

function updateToolTip(info) {
    G_tooltipInfo = info;
}

// Draw tooltip near mouse
function drawTooltip(info) {
    if (info === null) {
        return;
    }

    var text = info.text;

    if (!Array.isArray(text)) {
        text = [text];
    }

    const FONT_SIZE = 14;

    var tooltipHeight = (FONT_SIZE * text.length + 6) / G_canvasHeight;
    var tooltipWidth = 0;
    for (var ii = 0; ii < text.length; ++ ii) {
        tooltipWidth = Math.max(tooltipWidth, measureTextWidth(text[ii], FONT_SIZE));
    }
    tooltipWidth += 2 * TEXT_INSET;

    var tooltipX = clamp(G_mousePos.x, 0, 1.0 - tooltipWidth);
    var tooltipY = 0.01 + G_mousePos.y + tooltipHeight * 0.5;

    G_overCtxOffscreen.fillStyle = COLOR_TOOLTIP;
    G_overCtxOffscreen.fillRect(tooltipX * G_canvasWidth, (1.0 - (tooltipY + 0.5 * tooltipHeight)) * G_canvasHeight, tooltipWidth * G_canvasWidth, tooltipHeight * G_canvasHeight);

    for (var ii = 0; ii < text.length; ++ ii) {
        drawText(text[ii], tooltipX + TEXT_INSET, tooltipY - ((ii - text.length / 2) * FONT_SIZE + 2) / G_canvasHeight, "left", "top", tooltipWidth, "#ffffff", FONT_SIZE);
    }
}

// Draw all of the given labels at the starting y
function drawLabels(labelsetName, ymid, labels, highlightRange) {
    if (!G_config) {
        return;
    }

    // Used to convert the label's raw data points to data points at the current zoom level
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    // Variables for displaying indication of small labels and gaps
    var lastSmallLoX = null;
    var lastSmallHiX = null;
    var lastSmallHasGap = false;
    var lastSmallColors = [];

    var mouseOnLabel = null; // information on the label the mouse is over, if any
    var textXCutoff = 0.0; // point before which we should not draw label text

    // Construct a list of the label types that should not be displayed
    var visibleLabelsLookup = getVisibleLabels();

    // find the labels to show
    var visibleLabels = [];
    var anyOverlap = false;
    for (var ll = 0; ll < labels.length; ++ ll) {
        var label = labels[ll];

        var lookupName = label.lname;
        if (G_labelColors[lookupName] == undefined) {
            lookupName = "OTHER";
        }

        if (visibleLabelsLookup[lookupName] !== undefined) {
            visibleLabels.push(label);
        }

        if (ll + 1 < labels.length && label.hi > labels[ll + 1].lo) {
            anyOverlap = true;
        }
    }

    if (anyOverlap) {
        var errorlabel = {
            lo: 0,
            hi: G_config.length,
            lname: "[overlapping labels]"
        };
        visibleLabels = [errorlabel];
    }

    // Go through all labels and gaps to be drawn
    for (var ll = 0; ll < visibleLabels.length * 2 - 1; ++ ll) {
        // even: label, odd: gap
        var slo;
        var shi;
        var name;
        var detail;
        var color;
        var isgap;
        var isempty;
        if (ll % 2 === 0) {
            var label = visibleLabels[ll / 2];
            slo = label.lo;
            shi = label.hi;
            name = label.lname;
            detail = label.detail;
            color = getLabelColor(label.lname);
            isgap = false;
            isempty = false;
        } else {
            var labelLo = visibleLabels[(ll - 1) / 2];
            var labelHi = visibleLabels[(ll - 1) / 2 + 1];
            slo = labelLo.hi;
            shi = labelHi.lo;
            name = 'NONE';
            detail = null;
            color = COLOR_CANVAS_BACKGROUND;
            isgap = true;
            isempty = (shi <= slo);
        }

        if (isgap && isempty) {
            continue;
        }

        // Determine label coordinates
        var lo = slo / zoom;
        var hi = shi / zoom;

        var left = G_xScale * (G_xOffset + lo) + X_OFFSET;
        var width = G_xScale * (hi - lo);

        var xlo = left;
        var xhi = left + width;

        // Draw label if needed
        const BIGSIZE = 5;
        var isBig = (G_xScale * (hi - lo) * G_canvasWidth) >= BIGSIZE;

        if (isBig) {
            // Draw small label summary, if needed
            if (lastSmallLoX != null) {
                var sleft = lastSmallLoX;
                var swidth = lastSmallHiX - lastSmallLoX;
                if (sleft + swidth >= -0.01 && 1.01 > sleft) {

                    var gapX0 = sleft - LABEL_INDICATOR_OVERHANG;
                    var gapWidth= swidth + 2 * LABEL_INDICATOR_OVERHANG;
                    var gapY0 = ymid + LABEL_HEIGHT / 2 + LABEL_INDICATOR / 2;
                    var gapHeight = LABEL_INDICATOR / 2;

                    setColor(lastSmallHasGap ? COLOR_SMALL_GAP : COLOR_SMALL_LABEL);
                    drawQuad(true, gapX0, gapY0, gapWidth, gapHeight);
                    setColor(averageColor(lastSmallColors));
                    drawQuad(true,
                             sleft, ymid,
                             swidth, LABEL_HEIGHT / 2);

                    // Draw tooltip if mouse is hovering over small gap indicator
                    var mouseOverGapIndicator = G_mousePos && gapX0 <= G_mousePos.x && G_mousePos.x <= gapX0 + gapWidth
                        && gapY0 - (gapHeight * 2) <= G_mousePos.y && G_mousePos.y <= gapY0;

                    if (mouseOverGapIndicator && readyForTooltip(TT_DELAY_SUMMARY)) {
                        updateToolTip({ text: lastSmallHasGap ? TT_SUMMARY_WITH_GAP : TT_SUMMARY_WITHOUT_GAP });
                    }
                }
            }
            lastSmallLoX = null;
            lastSmallHiX = null;
            lastSmallHasGap = false;
            lastSmallColors = [];

            // Draw label itself
            if (left + width >= -0.01 && 1.01 > left) {
                if (!isgap) {
                    setColor(color);
                    drawQuad(true,
                             left, ymid,
                             width, LABEL_HEIGHT / 2);

                    setColor(color, 1.2);
                    drawQuad(true,
                             left, ymid,
                             TINY_SIZE, LABEL_HEIGHT / 2);
                }
            }
        } else {
            // Remember small labels not drawn
            if (lastSmallLoX != null) {
                lastSmallLoX = Math.min(lastSmallLoX, xlo);
                lastSmallHiX = Math.max(lastSmallHiX, xhi);
            } else {
                lastSmallLoX = xlo;
                lastSmallHiX = xhi;
            }
            lastSmallHasGap = lastSmallHasGap || isgap;
            addLabel(lastSmallColors, name, Math.max(1, shi - slo) * (isgap ? 0.25 : 1.0));
        }

        // Handle the text channel of this label
        if (!isgap) {
            if (left + width >= -0.01 && 1.01 > left) {
                var text = name;
                var textx = Math.max(NAME_OFFSET + NAME_WIDTH, left) + TEXT_INSET;
                var textxmax = (left + width) - TEXT_INSET;
                var texty = ymid;
                var maxTextWidth = textxmax - textx;
                const TEXT_WIDTH_TO_SHOW = 0.02;

                var mouseOverLabel = G_mousePos && left <= G_mousePos.x && G_mousePos.x <= left + width &&
                    ymid - LABEL_HEIGHT / 2 <= G_mousePos.y && G_mousePos.y <= ymid + LABEL_HEIGHT / 2 &&
                    G_mousePos.x > NAME_OFFSET + NAME_WIDTH + TEXT_INSET;

                if (mouseOverLabel && G_mouseAction === MOUSE_COPY_LABEL) {
                    setCurrentLabel(name);
                    G_mouseAction = MOUSE_COPY_LABEL_COMPLETE;
                }

                if (detail !== null && detail !== undefined) {
                    if (mouseOverLabel && readyForTooltip(TT_DELAY_SUMMARY)) {
                        updateToolTip({ text: detail });
                    }
                }

                var canShowText = false;
                var textWidth = undefined;
                if (maxTextWidth >= TEXT_WIDTH_TO_SHOW) {
                    textWidth = measureTextWidth(text, 18);
                    if (textWidth < maxTextWidth * 1.25) {
                        canShowText = true;
                    }
                }

                if (!mouseOnLabel && mouseOverLabel && (G_mouseAction === MOUSE_COPY_LABEL || G_mouseAction === MOUSE_COPY_LABEL_COMPLETE || G_mouseAction === null)) {
                    var usemaxtextwidth = maxTextWidth;
                    if (!canShowText) {
                        usemaxtextwidth = undefined;
                    }
                    if (G_mouseDown && G_mouseAction === null) {
                        text += ": ";
                        text += dateStringFromSample(slo, true, false, false);
                        text += " - ";
                        text += dateStringFromSample(shi, true, false, false);
                        usemaxtextwidth = undefined;
                        textWidth = measureTextWidth(text, 18);
                        highlightRange.lo = slo;
                        highlightRange.hi = shi;
                    }

                    if (textWidth === undefined) {
                        textWidth = measureTextWidth(text, 18);
                    }
                    textXCutoff = textx + textWidth + TEXT_INSET;
                    mouseOnLabel = { text: text, textx: textx, texty: texty, maxtextwidth: usemaxtextwidth, lo: slo, hi: shi };
                } else {
                    if (canShowText && textx > textXCutoff) {
                        drawText(text, textx, texty, "left", "middle", maxTextWidth, "#ffffff", 18, true);
                    }
                }
            }
        }
    }

    // Draw final small label summary, if needed
    if (lastSmallLoX != null) {

        var sleft = lastSmallLoX;
        var swidth = lastSmallHiX - lastSmallLoX;
        if (sleft + swidth >= -0.01 && 1.01 > sleft) {

            var gapX0 = sleft - LABEL_INDICATOR_OVERHANG;
            var gapWidth= swidth + 2 * LABEL_INDICATOR_OVERHANG;
            var gapY0 = ymid + LABEL_HEIGHT / 2 + LABEL_INDICATOR / 2;
            var gapHeight = LABEL_INDICATOR / 2;

            setColor(lastSmallHasGap ? COLOR_SMALL_GAP : COLOR_SMALL_LABEL);
            drawQuad(true, gapX0, gapY0, gapWidth, gapHeight);

            setColor(averageColor(lastSmallColors));
            drawQuad(true,
                     sleft, ymid,
                     swidth, LABEL_HEIGHT / 2);

            // Draw tooltip if mouse is hovering over small gap indicator
            var mouseOverGapIndicator = G_mousePos && gapX0 <= G_mousePos.x && G_mousePos.x <= gapX0 + gapWidth
                && gapY0 - gapHeight <= G_mousePos.y && G_mousePos.y <= gapY0;

            if (mouseOverGapIndicator && readyForTooltip(TT_DELAY_SUMMARY)) {
                updateToolTip({ text: lastSmallHasGap ? TT_SUMMARY_WITH_GAP : TT_SUMMARY_WITHOUT_GAP });
            }
        }
    }
    lastSmallLoX = null;
    lastSmallHiX = null;

    // Turn the label text yellow if the user is hovering over the label
    if (mouseOnLabel) {
        drawText(mouseOnLabel.text, mouseOnLabel.textx, mouseOnLabel.texty, "left", "middle", mouseOnLabel.maxtextwidth, "#ffff88", 18, true);
    }

    var clickedOnLabelName = drawLabelName(labelsetName, ymid, true);
    if (clickedOnLabelName && G_mouseAction === MOUSE_COPY_LABEL) {
        updateLabelsLocal(true, labels);
        G_mouseAction = MOUSE_COPY_LABEL_COMPLETE;
    }
}

function drawMidnights(zoom) {
    var dates = (G_config.length / G_config.sample_rate) / (60 * 60 * 24) + 2;

    for (var date = 0; date < dates; ++ date) {
        var dt = new Date(G_config.start_time_ms); // this resets to the initial year/month
        dt.setUTCDate(dt.getUTCDate() + date);
        dt.setUTCHours(0);
        dt.setUTCMinutes(0);
        dt.setUTCSeconds(0);
        dt.setUTCMilliseconds(0);

        var sample = ((dt.getTime() - G_config.start_time_ms) / 1000) * G_config.sample_rate;

        if (0 <= sample && sample <= G_config.length) {
            var smpx = G_xScale * (G_xOffset + (sample / zoom)) + X_OFFSET;

            setColor(G_modeColorMap.midnight);
            drawQuad(false,
                     smpx - REALLY_TINY_SIZE / 2, G_plotY[0],
                     REALLY_TINY_SIZE, G_plotHeight / 2);
        }
    }
}

function drawTime(sample, elsc, elms, includesample, zoom, ymid, yheight, mouseHover, showDayCount, withDurationFromSample) {
    var smpx = G_xScale * (G_xOffset + (sample / zoom)) + X_OFFSET;

    if (mouseHover) {
        //Draws the range axis on mouse over as well
        drawQuad(false,
                 smpx - REALLY_TINY_SIZE / 2, G_plotY[0],
                 REALLY_TINY_SIZE, G_plotHeight / 2);
        drawRangeAxisMarkers(smpx);
    }

    drawQuad(true,
             smpx - TINY_SIZE / 2, ymid,
             TINY_SIZE, yheight);

    var textPos = smpx + TEXT_INSET;

    if (withDurationFromSample !== false && sample != withDurationFromSample) {
        var durationString = "[" + durationStringFromSamples(Math.abs(sample - withDurationFromSample)) + "]";
        drawText(durationString, textPos, ymid, "left", "middle", undefined, COLORH_DURATION_TEXT, 14);
        textPos += measureTextWidth(durationString, 14) + TEXT_INSET;
    }

    var displayString = dateStringFromSample(sample, includesample, elsc, elms);

    // Get day count for the given sample
    if (showDayCount) {
        var sampleDate = new Date(G_config.start_time_ms + (1000 * (sample / G_config.sample_rate)));
        var dayCount = G_startDayIdx + datediff(G_startDate, sampleDate);
        displayString = "Day " + dayCount + ": " + displayString;
    }

    drawText(displayString, textPos, ymid, "left", "middle", undefined, COLORH_TIMELINE_TEXT, 14);
    textPos += measureTextWidth(displayString, 14) + 2 * TEXT_INSET;

    return textPos;
}

function checkMouseOnLabelEdge() {
    G_mouseAdjust = null;

    const DELTA = 0.003;

    let y_mid = (G_plotY[0] - G_plotHeight / 2 - LABEL_GAP - LABEL_INDICATOR - LABEL_HEIGHT / 2 - TIMELINE_HEIGHT);
    if (!G_mousePos || G_mousePos.y < y_mid - LABEL_HEIGHT / 2 || G_mousePos.y > y_mid + LABEL_HEIGHT / 2) {
        G_glCanvas.style.cursor = "default";
        return;
    }

    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    var closest = null;
    var closestLeft = null;
    var closestRight = null;
    for (var ll = 0; ll < G_labelsLocal.length; ++ ll) {
        const label = G_labelsLocal[ll];

        var lo = G_xScale * (G_xOffset + (label.lo / zoom)) + X_OFFSET;
        var dlo = Math.abs(G_mousePos.x - lo);
        if (dlo <= DELTA && (closest === null || dlo < closest)) {
            closest = dlo;
            closestLeft = null;
            closestRight = ll;
            if (ll - 1 >= 0 && G_labelsLocal[ll - 1].hi === label.lo) {
                closestLeft = ll - 1;
            }
        }

        var hi = G_xScale * (G_xOffset + (label.hi / zoom)) + X_OFFSET;
        var dhi = Math.abs(G_mousePos.x - hi);
        if (dhi <= DELTA && (closest === null || dhi < closest)) {
            closest = dhi;
            closestLeft = ll;
            closestRight = null;
            if (ll + 1 < G_labelsLocal.length && G_labelsLocal[ll + 1].lo == label.hi) {
                closestRight = ll + 1;
            }
        }
    }

    if (closest === null) {
        G_glCanvas.style.cursor = "default";
    } else {
        G_mouseAdjust = { left: null, right: null};
        if (closestLeft !== null) {
            G_mouseAdjust.left = {
                lo: G_labelsLocal[closestLeft].lo,
                hi: G_labelsLocal[closestLeft].hi,
                lname: G_labelsLocal[closestLeft].lname,
                detail: G_labelsLocal[closestLeft].detail,
                index: closestLeft
            }
        }
        if (closestRight !== null) {
            G_mouseAdjust.right = {
                lo: G_labelsLocal[closestRight].lo,
                hi: G_labelsLocal[closestRight].hi,
                lname: G_labelsLocal[closestRight].lname,
                detail: G_labelsLocal[closestRight].detail,
                index: closestRight
            }
        }
        G_glCanvas.style.cursor = "ew-resize";
    }
}

// Draw the axes on the canvas for the plot
function drawAxes(left, right) {
    setColor(G_modeColorMap.rangeAxis);

    // Draw the range-axis
    drawQuad(false,
             RANGE_AXIS_POS, G_plotY[0],
             REALLY_TINY_SIZE, G_plotHeight/2);
    drawRangeAxisMarkers(RANGE_AXIS_POS)

    setColor(G_modeColorMap.xaxis);

    // Draw the x-axis
    drawQuad(false,
             left, G_plotY[0] + G_rangeInfo.plotOffset,
             right - left, REALLY_TINY_SIZE);
}

// Draw the indicator bar. Pass parameters of the left and right end point of the highlight.
function drawIndicatorBar(zoom) {
    const YMID = 0.025;
    const HEIGHT = 0.05;
    const MIN_SIZE = 0.005;

    setColor(COLOR_TIMELINE, 0.5);
    drawQuad(true,
             0.0, YMID,
             1.0, HEIGHT / 2);

    var smplo = Math.round((0.0 - X_OFFSET) / G_xScale - G_xOffset);
    var smphi = Math.round((1.0 - X_OFFSET) / G_xScale - G_xOffset);
    var barlo = clamp(smplo / (G_config.length / zoom), 0.0, 1.0);
    var barhi = clamp(smphi / (G_config.length / zoom), 0.0, 1.0);
    if (barhi - barlo < MIN_SIZE) {
        barlo = 0.5 * (barhi + barlo) - MIN_SIZE / 2.0;
        barhi = barlo + MIN_SIZE;
    }
    setColor(COLOR_TIMELINE, 1.5);
    drawQuad(true,
             barlo, YMID,
             barhi - barlo, HEIGHT / 2);

    if (G_zoomInHistory) {
        var hbarlo = clamp(G_zoomInHistory.smplo / G_config.length, 0.0, 1.0);
        var hbarhi = clamp(G_zoomInHistory.smphi / G_config.length, 0.0, 1.0);
        if (hbarhi - hbarlo < MIN_SIZE) {
            hbarlo = 0.5 * (hbarhi + hbarlo) - MIN_SIZE / 2.0;
            hbarhi = hbarlo + MIN_SIZE;
        }

        setColor(COLOR_TIMELINE);
        drawQuad(true,
                 hbarlo, YMID - HEIGHT * 1 / 3,
                 hbarhi - hbarlo, HEIGHT / 6);
    }
}

// This draws the range axis markers and its labels.
// if the argument is RANGE_AXIS_POS it only draws at the ordinate position.
// On mouse over it is drawn at the mouse position on canvas.
function drawRangeAxisMarkers(smpx) {
    var nMarkers = 1;

    var totalRange = G_rangeInfo.rmax - G_rangeInfo.rmin;
    if (Math.round(totalRange) === totalRange && totalRange > 1) {
        if (totalRange % 8 == 0) {
            nMarkers = 8;
        } else if (totalRange % 4 === 0) {
            nMarkers = 4;
        } else if (totalRange % 2 === 0) {
            nMarkers = 2;
        }
    }

    // this will add a marker at 0 if the range is symmetric around 0
    if (nMarkers === 1 && G_rangeInfo.rmax + G_rangeInfo.rmin === 0) {
        nMarkers = 2;
    }

    var markerDistance = G_plotHeight / nMarkers;

    for(var ii = 0; ii <= nMarkers; ++ ii) {
        drawQuad(false,
                 smpx - RANGE_AXIS_TICK, G_plotY[0] - G_plotHeight / 2 + (markerDistance * ii),
                 RANGE_AXIS_TICK, REALLY_TINY_SIZE);
    }

    var range_unit = (G_rangeInfo.unit === null ? "" : G_rangeInfo.unit);
    drawText((G_rangeInfo.rmax > 0 ? "+" : "") + G_rangeInfo.rmax + range_unit, smpx - RANGE_AXIS_TICK, G_plotY[0] + G_plotHeight / 2, "right", "top", undefined, G_modeColorMap.rangeAxisText, 14);
    drawText((G_rangeInfo.rmin > 0 ? "+" : "") + G_rangeInfo.rmin + range_unit, smpx - RANGE_AXIS_TICK, G_plotY[0] - G_plotHeight / 2, "right", "bottom", undefined, G_modeColorMap.rangeAxisText, 14);
}


// Draw the horizontal timeline
function drawTimeline(left, right, ymid, yheight, mylo, myhi) {
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    setColor(COLOR_TIMELINE, 0.5);
    drawQuad(true,
             0.0, ymid,
             1.0, yheight);

    setColor(COLOR_TIMELINE);
    drawQuad(true,
             left, ymid,
             right - left, yheight);

    var considerMouseOverTimeline = ((G_mousePos && mylo <= G_mousePos.y && G_mousePos.y <= myhi) || G_mouseAction === MOUSE_PAN || G_mouseAction === MOUSE_CREATE_LABEL);

    var mouseTextEnd = -1.0;
    if (G_mousePos && left <= G_mousePos.x && G_mousePos.x <= right && considerMouseOverTimeline) {
        var sample = Math.round(((G_mousePos.x - X_OFFSET) / G_xScale) - G_xOffset) * zoom;
        if (sample >= 0 && sample < G_config.length) {
            setColor(G_modeColorMap.rangeAxis);
            mouseTextEnd = drawTime(sample, false, false, true, zoom, ymid, yheight, true, true, G_mouseDown);
        }
    }

    if (G_config.start_time_ms) { // maybe unneeded check
        var SCALES = getScales(G_config.sample_rate);

        var scale = SCALES[0];
        for (var ii = 1; ii < SCALES.length; ++ ii) {
            if (G_xScale * (scale[2] / zoom) > 0.20) {
                break;
            }
            scale = SCALES[ii];
        }

        var elsc = scale[0];
        var elms = scale[1];
        var scalesmp = scale[2];

        var startSample = (G_config.start_time_ms + (1000 * 60 * 60 * 19)) * G_config.sample_rate / 1000; // TODO: offset?
        var startOffset = scalesmp - (startSample % scalesmp);

        var losmp = (((0.0 - X_OFFSET) / G_xScale) - G_xOffset) * zoom;
        losmp = Math.max(0, losmp);
        losmp = Math.floor(losmp / scalesmp) * scalesmp + startOffset;
        if (losmp >= scalesmp) {
            losmp -= scalesmp;
        }
        var hismp = losmp + (6 * scalesmp);
        hismp = Math.min(hismp, G_config.length - scalesmp / 4);

        setColor(COLOR_TIMELINE_TEXT);
        for (var smp = losmp; smp < hismp; smp += scalesmp) {
            var skip = false;
            var smpx = G_xScale * (G_xOffset + (smp / zoom)) + X_OFFSET;
            if (G_mousePos && considerMouseOverTimeline && smpx < mouseTextEnd && G_mousePos.x <= smpx + 0.12 && left <= G_mousePos.x && G_mousePos.x <= right && considerMouseOverTimeline) {
                skip = true;
            }

            if (!skip) {
                drawTime(smp, elsc, elms, false, zoom, ymid, yheight, false, true, false);
            }
        }
    }
}

function drawScene() {
    window.requestAnimationFrame(doDrawScene);

    // Restore focus to the document body, unless specified otherwise
    if (document.activeElement !== document.getElementById('datasetsdropdown')
        && document.activeElement !== document.getElementById('labelsetsdropdown')
        && document.activeElement !== document.getElementById('newlabelset')) {
        document.activeElement.blur();
    }

}

// Render the page
function doDrawScene() {
    G_glCtx.clearColor(0.0, 0.0, 0.0, 0.0);
    G_glCtx.clear(G_glCtx.COLOR_BUFFER_BIT);

    G_overCtxOffscreen.clearRect(0, 0, G_canvasWidth, G_canvasHeight);
    G_underCtxOffscreen.fillStyle = getColorString(COLOR_CANVAS_BACKGROUND);
    G_underCtxOffscreen.fillRect(0, 0, G_canvasWidth, G_canvasHeight);

    if (!G_config) {
        G_overCtx.clearRect(0, 0, G_canvasWidth, G_canvasHeight);
        G_underCtx.fillStyle = getColorString(COLOR_CANVAS_BACKGROUND);
        G_underCtx.fillRect(0, 0, G_canvasWidth, G_canvasHeight);
        return;
    }

    G_tooltipInfo = null;

    // Draw the border of the main image
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    var left  = Math.max(0.0, G_xScale * (G_xOffset + 0) + X_OFFSET);
    var right = Math.min(1.0, G_xScale * (G_xOffset + ((G_config.length - 1) / zoom)) + X_OFFSET);

    // Sensor visibility might change, so update range info
    updateRangeInfo()

    G_underCtxOffscreen.fillStyle = getColorString(G_modeColorMap.border);
    G_underCtxOffscreen.fillRect((0.0) * G_canvasWidth, (1.0 - G_plotY[0] - G_plotHeight / 2) * G_canvasHeight,
                                 (1.0) * G_canvasWidth, (G_plotHeight) * G_canvasHeight);

    G_underCtxOffscreen.fillStyle = getColorString(G_modeColorMap.background);
    G_underCtxOffscreen.fillRect((left) * G_canvasWidth, (1.0 - G_plotY[0] - G_plotHeight / 2) * G_canvasHeight,
                                 (right - left) * G_canvasWidth, (G_plotHeight) * G_canvasHeight);

    // Draw the midnight marker
    drawMidnights(zoom);

    // Draw the axes to show magnitude.
    drawAxes(left, right);

    // Draw the indicator bar with highlight suggesting where in the data set you are.
    drawIndicatorBar(zoom);

    // Draw the timestamps (behind the plot)
    drawTimeline(left, right, G_plotY[0] - G_plotHeight / 2 - TIMELINE_HEIGHT / 2, TIMELINE_HEIGHT / 2, G_plotY[0] - G_plotHeight / 2 - TIMELINE_HEIGHT, G_plotY[0] + G_plotHeight / 2);

    // Scissor box to clip the plot
    G_glCtx.enable(G_glCtx.SCISSOR_TEST);
    G_glCtx.scissor(0, G_canvasHeight * (G_plotY[0] - G_plotHeight / 2),
                 G_canvasWidth, G_canvasHeight * G_plotHeight);

    // Load the tiles to be drawn if necessary
    var tileIndex = -Math.floor((G_xOffset + X_OFFSET / G_xScale) / G_config.tile_size);
    var lastImageEndX = new Map();
    for (var tt = -1; tt <= 3; ++ tt) {
        if (G_zoomLevel > 0) {
            for (var ff = 0; ff < G_config.tile_subsample; ++ ff) {
                fetchTileIfNeeded(G_zoomLevel - 1, Math.floor((tileIndex + tt) * G_config.tile_subsample + ff));
            }
        }
        if (G_zoomLevel < G_config.zoom_max) {
            for (var ff = -1; ff <= 1; ++ ff) {
                fetchTileIfNeeded(G_zoomLevel + 1, Math.floor((tileIndex + tt) / G_config.tile_subsample + ff));
            }
        }

        fetchTileIfNeeded(G_zoomLevel, tileIndex + tt);
        drawTile(G_zoomLevel, tileIndex + tt, G_fetchingLabelsLocal);
        drawTileImages(G_zoomLevel, tileIndex + tt, G_fetchingLabelsLocal, lastImageEndX);
    }

    G_glCtx.disable(G_glCtx.SCISSOR_TEST);

    if (extension_onDraw != null) {
        extension_onDraw();
    }

    var displayedlabels = 0;
    var anyNotDisplayed = false;
    var highlightRange = {};

    var labelY = G_plotY[0] - G_plotHeight / 2 - LABEL_GAP - LABEL_INDICATOR - LABEL_HEIGHT / 2 - TIMELINE_HEIGHT;
    const LABEL_ADVANCE = -(LABEL_GAP + LABEL_INDICATOR + LABEL_HEIGHT);

    // Draw your local labels
    drawLabels("Yours (" + G_labelset + ")", labelY, G_labelsLocal, highlightRange);
    labelY += LABEL_ADVANCE;

    // Draw your remote labels
    if (G_labelsRemoteYours) {
        var labels = G_labelsRemoteYours;
        var labelsetName = "Yours (last saved)";

        if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
            drawLabels(labelsetName, labelY, labels.labels, highlightRange);
            labelY += LABEL_ADVANCE;
            ++ displayedlabels;
        } else {
            anyNotDisplayed = true;
        }
    }

    for (var ll = 0; ll < G_labelsRemoteNotes.length; ++ ll) {
        var index = ll;
        var labels = G_labelsRemoteNotes[index];

        var labelsetName = labels.labelset.substring(0, 5);
        if (labels.source) {
            labelsetName = labels.source.substring(0, 6) + " " + labelsetName;
        }

        if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
            drawLabels(labelsetName, labelY, labels.labels, highlightRange);
            labelY += LABEL_ADVANCE;
            ++ displayedlabels;
        } else {
            anyNotDisplayed = true;
        }
    }

    // Draw ground truth labels
    if (G_drawGroundTruth) {
        if (G_labelsRemoteGroundTruth !== null) {
            if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
                drawLabels("Truth", labelY, G_labelsRemoteGroundTruth.labels, highlightRange);
                labelY += LABEL_ADVANCE;
                ++ displayedlabels;
            } else {
                anyNotDisplayed = true;
            }
        }
    }

    // Draw algorithm labels
    for (var ll = 0; ll < G_labelsRemoteAlgo.length; ++ll) {
        if (shouldFetchSource(SOURCE_PLAYER) && ll >= MAX_REMOTE_LABEL_ALGO_DISPLAY) {
            anyNotDisplayed = true;
            break;
        }

        var index = (ll + G_labelsRemoteStartIndexAlgo) % G_labelsRemoteAlgo.length;
        var labels = G_labelsRemoteAlgo[index];

        var labelsetName = labels.labelset.substring(0, 5);
        if (labels.source) {
            labelsetName = labels.source.substring(0, 6) + " " + labelsetName;
        }

        if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
            drawLabels(labelsetName, labelY, labels.labels, highlightRange);
            labelY += LABEL_ADVANCE;
            ++displayedlabels;
        } else {
            anyNotDisplayed = true;
        }
    }

    // Draw remote player labels
    for (var ll = 0; ll < G_labelsRemoteOtherPlayer.length; ++ ll) {
        var index = (ll + G_labelsRemoteStartIndexPlayer) % G_labelsRemoteOtherPlayer.length;
        var labels = G_labelsRemoteOtherPlayer[index];

        var labelsetName = labels.labelset.substring(0, 5);
        if (labels.source) {
            labelsetName = labels.source.substring(0, 6) + " " + labelsetName;
        }

        if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
            drawLabels(labelsetName, labelY, labels.labels, highlightRange);
            labelY += LABEL_ADVANCE;
            ++ displayedlabels;
        } else {
            anyNotDisplayed = true;
        }
    }

    // Draw more labels indicator
    if (anyNotDisplayed) {
        drawLabelName("(more...)", labelY + LABEL_INDICATOR, false);
    }

    if (highlightRange.lo !== undefined && highlightRange.hi !== undefined) {
        setColor(G_modeColorMap.rangeAxis);
        drawQuad(false,
                 G_xScale * (G_xOffset + highlightRange.lo / zoom) + X_OFFSET, G_plotY[0],
                 G_xScale * (highlightRange.hi - highlightRange.lo) / zoom, G_plotHeight / 2);
    }


    // Draw the box the user is selecting
    var pendingLabels = getPendingLabels();
    for (var ll = 0; ll < pendingLabels.length; ++ ll) {
        const lbl = pendingLabels[ll];

        var color = getLabelColor(lbl.lname);
        setColor(color, 1.2);
        drawQuad(false,
                 G_xScale * (G_xOffset + lbl.lo / zoom) + X_OFFSET, G_plotY[0],
                 G_xScale * (lbl.hi - lbl.lo) / zoom, G_plotHeight / 2);
        drawQuad(true,
                 G_xScale * (G_xOffset + lbl.lo / zoom) + X_OFFSET, G_plotY[0] - G_plotHeight / 2 - TIMELINE_HEIGHT - LABEL_GAP - LABEL_INDICATOR - LABEL_HEIGHT / 2,
                 G_xScale * (lbl.hi - lbl.lo) / zoom, LABEL_HEIGHT / 2);
    }

    if (G_mouseAction === MOUSE_COPY_LABEL) {
        G_mouseAction = MOUSE_COPY_LABEL_COMPLETE;
    }

    checkChannelTooltip();

    // Draw tooltip if needed
    drawTooltip(G_tooltipInfo);

    // draw offscreen canvases
    G_overCtx.clearRect(0, 0, G_canvasWidth, G_canvasHeight);
    G_overCtx.drawImage(G_overCanvasOffscreen, 0, 0);

    G_underCtx.clearRect(0, 0, G_canvasWidth, G_canvasHeight);
    G_underCtx.drawImage(G_underCanvasOffscreen, 0, 0);

}

// Generate a random id
function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
                                                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
}

// Generate a random id
function makeId() {
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

    var text = '';
    for (var ii = 0; ii < 9; ++ii) {
        var rnd = crypto.getRandomValues(new Uint8Array(1))[0] / 255.0;
        text += possible.charAt(clamp(Math.floor(rnd * possible.length), 0, possible.length - 1));
    }

    var check = 0;
    for (var ii = 0; ii < text.length; ++ii) {
        check += text.charCodeAt(ii);
    }
    text += (check % 16).toString(16).toUpperCase();

    return text;
}

function loadDataset(dataset, labelset) {
    window.location.href = 'signaclient.html?labelset=' + labelset + '&dataset=' + dataset;
}

function loadPage(page) {
    window.location.href = page;
}

// Get the id of the given tile at the given zoom level
function getTileId(zoomLevel, tile) {
    return "z" + zoomLevel.toString().padStart(2, '0') + "t" + tile.toString().padStart(6, '0');
}

function getZoomLevel() {
    return (G_zoomLevel != null && G_zoomLevelIntermediate != null) ? this.G_zoomLevel.toString() + ':' + this.G_zoomLevelIntermediate.toString().padStart(2, '0') : ''
}

function getAmountOfTimeVisibleString() {
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
    var smplo = zoom * Math.round((0.0 - X_OFFSET) / G_xScale - G_xOffset);
    var smphi = zoom * Math.round((1.0 - X_OFFSET) / G_xScale - G_xOffset);
    var smploc = clamp(smplo, 0, G_config.length);
    var smphic = clamp(smphi, 0, G_config.length);

    var smpSeconds = (smphi - smplo) / G_config.sample_rate;
    var visibleSeconds = (smphic - smploc) / G_config.sample_rate;
    if (smpSeconds >= 60 * 60 * 24) {
        return (visibleSeconds / (60 * 60 * 24)).toFixed(1) + ' days';
    } else if (smpSeconds >= 60 * 60) {
        return (visibleSeconds / (60 * 60)).toFixed(1) + ' hours';
    } else if (smpSeconds >= 60) {
        return (visibleSeconds / (60)).toFixed(1) + ' minutes';
    } else {
        return (visibleSeconds).toFixed(1) + ' seconds';
    }
}

function updateMessageDisplay() {
    var message = getAmountOfTimeVisibleString();
    showText("message", message);
}

function genericLogObject() {
    return {
        time: Date.now(),
        dataset: G_dataset,
        labelset: G_labelset,
        run: G_run,
        token: makeId()
    };
}

// Send the given data to the server
function sendLabels() {
    var data = genericLogObject();
    data.source = G_source;
    data.labels = G_labelsLocal;

    requestToServer('reportlabels', data, 3, onSendLabelsSuccess, onSendLabelsError);
}

function onSendLabelsError() {
    alert("Error contacting server. Please reconnect to the internet and then Save and update.");
}

function onSendLabelsSuccess(response) {
    G_labelsRemoteYours = JSON.parse(response);
}

// Send the given data to the server
function sendLog(type, info) {
    var data = genericLogObject();
    data.type = type;
    data.info = info;

    requestToServer('log', data, 0, null, null, null);
}

// Return the average color from the map of label weights
function averageColor(labels) {
    var rr = 0.0;
    var gg = 0.0;
    var bb = 0.0;
    var total = 0.0;

    for (var lbl in labels) {
        var weight = labels[lbl];
        var clr;
        if (lbl === 'NONE') {
            clr = [0.0, 0.0, 0.0];
        } else {
            clr = getLabelColor(lbl);
        }
        rr += weight * clr[0];
        gg += weight * clr[1];
        bb += weight * clr[2];
        total += weight;
    }

    if (total < 0.001) {
        return [0.0, 0.0, 0.0];
    } else {
        return [rr / total, gg / total, bb / total];
    }
}

function addLabel(labels, label, weight) {
    if (labels[label] === undefined) {
        labels[label] = 0.0;
    }
    labels[label] += weight;
}

function pad(number) {
    if (number < 10) {
        return '0' + number;
    }
    return number;
}

// Returns the number of days between the given start and end Date objects
function datediff(start, end) {
    var startDate = new Date(start.getUTCFullYear(), start.getUTCMonth(), start.getUTCDate());
    var endDate = new Date(end.getUTCFullYear(), end.getUTCMonth(), end.getUTCDate());
    var diffInMilliseconds = endDate - startDate;
    return Math.round(diffInMilliseconds / (1000 * 60 * 60 * 24));
}

function dateStringFromSample(sample, includesample, elsc, elms) {
    var ret = null;
    if (G_config.start_time_ms) { // maybe unneeded check
        var dt = new Date(G_config.start_time_ms + (1000 * (sample / G_config.sample_rate)));
        var dy = dt.getUTCDay();
        var hr = dt.getUTCHours() > 12 ? dt.getUTCHours() - 12 : dt.getUTCHours();
        hr = hr === 0 ? 12 : hr;
        var ampm = dt.getUTCHours() > 11 ? "PM" : "AM";
        var mn = dt.getUTCMinutes();
        var sc = dt.getUTCSeconds();
        var ms = dt.getUTCMilliseconds();

        ret = "";

        ret += WEEKDAY[dy] + " ";
        ret += pad(hr) + ":" + pad(mn);
        if (!elsc || sc !== 0) {
            ret += ":" + pad(sc);
        }
        if (!elms || ms !== 0) {
            ret += "." + (ms / 1000).toFixed(3).slice(2, 5);
        }
        ret += " " + ampm;

        if (ret.indexOf("NaN") !== -1) {
            ret = null;
        }
    }

    if (ret == null) {
        ret = "" + sample;
    } else if (includesample) {
        ret = ret + " (" + sample + ")";
    }
    return ret;
}

// Get scales
function getScales(sampleRate) {
    return [[0, 0, sampleRate],
            [0, 1, sampleRate * 2],
            [0, 1, sampleRate * 5],
            [0, 1, sampleRate * 10],
            [0, 1, sampleRate * 30],

            [0, 1, sampleRate * 60],
            [1, 1, sampleRate * 60 * 2],
            [1, 1, sampleRate * 60 * 5],
            [1, 1, sampleRate * 60 * 10],
            [1, 1, sampleRate * 60 * 30],

            [1, 1, sampleRate * 60 * 60],
            [1, 1, sampleRate * 60 * 60 * 2],
            [1, 1, sampleRate * 60 * 60 * 5],
            [1, 1, sampleRate * 60 * 60 * 10],

            [1, 1, sampleRate * 60 * 60 * 24],
            [1, 1, sampleRate * 60 * 60 * 24 * 2],
            [1, 1, sampleRate * 60 * 60 * 24 * 5]
           ];
}

// Return the color associated with the given sensor
function getSensorColor(sname) {
    var color = G_sensorColors[sname];
    if (color == undefined) {
        color = COLOR_UNKNOWN;
    }
    return color;
}

// Return the color associated with the given channel
function getChannelColor(cname) {
    var color = G_channelColors[cname];
    if (color == undefined) {
        color = COLOR_UNKNOWN;
    }
    return color;
}

// Return the color associated with the given label
function getLabelColor(lname) {
    var color = G_labelColors[lname];
    if (color == undefined) {
        color = COLOR_UNKNOWN;
    }
    return color;
}

// multiple two colors
function multiplyColors(c0, c1) {
    return [c0[0] * c1[0], c0[1] * c1[1], c0[2] * c1[2]];
}

// Return a string of the rgb value of the given color
function getColorString(color) {
    var rr = Math.round(Math.min(255, color[0] * 255));
    var gg = Math.round(Math.min(255, color[1] * 255));
    var bb = Math.round(Math.min(255, color[2] * 255));
    var colorString = '#' + rr.toString(16).padStart(2, '0') + gg.toString(16).padStart(2, '0') + bb.toString(16).padStart(2, '0');
    return colorString;
}

// Display the given text on the page in the textarea
function showText(id, text) {
    document.getElementById(id).innerHTML = text;
}

// Return data array to init quad buffer
function getQuadBufferData() {
    return [0.0,  1.0,
            0.0, -1.0,
            1.0, -1.0,
            1.0, 1.0];
}

function logTick() {
    data = {
        tilesLoaded: noOfTilesLoaded(),
        zoom: [G_zoomLevel, G_zoomLevelIntermediate]
    };

    sendLog('tick', data);
}

// Returns the no of tiles loaded till now.
function noOfTilesLoaded() {
    return G_tileData.size;
}

function getWorldMousePos(evt, g_glCanvas) {
    var rect = g_glCanvas.getBoundingClientRect();

    var x = (evt.clientX - rect.left) / g_glCanvas.width;
    var y = 1.0 - (evt.clientY - rect.top) / g_glCanvas.height;
    x = clamp(x, 0.0, 1.0);
    y = clamp(y, 0.0, 1.0);

    return { x: x, y: y };
}

function debugLogMessage(msg) {
    console.debug(msg);
}

// Updates the access time log in map objects and clears cache if exceeded.
function updateAccess(tileId) {
    let currentTimeStamp = new Date();
    let tileData = G_tileData.get(tileId);
    tileData["timestamp"] = currentTimeStamp;
    G_tileData.set(tileId, tileData);

    // Checks if cache needs to be cleared.
    if (G_tileData.size > G_cacheMax) {
        clearCache();
    }
}

// Clears the oldest cache.
function clearCache() {
    let oldestTimeStamp = new Date();
    let tileIdToBeDeleted;
    let tileBuffers;
    for (let [key, value] of G_tileData) {
        let tileId = key;
        let tileData = value;
        if (tileData.timestamp < oldestTimeStamp) {
            tileIdToBeDeleted = tileId;
            oldestTimeStamp = tileData.timestamp;
        }
    }

    // Deletes the buffers if the tile to be deleted had buffers.
    tileBuffers = G_tileData.get(tileIdToBeDeleted).buffers;
    if (typeof tileBuffers != 'undefined'){
        for (let i = 0; i < tileBuffers.length; i++){
            for (let j = 0; j < tileBuffers[i].length; j++){
                if (G_glCtx.isBuffer(tileBuffers[i][j])){
                    G_glCtx.deleteBuffer(tileBuffers[i][j]);
                }
            }
        }
    }

    G_tileData.delete(tileIdToBeDeleted);
}

// let timeAfterWhichCacheIsCleared = (delay) => {return new Date(new Date().getTime() - delay*60000)};

// // Clears the cache size to G_cacheMax/2.
// function clearCache() {
//     let localDelay = G_cacheDelay;
//     while (G_tileData.size > (G_cacheMax/2)) {
//         removeTilesFromCache(timeAfterWhichCacheIsCleared(localDelay));
//         localDelay /= 2;
//     }
// }

// // Removes all the tiles with access time before the delay.
// function removeTilesFromCache(timeDelay) {
//     let entries = G_tileData.entries();
//     for (let [key, value] of G_tileData){
//         let tileId = key;
//         let tileData = value;
//         if (tileData.timestamp < timeDelay) {
//             G_tileData.delete(tileId);
//         }
//     }
// }
