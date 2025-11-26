const penModes = {
    NONE: 'none',
    BRUSH: 'brush',
    LINE: 'line',
    SELECTION: 'selection',
    CONTINUOUSLINE: 'continuous-line',
    CONTINUOUSSELECTION: 'continuous-selection',
    CAPTURE: 'capture',
    SHAPE: 'shape',
    LATEX: 'latex',
    ROTATION: 'rotation'
};


class Pen {
    constructor(artist, previewArtist, selectionArtist, shapeArtist, name, textPrompt, latexArtist) {
        this.name = name;

        this.artist = artist;
        this.previewArtist = previewArtist;
        this.selectionArtist = selectionArtist;
        this.shapeArtist = shapeArtist;
        this.latexArtist = latexArtist;

        this.textPrompt = textPrompt;

        this.enabled = false;

        this.currentPoint = [0, 0];

        this.clipboard = new Clipboard(this, selectionArtist);

        this.brush = new Brush(this, artist, previewArtist);
        this.brush.drawPreview();

        this.defaultFontSize = 12;

        this.selection;
        this.line;
        this.shape;

        this.styles = new Set();

        this.captureCallback;

        this.mode = penModes.NONE;

        this.history = new History(artist, 500);

        this.bind();
    }

    clear() {
        this.artist.clear();

        // Also clear any LaTeX-specific state/overlays owned by the latex artist
        try {
            if (this.latexArtist) {
                try { this.latexArtist.clear(); } catch (e) {}

                // Remove any committed overlay fragments that were marked as LaTeX
                try {
                    if (typeof window !== 'undefined' && window.__maxwell_svg_overlay) {
                        const svg = window.__maxwell_svg_overlay.querySelector('svg');
                        if (svg) {
                            const nodes = Array.from(svg.querySelectorAll('[data-latex-fragment]'));
                            for (const n of nodes) {
                                n.remove();
                            }
                        }
                    }
                } catch (e) {}
            }
        } catch (e) {}

        if (this.enabled) {
            this.history.takeSnapshot();
        }
    }

    toggle() {
        this.clear();
        this.enabled = !this.enabled;
        this.artist.canvas.classList.toggle('hide');
        this.previewArtist.canvas.classList.toggle('hide');
        document.body.classList.toggle('draggable');
        zoom(1, false);
    }

    setPrompt(message) {
        if (!keyPrompt.innerText) {
            keyPrompt.innerText = message;
        }
    }

    cancel() {
        switch (this.mode) {
        case penModes.CONTINUOUSSELECTION:
        case penModes.SELECTION:
            this.selection.cancel();
            this.selection = undefined;

            this.history.takeSnapshot();
            this.history.travel(-1);

            break;

        case penModes.CONTINUOUSLINE:
        case penModes.LINE:
            this.line = undefined;

            this.history.takeSnapshot();
            this.history.travel(-1);

            break;

        case penModes.BRUSH:
            this.brush.lift();
            this.history.takeSnapshot();

            break;

        case penModes.SHAPE:
            this.shape.cancel();
            this.shape = undefined;

            break;

        case penModes.ROTATION:
            keyPrompt.innerText = '';

            if (this.shape) {
                this.mode = penModes.SHAPE;
                this.cancel();
            } else if (this.selection) {
                this.mode = penModes.SELECTION;
                this.cancel();
            }

            break;
        }

        this.mode = penModes.NONE;
    }

    capture(callback) {
        this.mode = penModes.CAPTURE;
        this.captureCallback = callback;
        this.selection = new Selection(
            this.selectionArtist,
            this.artist
        );
        this.selection.copyMode = true;
    }

