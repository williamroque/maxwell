const penModes = {
    NONE: 'none',
    BRUSH: 'brush',
    LINE: 'line',
    SELECTION: 'selection',
    CONTINUOUSLINE: 'continuous-line',
    CONTINUOUSSELECTION: 'continuous-selection'
};


class Pen {
    constructor(artist, previewArtist, selectionArtist, name) {
        this.name = name;

        this.artist = artist;
        this.previewArtist = previewArtist;
        this.selectionArtist = selectionArtist;

        this.enabled = false;

        this.currentPoint;

        this.clipboard = new Clipboard(this, selectionArtist);

        this.brush = new Brush(artist, previewArtist);
        this.brush.drawPreview();

        this.selection;
        this.line;

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
        }

        this.mode = penModes.NONE;
    }

    downBinding(e) {
        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        switch (this.mode) {
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

        case penModes.NONE:
            this.mode = penModes.BRUSH;
            break;
        }
    }

    moveBinding(e) {
        this.currentPoint = [e.pageX|0, e.pageY|0];

        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        switch (this.mode) {
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

        case penModes.BRUSH:
            this.brush.planStroke(e);
            break;
        }
    }

    upBinding(e) {
        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        switch (this.mode) {
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

    bind() {
        window.addEventListener('pointermove', this.moveBinding.bind(this));
        window.addEventListener('mousedown', this.downBinding.bind(this));
        window.addEventListener('mouseup', this.upBinding.bind(this));
    }

    parse(command, ...args) {
        const commandAssociation = {
            'toggle-eraser': this.brush.toggleEraser,
            'clear': this.clear,
            'next-color': this.brush.nextColor,
            'previous-color': this.brush.previousColor,
            'increase-brush-size': this.brush.increaseSize,
            'decrease-brush-size': this.brush.decreaseSize,
            'increase-sensitivity': this.brush.increaseSensitivity,
            'decrease-sensitivity': this.brush.decreaseSensitivity,
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
