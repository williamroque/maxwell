class History {
    constructor(artist, maxSnapshots) {
        this.artist = artist;
        this.maxSnapshots = maxSnapshots;

        this.reset();
    }

    reset() {
        this.snapshots = [];
        this.currentSnapshot = -1;
        this.takeSnapshot();
    }

    takeSnapshot() {
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
        const relativeSnap = this.currentSnapshot + count;

        if (relativeSnap < this.snapshots.length && relativeSnap >= 0) {
            this.currentSnapshot = relativeSnap;

            this.artist.clear();

            this.artist.ctx.drawImage(this.snapshots[this.currentSnapshot], 0, 0);
        }
    }
}


class Pen {
    constructor(artist, previewArtist, selectionArtist) {
        this.artist = artist;
        this.previewArtist = previewArtist;
        this.selectionArtist = selectionArtist;

        this.enabled = false;

        this.isDrawing = false;

        this.isEraser = false;
        this.brushSize = 1;
        this.eraserSize = 8;

        this.colorIndex = 0;
        this.colorOptions = ['#fdf4c1', '#6CA17A', '#cc6666', '#81a2be'];
        this.previewArtist.canvas.style.borderColor = this.brushColor;

        this.sensitivity = 1;

        this.drawingLine = false;
        this.lineStart;

        this.isSelecting = false;
        this.movingSelecting = false;
        this.selectionStart;

        this.brushPos;

        this.bind();

        this.history = new History(this.artist, 50);

        this.drawBrushPreview();
    }

    get brushColor() {
        return this.colorOptions[this.colorIndex];
    }

    clear() {
        this.artist.clear();
        this.history.reset();
    }

    toggle() {
        this.enabled = !this.enabled;
        this.artist.canvas.classList.toggle('hide');
        this.previewArtist.canvas.classList.toggle('hide');
        document.body.classList.toggle('draggable');
        this.clear();
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
                    brushSize + Math.pow(brushSize * e.pressure, 1 + this.sensitivity)
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
            const offset = 1;

            const curve = [
                [x, y],
                [x + adjustedBrushSize, y - offset],
                [x + adjustedBrushSize, y + adjustedBrushSize - offset],
                [x, y + adjustedBrushSize]
            ]

            const properties = {
                points: curve,
                color: this.brushColor,
                width: 1,
                arrows: 0,
                arrowSize: 0,
                fill: true
            };

            this.artist.drawCurve(properties);
        }
    }

    drawBrushPreview() {
        this.previewArtist.clear();

        const x = this.previewArtist.canvas.width / 2;
        const y = this.previewArtist.canvas.height / 2;

        const scaleFactor = 2.5;
        const size = (this.isEraser ? this.eraserSize : this.brushSize) * scaleFactor;
        const fillColor = this.isEraser ? 'transparent' : this.brushColor;

        this.previewArtist.canvas.style.borderColor = this.brushColor;

        const properties = {
            point: [x, y],
            width: size,
            height: size,
            fillColor: fillColor,
            borderColor: this.brushColor
        };

        this.previewArtist.drawRect(properties);
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
            this.cancelSelection();
            return;
        }

        let x = this.selectionArtist.canvas.style.left;
        x = x.slice(0, x.length - 2);
        x |= 0;

        let y = this.selectionArtist.canvas.style.top;
        y = y.slice(0, y.length - 2)
        y |= 0;

        this.selectionArtist.capture(this.artist.canvas, x, y);
        this.artist.clear(x, y, width, height);

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
        const [x, y] = this.getSelectionHandle(e);

        this.selectionArtist.canvas.style.left = x + 'px';
        this.selectionArtist.canvas.style.top = y + 'px';
    }

    applySelection(e) {
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
    }

    deleteSelection() {
        if (this.moveSelection) {
            this.selectionArtist.clear();
            this.selectionArtist.canvas.classList.add('hide');

            this.movingSelection = false;
            this.selectionStart = undefined;
            this.selectionEnd = undefined;

            this.history.takeSnapshot();
        }
    }

    cancelSelection() {
        this.selectionArtist.clear();
        this.selectionArtist.canvas.classList.add('hide');

        if (this.movingSelection) {
            this.history.takeSnapshot();
            this.history.travel(-1);
        }

        this.isSelecting = false;
        this.movingSelection = false;
        this.selectionStart = undefined;
        this.selectionEnd = undefined;
    }

    bind() {
        document.addEventListener('pointermove', e => {
            if (this.selectionStart && this.isSelecting) {
                this.changeSelection(e);
            } else if (this.movingSelection) {
                this.moveSelection(e);
            } else if (this.isDrawing && this.enabled) {
                this.planStroke(e);
            }
        });

        this.artist.canvas.addEventListener('mousedown', e => {
            if (this.isSelecting) {
                this.startSelection(e);
            } else if (!(this.drawingLine || this.movingSelection)) {
                this.isDrawing = true;
            }
        });

        this.artist.canvas.addEventListener('mouseup', e => {
            if (this.drawingLine) {
                const point = [e.pageX, e.pageY]

                if (this.lineStart) {
                    this.artist.drawCurve({
                        points: [this.lineStart, point],
                        color: this.brushColor,
                        width: this.brushSize * 2,
                        arrows: 0,
                        arrowSize: 0,
                        fill: false
                    });

                    this.drawingLine = false;
                    this.lineStart = undefined;
                    this.history.takeSnapshot();
                } else {
                    this.lineStart = point;
                }
            } else if (this.isSelecting) {
                this.endSelection(e);
            } else if (this.movingSelection) {
                this.applySelection(e);
            } else {
                this.isDrawing = false;
                this.brushPos = undefined;
                this.history.takeSnapshot();
            }
        });
    }

    increaseBrushSize() {
        if (this.isEraser) {
            this.eraserSize++;
        } else {
            this.brushSize++;
        }

        this.drawBrushPreview();
    }

    decreaseBrushSize() {
        if (this.isEraser) {
            this.eraserSize = Math.max(1, this.eraserSize - 1);
        } else {
            this.brushSize = Math.max(1, this.brushSize - 1);
        }

        this.drawBrushPreview();
    }

    increaseSensitivity() {
        this.sensitivity++;
    }

    decreaseSensitivity() {
        this.sensitivity--;
    }

    nextColor() {
        this.colorIndex = (this.colorIndex + 1) % this.colorOptions.length;
        this.drawBrushPreview();
    }

    previousColor() {
        const colorCount = this.colorOptions.length;

        this.colorIndex = (this.colorIndex + colorCount - 1) % colorCount;
        this.drawBrushPreview();
    }

    toggleEraser() {
        this.isEraser = !this.isEraser;
        this.drawBrushPreview();
    }
}
