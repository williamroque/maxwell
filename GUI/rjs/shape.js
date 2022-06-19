class Shape {
    constructor(pen, artist) {
        this.pen = pen;
        this.artist = artist;
        this.lengths = [];

        this.focusedLength = -1;

        this.firstPhase = this.defaultLengths.length + 2;
        this.phase = this.firstPhase;

        this.started = false;
        this.currentPoint;
        this.adjustedPoint;

        this.alpha;

        this.theta = 0;
        this.ctxTheta = 0;

        this.defaultSize;
    }

    cancel() {
        this.artist.hideCanvas();
    }

    get defaultLengths() {
        return this.constructor.defaultLengths;
    }

    get allLengths() {
        const lengths = this.lengths
              .concat(this.defaultLengths)
              .slice(0, this.defaultLengths.length);

        return lengths;
    }

    get angle() {
        return this.theta + (this.alpha || 0);
    }

    get pointFromCenter() {
        return this.moveFromCenter(this.adjustedPoint);
    }

    adjustCenter(oldBounds, newBounds) {
        this.adjustedPoint = [
            this.adjustedPoint[0] + oldBounds[0]/2 - newBounds[0]/2,
            this.adjustedPoint[1] + oldBounds[1]/2 - newBounds[1]/2
        ];

        this.artist.moveCanvas(...this.adjustedPoint);
    }

    renderLine(origin, end, factor) {
        this.artist.drawCurve({
            points: [origin, end],
            color: '#DC5A5E',
            width: this.pen.brush.brushSize * factor,
            arrow: false,
            arrowHead: [],
            fillColor: 'transparent'
        });
    }

    moveToCenter(point) {
        const bounds = this.shapeBounds();

        return [point[0] - bounds[0]/2, point[1] - bounds[1]/2];
    }

    moveFromCenter(point) {
        const bounds = this.shapeBounds();

        return [point[0] + bounds[0]/2, point[1] + bounds[1]/2];
    }

    start(e) {
        const point = this.moveToCenter([e.pageX | 0, e.pageY | 0]);
        this.currentPoint = point;
        this.adjustedPoint = point;

        this.artist.clear();

        this.artist.resizeCanvas(...this.shapeBounds());
        this.artist.moveCanvas(...point);
        this.render();
        this.artist.showCanvas();

        this.started = true;
    }

    update(e) {
        let point = [e.pageX | 0, e.pageY | 0];

        if (this.phase === this.firstPhase) {
            point = this.moveToCenter(point);

            this.currentPoint = point;
            this.adjustedPoint = point;
            this.artist.moveCanvas(...point);
        } else {
            this.render(point);
        }
    }

    switchPhase() {
        this.phase--;

        if (this.phase === 0) {
            const oldBounds = this.shapeBounds();
            this.defaultSize = Math.sqrt(oldBounds[0]**2 + oldBounds[1]**2);
            this.adjustCenter(oldBounds, this.shapeBounds());

            this.ctxTheta = this.angle;

            this.render();

            this.pen.artist.capture(
                this.artist.canvas,
                0, 0,
                ...this.adjustedPoint
            );
            this.artist.hideCanvas();
            this.artist.rotateCanvas(null, null);
            this.artist.rotate(0);
        } else if (this.phase === 1) {
            if (this.constructor.skipRotation) {
                this.switchPhase();
                return;
            }

            this.render();
            this.pen.rotate();
        } else {
            this.focusedLength++;
        }

        return this.phase;
    }

    projectDistance(origin, end, point) {
        const dx = end[0] - origin[0];
        const dy = end[1] - origin[1];

        const norm = Math.sqrt(dx*dx + dy*dy);

        const normal = [dx/norm, dy/norm];

        return point[0]*normal[0] + point[1]*normal[1];
    }
}


class Rect extends Shape {
    static defaultLengths = [50, 50];
    static skipRotation = false;

