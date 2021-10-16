class History {
    constructor(artist, maxSnapshots) {
        this.artist = artist;
        this.maxSnapshots = maxSnapshots;

        this.isFrozen = false;

        this.reset();
    }

    reset() {
        this.snapshots = [];
        this.currentSnapshot = -1;
        this.takeSnapshot();
    }

    takeSnapshot() {
        if (this.isFrozen) return;

        const bufferCanvas = document.createElement('canvas');
        const bufferCtx = bufferCanvas.getContext('2d');

        bufferCanvas.width = this.artist.canvas.width;
        bufferCanvas.height = this.artist.canvas.height;

        bufferCtx.drawImage(this.artist.canvas, 0, 0);

        this.snapshots.splice(this.currentSnapshot + 1, this.snapshots.length, bufferCanvas);

        if (this.currentSnapshot + 1 > this.maxSnapshots) {
            this.snapshots.shift();
        }

        this.currentSnapshot = Math.min(this.currentSnapshot + 1, this.maxSnapshots);
    }

    travel(count) {
        if (this.isFrozen) return;

        const relativeSnap = this.currentSnapshot + count;

        if (relativeSnap < this.snapshots.length && relativeSnap >= 0) {
            this.currentSnapshot = relativeSnap;

            this.artist.clear();

            this.artist.ctx.drawImage(this.snapshots[this.currentSnapshot], 0, 0);
        }
    }

    freeze() {
        this.isFrozen = true;
    }

    thaw() {
        this.isFrozen = false;
        this.travel(0);
    }
}


class Clipboard {
    constructor(pen, selectionArtist) {
        this.pen = pen;
        this.selectionArtist = selectionArtist;

        this.items = [];
        this.registry = {};
    }

    changePen(pen) {
        this.pen = pen;
    }

    createBuffer() {
        const bufferCanvas = document.createElement('canvas');
        const bufferCtx = bufferCanvas.getContext('2d');

        bufferCanvas.width = this.selectionArtist.canvas.width;
        bufferCanvas.height = this.selectionArtist.canvas.height;

        bufferCtx.drawImage(this.selectionArtist.canvas, 0, 0);

        return bufferCanvas;
    }

    store() {
        const bufferCanvas = this.createBuffer();

        this.items.unshift(bufferCanvas);
        this.items.splice(10);
    }

    register(key) {
        if (key) {
            this.registry[key] = this.createBuffer();
            this.store();
            this.pen.cancel();
        }
    }

    sendSelection(canvas, x, y) {
        this.pen.selectionArtist.canvas.style.top = y + 'px';
        this.pen.selectionArtist.canvas.style.left = x + 'px';

        this.pen.selectionArtist.canvas.width = canvas.width;
        this.pen.selectionArtist.canvas.height = canvas.height;

        this.pen.selectionArtist.canvas.classList.remove('hide');

        this.pen.selectionArtist.capture(canvas, 0, 0);

        this.pen.selectionStart = [x + canvas.width, y + canvas.height];
        this.pen.selectionEnd = [x, y];

        this.pen.movingSelection = true;
    }

    paste(key) {
        const index = key === 'p' ? 0 : parseInt(key);

        if (this.pen.currentPoint) {
            const [ x, y ] = this.pen.currentPoint;

            if (isNaN(key) && key in this.registry && key !== 'p') {
                this.sendSelection(this.registry[key], x, y);
                this.pen.history.takeSnapshot();
            } else if (index < this.items.length) {
                this.sendSelection(this.items[index], x, y);
                this.pen.history.takeSnapshot();
            }
        }
    }
}


