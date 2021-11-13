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
        if (this.selection) {
            this.selection.cancel();
            this.selection = undefined;

            this.history.takeSnapshot();
            this.history.travel(-1);
        }
    }

    downBinding(e) {
        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        if (this.selection) {
            if (!this.selection.completed) {
                this.selection.start(e);
            }
        } else {
            this.isDrawing = true;
        }
    }

    moveBinding(e) {
        this.currentPoint = [e.pageX|0, e.pageY|0];

        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        if (this.selection && this.selection.started) {
            if (this.selection.completed) {
                this.selection.move(e);
            } else {
                this.selection.change(e);
            }
        } else if (this.isDrawing) {
            this.brush.planStroke(e);
        }
    }

    upBinding(e) {
        if (Properties.awaitingEvent || e.which > 1 || !this.enabled) return;

        if (this.selection) {
            if (this.selection.completed) {
                this.selection.apply(e);
                this.selection = undefined;

                this.history.takeSnapshot();
            } else {
                this.selection.end(e);
            }
        } else {
            this.isDrawing = false;
            this.history.takeSnapshot();
            this.brush.lift();
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
            },
            'yank': () => {
                if (!this.selection) {
                    this.selection = new Selection(
                        this.selectionArtist,
                        this.artist
                    )

                    this.selection.copyMode = true;
                } else if (this.selection.completed) {
                    this.clipboard.store();
                    currentPen.cancel();
                }
            },
            'yank-with': () => args[0].store(),
            'delete': () => {
                if (this.selection.completed) {
                    this.selection.delete(args[0], this.clipboard);
                }
            },
            'delete-with': () => {
                if (this.selection.completed) {
                    this.selection.delete(args[0], args[1]);
                }
            }
        };

        return () => {
            if (!this.enabled) return;
            commandAssociation[command]();
        };
    }
}
