// top-level require for perfect-freehand so it's available at module load
const perfectFreehand = (() => {
    try {
        const mod = require('perfect-freehand');
        if (typeof mod === 'function') return mod;
        if (mod && typeof mod.default === 'function') return mod.default;
        console.warn('perfect-freehand: unexpected export, expected function');
        return null;
    } catch (e) {
        console.warn('perfect-freehand not available:', e);
        return null;
    }
})();

class Brush {
    constructor(pen, artist, previewArtist) {
        this.pen = pen;
        this.artist = artist;
        this.previewArtist = previewArtist;

        this.enabled = false;

        this.isEraser = false;
        this.brushSize = 1;
        this.eraserSize = 8;
        this.sensitivity = 1;

        this.colorIndex = 0;
        this.previousColorIndex = 0;

        this.darkColorOptions = ['#fdf4c1', '#6CA17A', '#cc6666', '#81a2be'];
        this.lightColorOptions = ['#121112', '#6CA17A', '#cc6666', '#81a2be'];

        this.previewArtist.canvas.style.borderColor = this.color;

        this.points = [];
    }

    // perfect-freehand is required at module top as `perfectFreehand`

    get colorOptions() {
        return Properties.isLightMode ? this.lightColorOptions : this.darkColorOptions;
    }

    get color() {
        return this.colorOptions[this.colorIndex];
    }