class Pen {
    constructor(artist, previewArtist, selectionArtist, key) {
        this.key = key

        this.artist = artist;
        this.previewArtist = previewArtist;
        this.selectionArtist = selectionArtist;

        this.enabled = false;

        this.isDrawing = false;

        this.isEraser = false;
        this.brushSize = 1/2;
        this.eraserSize = 8;

        this.colorIndex = 0;
        this.previousColorIndex = 0;
        this.colorOptions = ['#fdf4c1', '#6CA17A', '#cc6666', '#81a2be'];
        this.previewArtist.canvas.style.borderColor = this.brushColor;

        this.sensitivity = 1;

        this.drawingLine = false;
        this.lineMode = false;
        this.lineStart;

        this.isSelecting = false;
        this.selectionMode = false;
        this.movingSelection = false;
        this.copyMode = false;
        this.selectionStart;

        this.clipboard = new Clipboard(this, this.selectionArtist);

        this.brushPos;

        this.isRecording = false;
        this.recording = [];

        this.currentPoint;

        this.bind();

        this.history = new History(this.artist, 50);

        this.drawBrushPreview();

        this.skipEvent = false;
    }

    get brushColor() {
        return this.colorOptions[this.colorIndex];
    }

    clear() {
        this.artist.clear();

        if (this.enabled) {
            this.history.takeSnapshot();
        }
    }

    startRecording() {
        this.isRecording = true;
        this.recording = [];

        this.colorIndex = 2;
        this.drawBrushPreview();
    }

    stopRecording() {
        this.isRecording = false;

        this.colorIndex = this.previousColorIndex;
        this.drawBrushPreview();
    }

    toggle() {
        this.clear();
        this.enabled = !this.enabled;
        this.artist.canvas.classList.toggle('hide');
        this.previewArtist.canvas.classList.toggle('hide');
        document.body.classList.toggle('draggable');
        zoom(1, false);
    }

    planStroke(e) {
        const brushSize = this.isEraser ? this.eraserSize : this.brushSize;

        if (this.brushPos) {
            const dx = Math.abs(e.pageX - this.brushPos[0]);
            const dy = Math.abs(e.pageY - this.brushPos[1]);

            const gPosDiff = dx > dy ? 0 : 1;

            const direction = [
                Math.min(e.pageX - this.brushPos[0], 0) ? -1 : 1,
                Math.min(e.pageY - this.brushPos[1], 0) ? -1 : 1,
            ];

            for (let i = 0; i < [dx, dy][gPosDiff]; i++) {
                this.drawBrush(
                    ((gPosDiff ? dx / dy * i : i) || 0) * direction[0] + this.brushPos[0],
                    ((gPosDiff ? i : dy / dx * i) || 0) * direction[1] + this.brushPos[1],
                    brushSize + this.sensitivity * (1/(1 + Math.exp(-3*e.pressure)) - 1/2)
                );
            }
        } else {
            this.drawBrush(
                e.pageX,
                e.pageY,
                brushSize + Math.pow(brushSize * e.pressure, 1 + this.sensitivity)
            );
        }

        this.brushPos = [e.pageX, e.pageY];
    }

    drawBrush(x, y, adjustedBrushSize) {
        if (this.isEraser) {
            this.artist.clear(
                x - adjustedBrushSize/2,
                y - adjustedBrushSize/2,
                adjustedBrushSize,
                adjustedBrushSize
            );
        } else {
            const properties = {
                point: [x, y],
                radius: adjustedBrushSize,
                theta_1: 0,
                theta_2: 2*Math.PI,
                fillColor: this.brushColor,
                borderColor: this.brushColor,
                borderWidth: 0
            };

            this.artist.drawArc(properties);
        }

        if (this.isRecording) {
            this.recording.push([x, y, adjustedBrushSize, this.isEraser]);
        }
    }

    drawBrushPreview() {
        this.previewArtist.clear();

        const x = this.previewArtist.canvas.width / 2;
        const y = this.previewArtist.canvas.height / 2;

        const scaleFactor = 4;
        const scaleOffset = 2;
        const size = (this.isEraser ? this.eraserSize : this.brushSize) * scaleFactor + scaleOffset;
        const fillColor = this.isEraser ? 'transparent' : this.brushColor;

        this.previewArtist.canvas.style.borderColor = this.brushColor;

        const properties = {
            point: [x, y],
            width: size | 0,
            height: size | 0,
            fillColor: fillColor,
            borderColor: this.brushColor,
            borderWidth: 2
        };

        this.previewArtist.drawRect(properties);
    }

