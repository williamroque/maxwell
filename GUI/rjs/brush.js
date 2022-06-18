class Brush {
    constructor(artist, previewArtist) {
        this.artist = artist;
        this.previewArtist = previewArtist;

        this.enabled = false;

        this.isEraser = false;
        this.brushSize = 1/2;
        this.eraserSize = 8;
        this.sensitivity = 1;

        this.colorIndex = 0;
        this.previousColorIndex = 0;

        this.darkColorOptions = ['#fdf4c1', '#6CA17A', '#cc6666', '#81a2be'];
        this.lightColorOptions = ['#121112', '#6CA17A', '#cc6666', '#81a2be'];

        this.previewArtist.canvas.style.borderColor = this.color;

        this.lastPos;
    }

    get colorOptions() {
        return Properties.isLightMode ? this.lightColorOptions : this.darkColorOptions;
    }

    get color() {
        return this.colorOptions[this.colorIndex];
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
                fillColor: this.color,
                borderColor: this.color,
                borderWidth: 0
            };

            this.artist.drawArc(properties);
        }
    }

    drawPreview() {
        this.previewArtist.clear();

        const x = this.previewArtist.canvas.width / 2;
        const y = this.previewArtist.canvas.height / 2;

        const scaleFactor = 4;
        const scaleOffset = 2;
        const size = (this.isEraser ? this.eraserSize : this.brushSize) * scaleFactor + scaleOffset;
        const fillColor = this.isEraser ? 'transparent' : this.color;

        this.previewArtist.canvas.style.borderColor = this.color;

        const properties = {
            point: [x, y],
            width: size | 0,
            height: size | 0,
            fillColor: fillColor,
            borderColor: this.color,
            borderWidth: 2
        };

        this.previewArtist.drawRect(properties);
    }

    planStroke(e) {
        const brushSize = this.isEraser ? this.eraserSize : this.brushSize;

        if (this.lastPos) {
            const dx = Math.abs(e.pageX - this.lastPos[0]);
            const dy = Math.abs(e.pageY - this.lastPos[1]);

            const gPosDiff = dx > dy ? 0 : 1;

            const direction = [
                Math.min(e.pageX - this.lastPos[0], 0) ? -1 : 1,
                Math.min(e.pageY - this.lastPos[1], 0) ? -1 : 1,
            ];

            for (let i = 0; i < [dx, dy][gPosDiff]; i++) {
                this.drawBrush(
                    ((gPosDiff ? dx / dy * i : i) || 0) * direction[0] + this.lastPos[0],
                    ((gPosDiff ? i : dy / dx * i) || 0) * direction[1] + this.lastPos[1],
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

        this.lastPos = [e.pageX, e.pageY];
    }

    lift() {
        this.lastPos = undefined;
    }

    increaseSize() {
        if (this.isEraser) {
            this.eraserSize++;
        } else {
            this.brushSize += 1/2;
        }

        this.drawPreview();
    }

    decreaseSize() {
        if (this.isEraser) {
            this.eraserSize = Math.max(1, this.eraserSize - 1);
        } else {
            this.brushSize = Math.max(1/2, this.brushSize - 1/2);
        }

        this.drawPreview();
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
        this.drawPreview();
    }

    previousColor() {
        const colorCount = this.colorOptions.length;

        this.colorIndex = (this.colorIndex + colorCount - 1) % colorCount;
        this.previousColorIndex = this.colorIndex;
        this.drawPreview();
    }

    toggleEraser() {
        this.isEraser = !this.isEraser;
        this.drawPreview();
    }
}