    shapeBounds() {
        if (this.defaultSize) {
            return [this.defaultSize, this.defaultSize];
        }

        return this.allLengths.map(l => Math.abs(l) + this.pen.brush.brushSize * 4);
    }

    render(point) {
        if (point) {
            if (this.focusedLength === 0) {
                this.lengths[this.focusedLength] = point[0] - this.currentPoint[0];
            } else {
                this.lengths[this.focusedLength] = point[1] - this.currentPoint[1];
            }
        }

        const lengths = this.allLengths;
        const bounds = this.shapeBounds();

        this.artist.clear();
        this.artist.resizeCanvas(...bounds);

        this.artist.rotateCanvas(this.angle);
        this.artist.rotate(this.ctxTheta);

        if (point) {
            this.adjustedPoint = [
                lengths[0] < 0 && this.focusedLength === 0 ? point[0] : this.adjustedPoint[0],
                lengths[1] < 0 && this.focusedLength === 1 ? point[1] : this.adjustedPoint[1]
            ];

            this.artist.moveCanvas(...this.adjustedPoint);
        }

        const centerPoint = [
            this.artist.canvas.width / 2,
            this.artist.canvas.height / 2
        ];

        this.artist.drawRect({
            point: centerPoint,
            width: Math.abs(lengths[0]),
            height: Math.abs(lengths[1]),
            fillColor: 'transparent',
            borderColor: this.pen.brush.color,
            borderWidth: this.pen.brush.brushSize * 4
        });

        if (point) {
            const length = this.lengths[this.focusedLength];

            if (this.focusedLength === 0) {
                this.renderLine([0, 0], [Math.abs(length), 0], 10);
            } else {
                this.renderLine([0, 0], [0, Math.abs(length)], 10);
            }
        }
    }
}


class Circle extends Shape {
    static defaultLengths = [25];
    static skipRotation = true;

    shapeBounds() {
        if (this.defaultSize) {
            return [this.defaultSize, this.defaultSize];
        }

        const radius = this.allLengths[0];
        const size = radius*2 + this.pen.brush.brushSize*4;

        return [size, size];
    }

    render(point) {
        const oldBounds = this.shapeBounds();

        let x, y;

        if (point) {
            x = point[0] - (this.adjustedPoint[0] + oldBounds[0]/2);
            y = point[1] - (this.adjustedPoint[1] + oldBounds[1]/2);

            this.lengths[0] = Math.sqrt(x**2 + y**2);
        }

        const radius = this.allLengths[0];
        const bounds = this.shapeBounds();

        this.artist.clear();
        this.artist.resizeCanvas(...bounds);

        const centerPoint = [
            bounds[0] / 2,
            bounds[1] / 2
        ];

        this.artist.drawArc({
            point: centerPoint,
            radius: radius,
            theta_1: 0,
            theta_2: 2*Math.PI,
            fillColor: 'transparent',
            borderColor: this.pen.brush.color,
            borderWidth: this.pen.brush.brushSize * 4
        });

        this.adjustCenter(oldBounds, bounds);

        if (point) {
            this.renderLine(
                centerPoint,
                [centerPoint[0] + x, centerPoint[1] + y],
                6
            );
        }
    }
}


class Arc extends Shape {
    static defaultLengths = [25, 0, 2*Math.PI];
    static skipRotation = true;

    shapeBounds() {
        if (this.defaultSize) {
            return [this.defaultSize, this.defaultSize];
        }

        const radius = this.allLengths[0];
        const size = radius*2 + this.pen.brush.brushSize*4;

        return [size, size];
    }

