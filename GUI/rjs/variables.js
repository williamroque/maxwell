const { ipcRenderer } = require('electron');
const fs = require('fs');
const { spawn } = require('child_process');

const canvas = document.querySelector('#python-canvas');
const ctx = canvas.getContext('2d');

const backgroundCanvas = document.querySelector('#background-canvas');
const bgCtx = backgroundCanvas.getContext('2d');

const artist = new Artist(canvas);
const backgroundArtist = new Artist(backgroundCanvas);

let sequence;

function clearCanvas(background=true) {
    artist.clear();

    if (background) {
        backgroundArtist.clear();
    }
}

const keymap = {
    'ctrl+c': () => sequence.stop(),
    'ctrl+u': clearCanvas,
    'ctrl+b': toggleBackground
};
