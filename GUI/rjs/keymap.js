function parseKeymapFor(pen) {
    let keymap = {};

    for (const keys in parsedPenKeymap) {
        const binding = parsedPenKeymap[keys];

        if (Array.isArray(binding)) {
            keymap[keys] = pen.parse(...binding);
        } else {
            keymap[keys] = pen.parse(binding);
        }
    }

    return keymap;
}

function clearCanvas(background=true) {
    artist.clear();

    if (background) {
        backgroundArtist.clear();
    }
}

const generalKeymap = {
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
    'Enter': () => {
        if (Properties.capture) {
            captureArea(...Properties.capture);

            Properties.capturePath = undefined;
        }
    }

};

const penKeymap = {
    'Shift+c': () => {
        clearCanvas();
        for (const penName in pens) {
            pens[penName].artist.clear();
            pens[penName].history.takeSnapshot();
        }
    },
    'Escape Control+[': () => {
        snippetLibrary.isRecording = false;

        if (currentPen.enabled) {
            currentPen.cancel();
        }
    },
    '~p': [
        () => currentPen.enabled,
        key => clipboardFor(key).paste(key)
    ],
    '~P': [
        () => currentPen.enabled,
        key => globalClipboard.paste(key)
    ],
    '~w': [
        () => currentPen.enabled && currentPen.selection && currentPen.selection.completed,
        key => {
            clipboardFor(key).register(key);
            currentPen.cancel();
        }
    ],
    '~x': [
        () => currentPen.enabled && currentPen.selection && currentPen.selection.completed,
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

                keymap = {
                    ...generalKeymap,
                    ...penKeymap,
                    ...parseKeymapFor(currentPen)
                }
            }
        }
    ]
};

const parsedPenKeymap = {
    'e': 'toggle-eraser',
    'c': 'clear',
    '.': 'next-color',
    ',': 'previous-color',
    ']': 'increase-brush-size',
    '[': 'decrease-brush-size',
    'Shift+>': 'increase-sensitivity',
    'Shift+<': 'decrease-sensitivity',
    'u Meta+z': 'undo',
    'Control+r Meta+Shift+z': 'redo',
    's': 'select',
    'Shift+s': 'continuous-selection',
    'y': 'yank',
    'Shift+y': ['yank-with', globalClipboard],
    'd': ['delete', 'd'],
    'Shift+d': ['delete-with', 'D', globalClipboard],
    'l': 'draw-line',
    'Shift+l': 'continuous-draw-line',
};

let keymap = {
    ...generalKeymap,
    ...penKeymap,
    ...parseKeymapFor(currentPen)
}