    downBinding(e) {
        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        switch (this.mode) {
        case penModes.CAPTURE:
        case penModes.CONTINUOUSSELECTION:
        case penModes.SELECTION:
            if (!this.selection.completed) {
                this.selection.start(e);
            }
            break;

        case penModes.CONTINUOUSLINE:
        case penModes.LINE:
            this.line.start(e);
            break;

        case penModes.SHAPE:
            const phase = this.shape.switchPhase();

            if (phase === 0) {
                this.mode = penModes.NONE;
                this.shape = undefined;
            }

            this.history.takeSnapshot();

            break;

        case penModes.ROTATION:
            keyPrompt.innerText = '';

            if (this.shape) {
                this.mode = penModes.SHAPE;
            } else if (this.selection) {
                this.mode = penModes.SELECTION;
            } else {
                this.mode = penModes.NONE;
            }

            this.downBinding(e);

            break;

        case penModes.LATEX:
            this.mode = penModes.NONE;

            const centerPoint = [
                this.currentPoint[0] - (this.latexArtist && this.latexArtist.canvas ? this.latexArtist.canvas.width/2 : 0),
                this.currentPoint[1] - (this.latexArtist && this.latexArtist.canvas ? this.latexArtist.canvas.height/2 : 0)
            ];

            // Commit any SVG fragments produced by the latex artist directly
            // into the main artist as vector elements to avoid rasterization.
            try {
                const fragments = (this.latexArtist && Array.isArray(this.latexArtist._svgFragments)) ? this.latexArtist._svgFragments : [];
                console.debug('[Pen] committing latex fragments count', fragments.length, 'global', (typeof window !== 'undefined' && Array.isArray(window.__maxwell_svg_fragments)) ? window.__maxwell_svg_fragments.length : 0);

                if (fragments.length > 0) {
                    for (const frag of fragments) {
                        try {
                            this.artist.commitSVGFragment(frag, { pageX: this.currentPoint[0], pageY: this.currentPoint[1], latexArtist: this.latexArtist });
                        } catch (e) { console.warn('[Pen] commitSVGFragment error', e); }
                    }
                } else {
                    // Fallback: if no vector fragments are available, rasterize the latex canvas into the main canvas
                    try {
                        this.artist.capture(this.latexArtist.canvas, 0, 0, ...centerPoint);
                        console.debug('[Pen] fallback raster capture used for latex commit');
                    } catch (e) { console.warn('[Pen] fallback capture failed:', e); }
                }
            } catch (e) { console.warn('[Pen] failed to commit latex fragments as vector:', e); }

            // Hide and clear the latex artist's temporary content
            try { this.latexArtist.hideCanvas(); } catch (e) {}
            try { this.latexArtist.clear(); } catch (e) {}
            try { this.latexArtist._svgFragments = []; } catch (e) {}

            this.history.takeSnapshot();

            break;

        case penModes.NONE:
            this.mode = penModes.BRUSH;
            // record initial sample immediately so quick taps/dots are captured
            if (this.brush && typeof this.brush.drawBrush === 'function') {
                this.brush.drawBrush(e);
            }
            break;
        }
    }

    moveBinding(e) {
        this.currentPoint = [e.pageX|0, e.pageY|0];

        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        switch (this.mode) {
        case penModes.CAPTURE:
        case penModes.CONTINUOUSSELECTION:
        case penModes.SELECTION:
            if (this.selection.started) {
                if (this.selection.completed) {
                    this.selection.move(e);
                } else {
                    this.selection.change(e);
                }
            }
            break;

        case penModes.CONTINUOUSLINE:
        case penModes.LINE:
            if (this.line.started) {
                this.line.update(e);
            }
            break;

        case penModes.SHAPE:
            if (!this.shape.started) {
                this.shape.start(e);
            } else {
                this.shape.update(e);
            }
            break;

        case penModes.LATEX:
            const centerPoint = [
                this.currentPoint[0] - this.latexArtist.canvas.width/2,
                this.currentPoint[1] - this.latexArtist.canvas.height/2
            ];

            this.latexArtist.moveCanvas(...centerPoint);
            break;

        case penModes.BRUSH:
            this.brush.drawBrush(e);
            break;

        case penModes.ROTATION:
            if (this.shape) {
                const theta = Math.atan2(
                    this.shape.pointFromCenter[1] - this.currentPoint[1],
                    this.currentPoint[0] - this.shape.pointFromCenter[0]
                );

                if (this.shape.alpha === undefined) {
                    this.shape.alpha = -theta;
                }

                this.shape.theta = theta;
                this.shape.render();
            } else if (this.selection) {
                const centerPoint = this.selection.centerPoint;

                const theta = Math.atan2(
                    this.currentPoint[1] - centerPoint[1],
                    centerPoint[0] - this.currentPoint[0]
                );

                if (this.selection.alpha === undefined) {
                    this.selection.alpha = -theta;
                }
                this.selection.theta = theta;

                this.selection.artist.rotateCanvas(this.selection.angle);
            }

            break;
        }
    }

