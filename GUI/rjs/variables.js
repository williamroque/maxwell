const { ipcRenderer, remote, webFrame } = require('electron');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const canvas = document.querySelector('#python-canvas');
const backgroundCanvas = document.querySelector('#background-canvas');
const penCanvas = document.querySelector('#pen-canvas');
const penPreviewCanvas = document.querySelector('#pen-preview-canvas');
const selectionCanvas = document.querySelector('#selection-canvas');

const keyPrompt = document.querySelector('#key-prompt');

const artist = new Artist(canvas);
const backgroundArtist = new Artist(backgroundCanvas);
const penArtist = new Artist(penCanvas);
const penPreviewArtist = new Artist(penPreviewCanvas);
const selectionArtist = new Artist(selectionCanvas);

const pen = new Pen(penArtist, penPreviewArtist, selectionArtist);

const snippetPath = path.join(process.env.HOME, '.maxwell_snippets.json');
const snippetLibrary = new SnippetLibrary(pen, snippetPath);

const defaultWidth = window.innerWidth;

let isZoom = false;

let awaitingEvent = false;

let sequence;

function clearCanvas(background=true) {
    artist.clear();

    if (background) {
        backgroundArtist.clear();
    }
}

const keymap = {
    'Control+c': () => sequence.stop(),
    'Control+u': clearCanvas,
    'Control+b': toggleBackground,
    'Control+p': pen.toggle.bind(pen),
    'e': () => pen.enabled ? pen.toggleEraser() : [],
    'c': () => pen.enabled ? pen.clear() : [],
    'n': () => pen.enabled ? pen.nextColor() : [],
    'p': () => pen.enabled ? pen.previousColor() : [],
    ']': () => pen.enabled ? pen.increaseBrushSize() : [],
    '[': () => pen.enabled ? pen.decreaseBrushSize() : [],
    'u Meta+z': () => pen.enabled ? pen.history.travel(-1) : [],
    'r Control+r Meta+Shift+z': () => pen.enabled ? pen.history.travel(1) : [],
    'l': () => {
        pen.activateLine();
    },
    'Shift+l': () => {
        if (pen.enabled) {
            if (pen.lineMode) {
                pen.cancel();
            } else {
                pen.lineMode = true;
                pen.activateLine();
            }
        }
    },
    's': () => {
        pen.activateSelection();
    },
    'Shift+s': () => {
        if (pen.enabled) {
            if (pen.selectionMode) {
                pen.cancel();
            } else {
                pen.selectionMode = true;
                pen.activateSelection();
            }
        }
    },
    'y': () => {
        pen.copyMode = true;
        pen.activateSelection();
    },
    'd Backspace': () => {
        if (pen.enabled) {
            pen.deleteSelection();
        }
    },
    'Escape Control+[': () => {
        snippetLibrary.isRecording = false;

        if (pen.enabled) {
            pen.cancel();
        }
    },
    'Shift+>': () => pen.enabled ? pen.increaseSensitivity() : [],
    'Shift+<': () => pen.enabled ? pen.decreaseSensitivity() : [],
    'Meta+Enter': () => {
        const window = remote.getCurrentWindow();
        window.setFullScreen(!window.isFullScreen());
        resizeCanvas();
    },
    '=': () => pen.enabled ? zoom(.2) : [],
    '-': () => pen.enabled ? zoom(-.2) : [],
    '0': () => pen.enabled ? zoom(1, false) : [],
    '~q': [
        snippetLibrary.record.bind(snippetLibrary),
        snippetLibrary.record.bind(snippetLibrary)
    ],
    '~,': [
        () => pen.enabled,
        snippetLibrary.play.bind(snippetLibrary)
    ]
};
