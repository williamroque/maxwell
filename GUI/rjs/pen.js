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
    constructor(artist, previewArtist) {
        this.artist = artist;
        this.previewArtist = previewArtist;

        this.enabled = false;

        this.isDrawing = false;

        this.isEraser = false;
        this.brushSize = 2;

        this.colorIndex = 0;
        this.colorOptions = ['#fdf4c1', '#6CA17A', '#cc6666', '#81a2be'];

        this.sensitivity = 1;

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
                    this.brushSize + Math.pow(this.brushSize * e.pressure, 1 + this.sensitivity)
                );
            }
        } else {
            this.drawBrush(
                e.pageX,
                e.pageY,
                this.brushSize + Math.pow(this.brushSize * e.pressure, 1 + this.sensitivity)
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
                width: 0,
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

        const properties = {
            point: [x, y],
            width: this.brushSize * scaleFactor,
            height: this.brushSize * scaleFactor,
            fillColor: this.isEraser ? 'transparent' : this.brushColor,
            borderColor: this.brushColor
        };

        this.previewArtist.drawRect(properties);
    }

    bind() {
        document.addEventListener('pointermove', e => {
            if (this.isDrawing && this.enabled) {
                this.planStroke(e);
            }
        });

        this.artist.canvas.addEventListener('mousedown', e => {
            this.isDrawing = true;
        });

        this.artist.canvas.addEventListener('mouseup', e => {
            this.isDrawing = false;
            this.brushPos = undefined;
            this.history.takeSnapshot();
        });
    }

    increaseBrushSize() {
        this.brushSize++;
        this.drawBrushPreview();
    }

    decreaseBrushSize() {
        this.brushSize = Math.max(1, this.brushSize - 1);
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