    activateLine() {
        if (this.enabled && !this.movingSelection && !this.selectionStart && !this.isDrawing) {
            this.drawingLine = true;
        }
    }

    activateSelection() {
        if (this.enabled && !this.movingSelection && !this.selectionStart && !this.isDrawing) {
            this.isSelecting = true;
        }
    }

    startSelection(e) {
        this.selectionStart = [e.pageX|0, e.pageY|0];

        this.selectionArtist.canvas.style.top = (e.pageY|0) + 'px';
        this.selectionArtist.canvas.style.left = (e.pageX|0) + 'px';

        this.selectionArtist.canvas.width = 0;
        this.selectionArtist.canvas.height = 0;

        this.selectionArtist.canvas.classList.remove('hide');
    }

    changeSelection(e) {
        const x = e.pageX|0;
        const y = e.pageY|0;

        const dx = x - this.selectionStart[0];
        const dy = y - this.selectionStart[1];

        this.selectionArtist.canvas.width = Math.abs(dx);
        this.selectionArtist.canvas.height = Math.abs(dy);

        if (dx <= 0) {
            this.selectionArtist.canvas.style.left = x + 'px';
        }

        if (dy <= 0) {
            this.selectionArtist.canvas.style.top = y + 'px';
        }
    }

    endSelection(e) {
        this.isSelecting = false;

        const width = this.selectionArtist.canvas.width;
        const height = this.selectionArtist.canvas.height;

        if (!width || !height) {
            this.cancel();
            return;
        }

        let x = this.selectionArtist.canvas.style.left;
        x = x.slice(0, x.length - 2);
        x |= 0;

        let y = this.selectionArtist.canvas.style.top;
        y = y.slice(0, y.length - 2)
        y |= 0;

        this.selectionArtist.capture(this.artist.canvas, x, y);

        if (!this.copyMode) {
            this.artist.clear(x, y, width, height);
        }

        if (!this.selectionMode) {
            this.copyMode = false;
        }

        this.selectionEnd = [e.pageX|0, e.pageY|0];

        this.movingSelection = true;
    }

    getSelectionHandle(e) {
        const x = e.pageX|0;
        const y = e.pageY|0;
        const dx = this.selectionEnd[0] - this.selectionStart[0];
        const dy = this.selectionEnd[1] - this.selectionStart[1];

        return [dx > 0 ? x - dx : x, dy > 0 ? y - dy : y];
    }

    moveSelection(e) {
        if (!this.selectionStart || !this.selectionEnd) {
            this.cancel();
            return;
        }

        const [x, y] = this.getSelectionHandle(e);

        this.selectionArtist.canvas.style.left = x + 'px';
        this.selectionArtist.canvas.style.top = y + 'px';
    }

    applySelection(e) {
        if (!this.selectionStart || !this.selectionEnd) {
            this.cancel();
            return;
        }

        const [x, y] = this.getSelectionHandle(e);

        this.artist.capture(
            this.selectionArtist.canvas,
            0, 0,
            x, y
        );
        this.selectionArtist.clear();
        this.selectionArtist.canvas.classList.add('hide');

        this.movingSelection = false;
        this.selectionStart = undefined;
        this.selectionEnd = undefined;

        this.history.takeSnapshot();

        if (this.selectionMode) {
            this.isSelecting = true;
        }
    }

    deleteSelection() {
        if (this.movingSelection) {
            this.clipboard.store();

            this.selectionArtist.clear();
            this.selectionArtist.canvas.classList.add('hide');

            this.movingSelection = false;
            this.selectionStart = undefined;
            this.selectionEnd = undefined;

            this.history.takeSnapshot();

            if (this.selectionMode) {
                this.isSelecting = true;
            }
        }
    }

