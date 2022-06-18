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

        this.brush = new Brush(artist, previewArtist);
        this.brush.drawPreview();

        this.selection;
        this.line;
        this.shape;

        this.captureCallback;

        this.mode = penModes.NONE;

        this.history = new History(artist, 500);

        this.bind();
    }

    clear() {
        this.artist.clear();

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
                this.currentPoint[0] - latexArtist.canvas.width/2,
                this.currentPoint[1] - latexArtist.canvas.height/2
            ];

            this.artist.capture(this.latexArtist.canvas, 0, 0, ...centerPoint);

            this.latexArtist.hideCanvas();
            this.latexArtist.clear();

            this.history.takeSnapshot();

            break;

        case penModes.NONE:
            this.mode = penModes.BRUSH;
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
            this.brush.planStroke(e);
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
            this.history.takeSnapshot();

            this.mode = penModes.NONE;
            this.brush.lift();

            break;
        }
    }

    createLatex() {
        this.textPrompt.value = '';
        this.textPrompt.parentNode.classList.remove('hide');

        this.textPrompt.focus();
    }

    promptBinding(e) {
        e.stopPropagation();

        switch (e.key) {
        case 'j':
            if (!e.ctrlKey) break;
        case 'Enter':
            this.latexArtist.drawLatex({
                source: this.textPrompt.value,
                fontSize: 12,
                color: '#fdf4c1',
                align: 'center'
            }, undefined, () => {
                const centerPoint = [
                    this.currentPoint[0] - latexArtist.canvas.width/2,
                    this.currentPoint[1] - latexArtist.canvas.height/2
                ];

                this.latexArtist.moveCanvas(...centerPoint);
                this.latexArtist.showCanvas();
            }, true);

            this.mode = penModes.LATEX;

            this.textPrompt.parentNode.classList.add('hide');

            break;

        case 'Escape':
            this.mode = penModes.NONE;

            this.latexArtist.hideCanvas();
            this.latexArtist.clear();

            this.textPrompt.parentNode.classList.add('hide');

            break;
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
