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
    'e': currentPen.parse('toggle-eraser'),
    'c': currentPen.parse('clear'),
    'Shift+c': () => {
        clearCanvas();
        for (const penName in pens) {
            pens[penName].artist.clear();
            pens[penName].history.takeSnapshot();
        }
    },
    '.': currentPen.parse('next-color'),
    ',': currentPen.parse('previous-color'),
    ']': currentPen.parse('increase-brush-size'),
    '[': currentPen.parse('decrease-brush-size'),
    'Shift+>': () => currentPen.parse('increase-sensitivity'),
    'Shift+<': () => currentPen.parse('decrease-sensitivity'),
    'u Meta+z': currentPen.parse('undo'),
    'Control+r Meta+Shift+z': currentPen.parse('redo'),
    'Escape Control+[': () => {
        snippetLibrary.isRecording = false;

        if (currentPen.enabled) {
            currentPen.cancel();
        }
    },
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
    's': currentPen.parse('select'),
    'y': currentPen.parse('yank'),
    'Shift+y': () => currentPen.parse('yank-with', globalClipboard),
    '~p': [
        () => currentPen.enabled,
        key => clipboardFor(key).paste(key)
    ],
    '~P': [
        () => currentPen.enabled,
        key => globalClipboard.paste(key)
    ],
    '~w': [
        () => currentPen.enabled && currentPen.selection.completed,
        key => {
            clipboardFor(key).register(key);
            currentPen.cancel();
        }
    ],
    'd': currentPen.parse('delete', 'd'),
    'Shift+d': currentPen.parse('delete-with', 'D', globalClipboard),
    '~x': [
        () => currentPen.enabled && currentPen.selection.completed,
        key => {
            currentPen.selection.delete(key, clipboardFor(key));
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

                pens[key].currentPoint = currentPen.currentPoint;

                currentPen = pens[key];
                snippetLibrary.changePen(currentPen);

                currentPenLabel.innerText = key;

                currentPen.enabled = true;

                currentPen.artist.clear();
                currentPen.brush.drawPreview();
                currentPen.history.travel(0);

                globalClipboard.changePen(currentPen);
            }
        }
    ]
};
