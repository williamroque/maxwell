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
const currentPenLabel = document.querySelector('#current-pen-label');

const artist = new Artist(canvas);
const backgroundArtist = new Artist(backgroundCanvas);
const penArtist = new Artist(penCanvas);
const penPreviewArtist = new Artist(penPreviewCanvas);
const selectionArtist = new Artist(selectionCanvas);

const defaultPenKey = 'm';

let pens = {};
pens[defaultPenKey] = new Pen(penArtist, penPreviewArtist, selectionArtist, defaultPenKey);

let currentPen = pens[defaultPenKey];

const globalClipboard = new Clipboard(currentPen, selectionArtist);

function clipboardFor(key) {
    if (isNaN(key) && key === key.toUpperCase())
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
    'Control+p': () => {
        if (currentPen.enabled) {
            currentPenLabel.innerText = '';
        } else {
            currentPenLabel.innerText = currentPen.name;
        }

        currentPen.toggle();
    },
    'e': () => currentPen.enabled ? currentPen.toggleEraser() : [],
    'c': () => currentPen.enabled ? currentPen.clear() : [],
    '.': () => currentPen.enabled ? currentPen.nextColor() : [],
    ',': () => currentPen.enabled ? currentPen.previousColor() : [],
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
    'y': () => currentPen.yank(currentPen.clipboard),
    'Shift+y': () => currentPen.yank(globalClipboard),
    '~P': [
        () => currentPen.enabled,
        key => globalClipboard.paste(key)
    ],
    'd': () => {
        if (currentPen.enabled && currentPen.movingSelection) {
            currentPen.deleteSelection('d', currentPen.clipboard);
        }
    },
    '~D': [
        () => currentPen.enabled && currentPen.movingSelection,
        key => {
            currentPen.deleteSelection(key, clipboardFor(key));
        }
    ],
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
        () => currentPen.enabled && currentPen.movingSelection,
        key => {
            clipboardFor(key).register(key);
            currentPen.cancel();
        }
    ],
    '~\'': [
        () => currentPen.enabled,
        key => {
            if (key && /^[A-Za-z0-9]$/.test(key)) {
                if (!(key in pens)) {
                    pens[key] = new Pen(penArtist, penPreviewArtist, selectionArtist, key);
                    pens[key].history.currentSnapshot = -1;
                    pens[key].clear();
                }

                currentPen.enabled = false;

                currentPen = pens[key];
                snippetLibrary.changePen(currentPen);

                currentPenLabel.innerText = key;

                currentPen.enabled = true;

                currentPen.artist.clear();
                currentPen.drawBrushPreview();
                currentPen.history.travel(0);

                globalClipboard.changePen(currentPen);
            }
        }
    ]
};