    render(point) {
        const oldBounds = this.shapeBounds();

        let x, y;

        if (point) {
            if (this.focusedLength === 0) {
                x = point[0] - (this.adjustedPoint[0] + oldBounds[0]/2);
                y = point[1] - (this.adjustedPoint[1] + oldBounds[1]/2);

                this.lengths[0] = Math.sqrt(x**2 + y**2);
            } else {
                const theta = Math.atan2(
                    this.pointFromCenter[1] - point[1],
                    point[0] - this.pointFromCenter[0]
                );

                this.lengths[this.focusedLength] = -theta;
            }
        }

        const lengths = this.allLengths;
        const radius = lengths[0];

        const bounds = this.shapeBounds();

        this.artist.clear();
        this.artist.resizeCanvas(...bounds);

        const centerPoint = [
            bounds[0] / 2,
            bounds[1] / 2
        ];

        this.artist.drawArc({
            point: centerPoint,
            radius: radius,
            theta_1: lengths[1],
            theta_2: lengths[2],
            fillColor: 'transparent',
            borderColor: this.pen.brush.color,
            borderWidth: this.pen.brush.brushSize * 4
        });

        this.adjustCenter(oldBounds, bounds);

        if (point) {
            if (this.focusedLength === 0) {
                this.renderLine(
                    centerPoint,
                    [centerPoint[0] + x, centerPoint[1] + y],
                    6
                );
            } else {
                const theta = lengths[this.focusedLength];

                this.renderLine(
                    centerPoint,
                    [
                        centerPoint[0] + radius*Math.cos(theta),
                        centerPoint[1] + radius*Math.sin(theta)
                    ],
                    6
                );
            }
        }
    }
}


class RTriangle extends Shape {
    static defaultLengths = [50, 50];
    static skipRotation = false;

    shapeBounds() {
        if (this.defaultSize) {
            return [this.defaultSize*2, this.defaultSize*2];
        }

        return this.allLengths.map(l => Math.abs(l) + this.pen.brush.brushSize * 4);
    }

    moveToCenter(point) {
        const bounds = this.shapeBounds();

        const midpoint = [
            bounds[0]/3, bounds[1]*2/3
        ];

        return [point[0] - midpoint[0], point[1] - midpoint[1]];
    }

    render(point) {
        if (point) {
            if (this.focusedLength === 0) {
                this.lengths[this.focusedLength] = point[0] - this.currentPoint[0];
            } else {
                this.lengths[this.focusedLength] = point[1] - this.currentPoint[1];
            }
        }

        const lengths = this.allLengths;
        const absLengths = lengths.map(Math.abs);

        this.artist.clear();
        this.artist.resizeCanvas(...this.shapeBounds());

        const centerPoint = [
            this.artist.canvas.width / 2,
            this.artist.canvas.height / 2
        ];

        const points = [
            [centerPoint[0] - lengths[0]/2, centerPoint[1] - lengths[1]/2],
            [centerPoint[0] - lengths[0]/2, centerPoint[1] + lengths[1]/2],
            [centerPoint[0] + lengths[0]/2, centerPoint[1] + lengths[1]/2],
            [centerPoint[0] - lengths[0]/2, centerPoint[1] - lengths[1]/2],
        ];

        const midpoint = [
            points.slice(1).reduce((a, b) => a + b[0], 0)/3,
            points.slice(1).reduce((a, b) => a + b[1], 0)/3,
        ];

        this.artist.rotateCanvas(this.angle, midpoint);
        this.artist.rotate(this.ctxTheta, midpoint);

        if (point) {
            this.adjustedPoint = [
                lengths[0] < 0 && this.focusedLength === 0 ? point[0] : this.adjustedPoint[0],
                lengths[1] < 0 && this.focusedLength === 1 ? point[1] : this.adjustedPoint[1]
            ];

            this.artist.moveCanvas(...this.adjustedPoint);
        }

        this.artist.drawCurve({
            points: points,
            color: this.pen.brush.color,
            width: this.pen.brush.brushSize * 4,
            arrowHead: [],
            fillColor: 'transparent',
        });

        if (point) {
            switch (this.focusedLength) {
            case 0:
                this.renderLine(points[1], points[2], 10);
                break;
            case 1:
                this.renderLine(points[0], points[1], 10);
                break;
            }
        }
    }
}
