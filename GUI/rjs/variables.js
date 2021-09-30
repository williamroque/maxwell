const { ipcRenderer, remote } = require('electron');
const fs = require('fs');
const { spawn } = require('child_process');

const canvas = document.querySelector('#python-canvas');
const backgroundCanvas = document.querySelector('#background-canvas');
const penCanvas = document.querySelector('#pen-canvas');
const penPreviewCanvas = document.querySelector('#pen-preview-canvas');
const selectionCanvas = document.querySelector('#selection-canvas');

const artist = new Artist(canvas);
const backgroundArtist = new Artist(backgroundCanvas);
const penArtist = new Artist(penCanvas);
const penPreviewArtist = new Artist(penPreviewCanvas);
const selectionArtist = new Artist(selectionCanvas);

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
    'Control+p': () => pen.toggle(),
    'e': () => pen.enabled ? pen.toggleEraser() : [],
    'c': () => pen.enabled ? pen.clear() : [],
    'n': () => pen.enabled ? pen.nextColor() : [],
    'p': () => pen.enabled ? pen.previousColor() : [],
    ']': () => pen.enabled ? pen.increaseBrushSize() : [],
    '[': () => pen.enabled ? pen.decreaseBrushSize() : [],
    'u': () => pen.enabled ? pen.history.travel(-1) : [],
    'r': () => pen.enabled ? pen.history.travel(1) : [],
    'l': () => {
        if (pen.enabled) {
            pen.drawingLine = true;
        }
    },
    's': () => {
        if (pen.enabled) {
            pen.isSelecting = true;
        }
    },
    'y': () => {
        if (pen.enabled) {
            pen.copyMode = true;
            pen.isSelecting = true;
        }
    },
    'Backspace': () => {
        if (pen.enabled) {
            pen.deleteSelection();
        }
    },
    'd': () => {
        if (pen.enabled) {
            pen.deleteSelection();
        }
    },
    'Escape': () => {
        if (pen.enabled) {
            pen.cancelSelection();
        }
    },
    'Control+[': () => {
        if (pen.enabled) {
            pen.cancelSelection();
        }
    },
    'Shift+>': () => pen.enabled ? pen.increaseSensitivity() : [],
    'Shift+<': () => pen.enabled ? pen.decreaseSensitivity() : [],
    'Meta+Enter': () => {
        const window = remote.getCurrentWindow();
        window.setFullScreen(!window.isFullScreen());
    }
};
