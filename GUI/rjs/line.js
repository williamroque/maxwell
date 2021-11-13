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

        this.pen.artist.drawCurve({
            points: [this.startPos, [x, y]],
            color: this.pen.brush.color,
            width: this.pen.brush.brushSize * 4,
            arrow: false,
            arrowHead: [],
            fillColor: 'transparent'
        });
    }
}