    yank() {
        if (this.enabled && !this.movingSelection && !this.selectionStart && !this.isDrawing) {
            this.copyMode = true;
            this.activateSelection();
        } else if (this.movingSelection) {
            this.clipboard.store();
            this.cancel();
        }
    }

    cancel() {
        this.selectionArtist.clear();
        this.selectionArtist.canvas.classList.add('hide');

        if (this.movingSelection || this.lineStart) {
            this.history.takeSnapshot();
            this.history.travel(-1);
        }

        this.isSelecting = false;
        this.selectionMode = false;
        this.copyMode = false;
        this.movingSelection = false;
        this.selectionStart = undefined;
        this.selectionEnd = undefined;
        this.lineMode = false;
        this.drawingLine = false;
        this.lineStart = undefined;
    }

    moveBinding(e) {
        this.currentPoint = [e.pageX, e.pageY];

        if (awaitingEvent || e.which > 1 || !this.enabled) return;

        if (this.lineStart) {
            const point = [e.pageX, e.pageY]

            this.history.travel(0);

            this.artist.drawCurve({
                points: [this.lineStart, point],
                color: this.brushColor,
                width: this.brushSize * 4,
                arrow: false,
                arrowHead: [],
                fillColor: 'transparent'
            });
        } else if (this.selectionStart && this.isSelecting) {
            this.changeSelection(e);
        } else if (this.movingSelection) {
            this.moveSelection(e);
        } else if (this.isDrawing && this.enabled) {
            this.planStroke(e);
        }
    }

    downBinding(e) {
        if (awaitingEvent || e.which > 1 || !this.enabled) return;

        if (this.isSelecting) {
            this.startSelection(e);
        } else if (this.drawingLine) {
            this.lineStart = [e.pageX, e.pageY];
        } else if (!this.movingSelection) {
            this.isDrawing = true;
        }
    }

    upBinding(e) {
        if (awaitingEvent || e.which > 1 || this.skipEvent || !this.enabled) {
            this.skipEvent = false;
            return;
        };

        if (this.lineStart) {
            if (!this.lineMode) {
                this.drawingLine = false;
            }

            this.lineStart = undefined;
            this.history.takeSnapshot();
        } else if (this.isSelecting) {
            this.endSelection(e);
        } else if (this.movingSelection) {
            this.applySelection(e);
        } else {
            this.isDrawing = false;
            this.brushPos = undefined;
            this.history.takeSnapshot();
        }
    }

    bind() {
        window.addEventListener('pointermove', this.moveBinding.bind(this));
        window.addEventListener('mousedown', this.downBinding.bind(this));
        window.addEventListener('mouseup', this.upBinding.bind(this));
    }

    increaseBrushSize() {
        if (this.isEraser) {
            this.eraserSize++;
        } else {
            this.brushSize += 1/2;
        }

        this.drawBrushPreview();
    }

    decreaseBrushSize() {
        if (this.isEraser) {
            this.eraserSize = Math.max(1, this.eraserSize - 1);
        } else {
            this.brushSize = Math.max(1/2, this.brushSize - 1/2);
        }

        this.drawBrushPreview();
    }

    increaseSensitivity() {
        this.sensitivity += 2;
    }

    decreaseSensitivity() {
        this.sensitivity = Math.max(1, this.sensitivity - 2);
    }

    nextColor() {
        this.colorIndex = (this.colorIndex + 1) % this.colorOptions.length;
        this.previousColorIndex = this.colorIndex;
        this.drawBrushPreview();
    }

    previousColor() {
        const colorCount = this.colorOptions.length;

        this.colorIndex = (this.colorIndex + colorCount - 1) % colorCount;
        this.previousColorIndex = this.colorIndex;
        this.drawBrushPreview();
    }

    toggleEraser() {
        this.isEraser = !this.isEraser;
        this.drawBrushPreview();
    }
}