    upBinding(e) {
        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        switch (this.mode) {
        case penModes.CAPTURE:
            this.mode = penModes.NONE;

            this.selection.end(e);
            this.selection.cancel();
            this.captureCallback(this.selection);

            break;

        case penModes.CONTINUOUSSELECTION:
        case penModes.SELECTION:
            if (this.selection.completed) {
                this.selection.apply(e);
                this.selection = undefined;

                if (this.mode === penModes.SELECTION) {
                    this.mode = penModes.NONE;
                } else {
                    this.selection = new Selection(
                        this.selectionArtist,
                        this.artist
                    );
                }

                this.history.takeSnapshot();
            } else {
                this.selection.end(e);
            }
            break;

        case penModes.LINE:
            this.history.takeSnapshot();

            this.mode = penModes.NONE;
            this.line = undefined;

            break;

        case penModes.CONTINUOUSLINE:
            this.history.takeSnapshot();
            this.line = new Line(this);
            break;

        case penModes.BRUSH:
            // finalize the stroke first, then record snapshot that includes the final stroke
            this.mode = penModes.NONE;
            this.brush.lift();
            this.history.takeSnapshot();

            break;
        }
    }

    renderLatex(value) {
        value = value.split(';');

        this.defaultFontSize = value.length > 1
            ? (parseInt(value[1]) || this.defaultFontSize)
            : this.defaultFontSize;

        this.latexArtist.drawLatex({
            source: value[0].replace(/\\\((.*)\\\)/, '$1').trim(),
            fontSize: this.defaultFontSize,
            color: this.brush.color,
            point: this.currentPoint,
            align: 'center',
            embed: true
        }, undefined, () => {
            const centerPoint = [
                this.currentPoint[0] - latexArtist.canvas.width/2,
                this.currentPoint[1] - latexArtist.canvas.height/2
            ];

            this.latexArtist.moveCanvas(...centerPoint);
            this.latexArtist.showCanvas();
        });

        this.mode = penModes.LATEX;
    }

    createLatex() {
        if (Properties.externalPrompt) {
            getLatexPrompt().then(value => {
                if (value) {
                    this.renderLatex(value);
                } else {
                    Properties.externalPrompt = false;
                    this.createLatex();
                }
            });
        } else {
            this.textPrompt.value = '';
            this.textPrompt.parentNode.classList.remove('hide');

            this.textPrompt.focus();
        }
    }

    promptBinding(e) {
        e.stopPropagation();

        switch (e.key) {
        case 'j':
            if (!e.ctrlKey) break;
        case 'Enter':
            this.renderLatex(this.textPrompt.value);
            this.textPrompt.parentNode.classList.add('hide');

            break;

        case 'g':
            if (!e.ctrlKey) break;

        case 'Escape':
            this.mode = penModes.NONE;

            this.latexArtist.hideCanvas();
            this.latexArtist.clear();

            this.textPrompt.parentNode.classList.add('hide');

            break;
        }
    }

    toggleStyle(style) {
        if (this.styles.has(style)) {
            this.styles.delete(style);
        } else {
            this.styles.add(style);
        }
    }

    hasStyle(style) {
        return this.styles.has(style);
    }

    setStyle(key) {
        const styleMap = {
            a: 'arrow',
            d: 'dashed',
            f: 'shape-fill'
        };

        if (key in styleMap) {
            this.toggleStyle(styleMap[key]);
        }
    }

