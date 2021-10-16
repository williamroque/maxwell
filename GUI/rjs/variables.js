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

let pens = {
    'm': new Pen(penArtist, penPreviewArtist, selectionArtist, 'm')
};
let currentPen = pens['m'];

const globalClipboard = new Clipboard(currentPen, selectionArtist);

function clipboardFor(key) {
    if (key === key.toUpperCase())
        return globalClipboard;
    return currentPen.clipboard;
}

const snippetPath = path.join(process.env.HOME, '.maxwell_snippets.json');
const snippetLibrary = new SnippetLibrary(currentPen, snippetPath);

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
    'Control+c': () => sequence ? sequence.stop() : [],
    'Control+u': clearCanvas,
    'Control+b': toggleBackground,
    'Control+p': () => currentPen.toggle(),
    'e': () => currentPen.enabled ? currentPen.toggleEraser() : [],
    'c': () => currentPen.enabled ? currentPen.clear() : [],
    'Shift+n': () => currentPen.enabled ? currentPen.nextColor() : [],
    'Shift+p': () => currentPen.enabled ? currentPen.previousColor() : [],
    ']': () => currentPen.enabled ? currentPen.increaseBrushSize() : [],
    '[': () => currentPen.enabled ? currentPen.decreaseBrushSize() : [],
    'u Meta+z': () => currentPen.enabled ? currentPen.history.travel(-1) : [],
    'Control+r Meta+Shift+z': () => currentPen.enabled ? currentPen.history.travel(1) : [],
    'l': () => {
        currentPen.activateLine();
    },
    'Shift+l': () => {
        if (currentPen.enabled) {
            if (currentPen.lineMode) {
                currentPen.cancel();
            } else {
                currentPen.lineMode = true;
                currentPen.activateLine();
            }
        }
    },
    's': () => {
        currentPen.activateSelection();
    },
    'Shift+s': () => {
        if (currentPen.enabled) {
            if (currentPen.selectionMode) {
                currentPen.cancel();
            } else {
                currentPen.selectionMode = true;
                currentPen.activateSelection();
            }
        }
    },
    'y': () => currentPen.yank(),
    'd Backspace': () => {
        if (currentPen.enabled) {
            currentPen.deleteSelection();
        }
    },
    'Escape Control+[': () => {
        snippetLibrary.isRecording = false;

        if (currentPen.enabled) {
            currentPen.cancel();
        }
    },
    'Shift+>': () => currentPen.enabled ? currentPen.increaseSensitivity() : [],
    'Shift+<': () => currentPen.enabled ? currentPen.decreaseSensitivity() : [],
    'Meta+Enter': () => {
        const window = remote.getCurrentWindow();
        window.setFullScreen(!window.isFullScreen());
        resizeCanvas();
    },
    '=': () => currentPen.enabled ? zoom(.2) : [],
    '-': () => currentPen.enabled ? zoom(-.2) : [],
    '0': () => currentPen.enabled ? zoom(1, false) : [],
    '~q': [
        () => snippetLibrary.record(),
        key => snippetLibrary.record(key),
    ],
    '~ ': [
        () => currentPen.enabled,
        key => snippetLibrary.play(key)
    ],
    '~p': [
        () => currentPen.enabled,
        key => clipboardFor(key).paste(key)
    ],
    '~w': [
        () => currentPen.enabled,
        key => clipboardFor(key).register(key)
    ],
    '~\'': [
        () => currentPen.enabled,
        key => {
            if (key && key !== 'Escape') {
                if (!(key in pens)) {
                    pens[key] = new Pen(penArtist, penPreviewArtist, selectionArtist, key);
                    pens[key].history.currentSnapshot = -1;
                    pens[key].clear();
                }

                currentPen.enabled = false;

                currentPen = pens[key];
                snippetLibrary.changePen(currentPen);

                currentPen.enabled = true;

                currentPen.artist.clear();
                currentPen.drawBrushPreview();
                currentPen.history.travel(0);

                globalClipboard.changePen(currentPen);
            }
        }
    ]
};
