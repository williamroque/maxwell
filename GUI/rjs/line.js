class Line {
    constructor(pen) {
        this.pen = pen;

        this.startPos;
        this.started = false;
    }

    start(e) {
        this.startPos = [e.pageX|0, e.pageY|0];
        this.started = true;
    }

    update(e) {
        const x = e.pageX|0;
        const y = e.pageY|0;

        this.pen.history.travel(0);

        const points = [this.startPos, [x, y]];

        if (this.pen.hasStyle('dashed')) {
            this.pen.artist.ctx.setLineDash([5, 10]);
        }

        let arrowHead = [];

        if (this.pen.hasStyle('arrow')) {
            arrowHead = this.pen.artist.calculateArrowHead(
                this.pen.brush.brushSize * 8,
                ...points,
                points[1]
            );
        }

        this.pen.artist.drawCurve({
            points: points,
            color: this.pen.brush.color,
            width: this.pen.brush.brushSize * 4,
            arrow: false,
            arrowHead: arrowHead,
            fillColor: 'transparent'
        });

        this.pen.artist.ctx.setLineDash([]);
    }
}