    drawBrush(e) {
        const brushSize = this.isEraser ? this.eraserSize : this.brushSize;
        const adjustedBrushSize = brushSize + Math.pow(brushSize * e.pressure, 1 + this.sensitivity);

        const x = e.pageX | 0;
        const y = e.pageY | 0;

        const pressure = (e.pressure === undefined) ? 1 : e.pressure;
        const point = [x, y, pressure];

        this.points.push(point);

        // Use the pen overlay canvas for live previews (this.artist is the pen overlay).
        const previewCtx = this.artist._realCtx;

        if (this.isEraser) {
            this.artist.clearCircle(
                x, y,
                adjustedBrushSize
            );
        } else {
            if (this.points.length > 1) {
                this.pen.history.travel(0);

                // If perfect-freehand is available, generate a polygonal stroke
                const getStroke = perfectFreehand;
                if (getStroke) {
                    // Use all sampled points so the preview shows the full stroke start-to-current
                    const pts = this.points.map(p => [p[0], p[1], p[2] || 1]);

                    const options = {
                        size: adjustedBrushSize * 2,
                        thinning: 0.5 + (this.sensitivity - 1) * 0.05,
                        smoothing: 0.6,
                        streamline: 0.5,
                        simulatePressure: true
                    };

                    let stroke = [];
                    try {
                        stroke = getStroke(pts, options);
                    } catch (err) {
                        console.warn('perfect-freehand error:', err);
                    }

                    if (stroke.length > 1) {
                        // draw preview to the preview canvas (or fallback to real canvas)
                        const ctxReal = previewCtx;
                        ctxReal.save();
                        ctxReal.fillStyle = this.color;
                        ctxReal.lineJoin = 'round';
                        ctxReal.lineCap = 'round';

                        ctxReal.beginPath();
                        ctxReal.moveTo(stroke[0][0], stroke[0][1]);
                        for (let i = 1; i < stroke.length; i++) {
                            ctxReal.lineTo(stroke[i][0], stroke[i][1]);
                        }
                        ctxReal.closePath();
                        ctxReal.fill();
                        ctxReal.restore();
                    }
                } else {
                    // Fallback: draw a smooth curve preview on the real context
                    let curve = [];
                    const ctxReal = previewCtx;

                    ctxReal.save();
                    ctxReal.strokeStyle = this.color;
                    ctxReal.lineWidth = adjustedBrushSize * 2;
                    ctxReal.lineCap = 'round';
                    ctxReal.lineJoin = 'round';

                    for (const pt of this.points) {
                        curve.push([pt[0], pt[1]]);

                        if (curve.length === 4) {
                            // draw cubic bezier on real ctx
                            ctxReal.beginPath();
                            ctxReal.moveTo(curve[0][0], curve[0][1]);
                            ctxReal.bezierCurveTo(
                                curve[1][0], curve[1][1],
                                curve[2][0], curve[2][1],
                                curve[3][0], curve[3][1]
                            );
                            ctxReal.stroke();
                            curve = [curve[3]];
                        }
                    }
                    if (curve.length > 1) {
                        ctxReal.beginPath();
                        ctxReal.moveTo(curve[0][0], curve[0][1]);
                        for (let i = 1; i < curve.length; i++) {
                            ctxReal.lineTo(curve[i][0], curve[i][1]);
                        }
                        ctxReal.stroke();
                    }

                    ctxReal.restore();
                }
            } else {
                // preview single-point as filled circle only on preview canvas (or real canvas fallback)
                const ctxReal = previewCtx;
                ctxReal.save();
                ctxReal.fillStyle = this.color;
                ctxReal.beginPath();
                ctxReal.arc(point[0], point[1], adjustedBrushSize, 0, 2 * Math.PI, false);
                ctxReal.fill();
                ctxReal.restore();
            }
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

    lift() {
        // finalize stroke on lift: draw full-stroke polygon once
        const getStroke = perfectFreehand;

        if (!this.points || this.points.length === 0) {
            this.points = [];
            return;
        }

        // If the stroke is very short (single point or negligible movement), treat as a dot
        const first = this.points[0];
        const last = this.points[this.points.length - 1];
        const dx = Math.abs(last[0] - first[0]);
        const dy = Math.abs(last[1] - first[1]);
        const smallThreshold = 4; // pixels

        const commitDot = (this.points.length === 1) || (dx < smallThreshold && dy < smallThreshold);

        if (commitDot) {
            const p = last;
            const pressure = p[2] || 1;
            const baseSize = this.isEraser ? this.eraserSize : this.brushSize;
            const adjustedBrushSize = baseSize + Math.pow(baseSize * pressure, 1 + this.sensitivity);

            // For tiny taps, render a smaller "dot" than the full stroke width so dots look proportional.
            const dotRadius = Math.max(1, Math.round(baseSize * (0.6 + 0.4 * pressure)));

            const ctx = this.artist.ctx;
            if (this.isEraser) {
                // keep eraser behavior unchanged
                if (typeof this.artist.clearCircle === 'function') {
                    this.artist.clearCircle(p[0], p[1], adjustedBrushSize);
                } else {
                    ctx.save();
                    ctx.beginPath();
                    ctx.arc(p[0], p[1], adjustedBrushSize, 0, 2 * Math.PI, false);
                    ctx.clip();
                    ctx.clearRect(p[0] - adjustedBrushSize - 1, p[1] - adjustedBrushSize - 1, adjustedBrushSize * 2 + 2, adjustedBrushSize * 2 + 2);
                    ctx.restore();
                }
            } else {
                ctx.save();
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(p[0], p[1], dotRadius, 0, 2 * Math.PI, false);
                ctx.fill();
                ctx.restore();
            }
        } else {
            // multi-point stroke: try perfect-freehand, but fall back to dot if it fails
            if (getStroke && !this.isEraser) {
                const pts = this.points.map(p => [p[0], p[1], p[2] || 1]);
                try {
                    const options = { size: this.brushSize * 2, thinning: 0.5, smoothing: 0.6, streamline: 0.5, simulatePressure: true };
                    const stroke = getStroke(pts, options);
                    if (stroke && stroke.length > 1) {
                        const ctx = this.artist.ctx;
                        ctx.save();
                        ctx.fillStyle = this.color;
                        ctx.lineJoin = 'round';
                        ctx.lineCap = 'round';
                        ctx.beginPath();
                        ctx.moveTo(stroke[0][0], stroke[0][1]);
                        for (let i = 1; i < stroke.length; i++) {
                            ctx.lineTo(stroke[i][0], stroke[i][1]);
                        }
                        ctx.closePath();
                        ctx.fill();
                        ctx.restore();
                    } else {
                        // fall back to drawing a circle at the last sample
                        const p = last;
                        const pressure = p[2] || 1;
                        const baseSize = this.brushSize;
                        const adjustedBrushSize = baseSize + Math.pow(baseSize * pressure, 1 + this.sensitivity);
                        const ctx = this.artist.ctx;
                        ctx.save();
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.arc(p[0], p[1], adjustedBrushSize, 0, 2 * Math.PI, false);
                        ctx.fill();
                        ctx.restore();
                    }
                } catch (err) {
                    console.warn('perfect-freehand finalize error:', err);
                    // fallback
                    const p = last;
                    const pressure = p[2] || 1;
                    const baseSize = this.brushSize;
                    const adjustedBrushSize = baseSize + Math.pow(baseSize * pressure, 1 + this.sensitivity);
                    const ctx = this.artist.ctx;
                    ctx.save();
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(p[0], p[1], adjustedBrushSize, 0, 2 * Math.PI, false);
                    ctx.fill();
                    ctx.restore();
                }
            } else if (this.isEraser) {
                // multi-point eraser: clear small circle at last sample
                const p = last;
                const pressure = p[2] || 1;
                const baseSize = this.eraserSize;
                const adjustedBrushSize = baseSize + Math.pow(baseSize * pressure, 1 + this.sensitivity);
                if (typeof this.artist.clearCircle === 'function') {
                    this.artist.clearCircle(p[0], p[1], adjustedBrushSize);
                }
            }
        }

        this.points = [];
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