    createShape(key) {
        switch (key) {
        case 'r':
            this.shape = new Rect(this, this.shapeArtist);
            break;

        case 'c':
            this.shape = new Circle(this, this.shapeArtist);
            break;

        case 'a':
            this.shape = new Arc(this, this.shapeArtist);
            break;

        case 't':
            this.shape = new RTriangle(this, this.shapeArtist);
            break;

        default:
            return;
        }

        this.mode = penModes.SHAPE;

        if (this.currentPoint) {
            this.shape.start({
                pageX: this.currentPoint[0],
                pageY: this.currentPoint[1]
            });
        }
    }

    rotate() {
        this.setPrompt('ROTATING');
        this.mode = penModes.ROTATION;
    }

    bind() {
        window.addEventListener('pointermove', this.moveBinding.bind(this));
        window.addEventListener('mousedown', this.downBinding.bind(this));
        window.addEventListener('mouseup', this.upBinding.bind(this));
        this.textPrompt.addEventListener('keydown', this.promptBinding.bind(this));
        window.addEventListener('keydown', e => {
            if (e.key === ';') e.preventDefault();
        }, false);
    }

    parse(command, ...args) {
        const commandAssociation = {
            'toggle-eraser': () => this.brush.toggleEraser(),
            'clear': () => this.clear(),
            'next-color': () => this.brush.nextColor(),
            'previous-color': () => this.brush.previousColor(),
            'increase-brush-size': () => this.brush.increaseSize(),
            'decrease-brush-size': () => this.brush.decreaseSize(),
            'increase-sensitivity': () => this.brush.increaseSensitivity(),
            'decrease-sensitivity': () => this.brush.decreaseSensitivity(),
            'undo': () => this.history.travel(-1),
            'redo': () => this.history.travel(1),
            'select': () => {
                this.selection = new Selection(
                    this.selectionArtist,
                    this.artist
                );
                this.mode = penModes.SELECTION;
            },
            'continuous-selection': () => {
                if (this.mode === penModes.CONTINUOUSSELECTION) {
                    this.cancel();
                } else if (this.mode === penModes.NONE) {
                    this.selection = new Selection(
                        this.selectionArtist,
                        this.artist
                    );
                    this.mode = penModes.CONTINUOUSSELECTION;
                }
            },
            'yank': () => {
                if (this.mode === penModes.NONE) {
                    this.selection = new Selection(
                        this.selectionArtist,
                        this.artist
                    );
                    this.mode = penModes.SELECTION;

                    this.selection.copyMode = true;
                } else if (this.mode === penModes.SELECTION && this.selection.completed) {
                    this.clipboard.store();
                    currentPen.cancel();
                }
            },
            'yank-with': () => {
                if (this.mode === penModes.SELECTION && this.selection.completed) {
                    args[0].store();
                    currentPen.cancel();
                }
            },
            'delete': () => {
                if (this.selection && this.selection.completed) {
                    this.selection.delete(args[0], this.clipboard);
                    this.history.takeSnapshot();

                    switch (this.mode) {
                    case penModes.SELECTION:
                        this.cancel();
                        break;

                    case penModes.CONTINUOUSSELECTION:
                        this.selection = new Selection(
                            this.selectionArtist,
                            this.artist
                        );
                        break;
                    }
                }
            },
            'delete-with': () => {
                if (this.selection && this.selection.completed) {
                    this.selection.delete(args[0], args[1]);
                    this.history.takeSnapshot();

                    switch (this.mode) {
                    case penModes.SELECTION:
                        this.cancel();
                        break;

                    case penModes.CONTINUOUSSELECTION:
                        this.selection = new Selection(
                            this.selectionArtist,
                            this.artist
                        );
                        break;
                    }
                }
            },
            'draw-line': () => {
                if (this.mode === penModes.NONE) {
                    this.line = new Line(this);
                    this.mode = penModes.LINE;
                }
            },
            'continuous-draw-line': () => {
                if (this.mode === penModes.CONTINUOUSLINE) {
                    this.cancel();
                } else if (this.mode === penModes.NONE) {
                    this.line = new Line(this);
                    this.mode = penModes.CONTINUOUSLINE;
                }
            }
        };

        return () => {
            if (!this.enabled) return;
            commandAssociation[command]();
        };
    }
}
