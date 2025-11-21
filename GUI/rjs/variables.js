const { ipcRenderer, remote, webFrame } = require('electron');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const canvas = document.querySelector('#main-canvas');
const backgroundCanvas = document.querySelector('#background-canvas');
const penCanvas = document.querySelector('#pen-canvas');
const penPreviewCanvas = document.querySelector('#pen-preview-canvas');
const selectionCanvas = document.querySelector('#selection-canvas');
const shapeCanvas = document.querySelector('#shape-canvas');
const latexCanvas = document.querySelector('#latex-canvas');

const htmlTree = new HTMLTree();

const keyPrompt = document.querySelector('#key-prompt');
const currentPenLabel = document.querySelector('#current-pen-label');

const textPrompt = document.querySelector('#text-prompt');

const artist = new Artist(canvas);
const backgroundArtist = new Artist(backgroundCanvas);
const penArtist = new Artist(penCanvas);
const penPreviewArtist = new Artist(penPreviewCanvas);
const selectionArtist = new Artist(selectionCanvas);
const shapeArtist = new Artist(shapeCanvas);
const latexArtist = new Artist(latexCanvas);

const defaultPenKey = 'm';

let pens = {};
pens[defaultPenKey] = new Pen(penArtist, penPreviewArtist, selectionArtist, shapeArtist, defaultPenKey, textPrompt, latexArtist);

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
