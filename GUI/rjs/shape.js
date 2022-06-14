class Shape {
    constructor(pen, artist) {
        this.pen = pen;
        this.artist = artist;
        this.lengths = [];

        this.focusedLength = -1;

        this.firstPhase = this.defaultLengths.length + 1;
        this.phase = this.firstPhase;

        this.started = false;
        this.currentPoint;
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

    start(e) {
        const point = this.moveToCenter([e.pageX | 0, e.pageY | 0]);
        this.currentPoint = point;

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
            this.artist.moveCanvas(...point);
        } else {
            this.render(point);
        }
    }

    switchPhase() {
        this.phase--;

        if (this.phase === 0) {
            this.render();
            this.pen.artist.capture(
                this.artist.canvas,
                0, 0,
                ...this.currentPoint
            );
            this.artist.hideCanvas();
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

    shapeBounds() {
        return this.allLengths.map(l => l + this.pen.brush.brushSize * 4);
    }

    render(point) {
        const endpoints = [
            [[0, 0],
             [1, 0]],
            [[0, 0],
             [0, 1]]
        ];

        if (point) {
            const [origin, end] = endpoints[this.focusedLength];

            point = [
                Math.max(0, point[0] - parseInt(this.artist.canvas.style.left)),
                Math.max(0, point[1] - parseInt(this.artist.canvas.style.top))
            ];

            this.lengths[this.focusedLength] = this.projectDistance(
                origin, end,
                point
            );
        }

        const lengths = this.allLengths;

        this.artist.clear();
        this.artist.resizeCanvas(...this.shapeBounds());

        const centerPoint = [
            this.artist.canvas.width / 2,
            this.artist.canvas.height / 2
        ];

        this.artist.drawRect({
            point: centerPoint,
            width: lengths[0],
            height: lengths[1],
            fillColor: 'transparent',
            borderColor: this.pen.brush.color,
            borderWidth: this.pen.brush.brushSize * 4
        });

        if (point) {
            const [origin, end] = endpoints[this.focusedLength];
            const projectedLength = this.lengths[this.focusedLength];

            this.renderLine(
                [origin[0] * projectedLength, origin[1] * projectedLength],
                [end[0] * projectedLength, end[1] * projectedLength],
                10
            );
        }
    }
}


class Circle extends Shape {
    static defaultLengths = [25];

    shapeBounds() {
        const radius = this.allLengths[0];
        const size = radius*2 + this.pen.brush.brushSize*4;

        return [size, size];
    }

    render(point) {
        const oldBounds = this.shapeBounds();

        if (point) {
            const x = point[0] - (this.currentPoint[0] + oldBounds[0]/2);

            this.lengths[0] = Math.max(0, x);
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

        this.currentPoint = [
            this.currentPoint[0] + oldBounds[0]/2 - bounds[0]/2,
            this.currentPoint[1] + oldBounds[1]/2 - bounds[1]/2
        ];
        this.artist.moveCanvas(...this.currentPoint);

        if (point) {
            const projectedLength = this.allLengths[0];

            this.renderLine(
                [bounds[0]/2, bounds[1]/2],
                [bounds[0], bounds[1]/2],
                6
            );
        }
    }
}
