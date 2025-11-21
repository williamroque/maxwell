class Selection {
    constructor(artist, penArtist) {
        this.artist = artist;
        this.penArtist = penArtist;

        this.copyMode = false;

        this.startPos;
        this.endPos;

        this.started = false;
        this.completed = false;

        this.alpha;

        this.theta = 0;
        this.ctxTheta = 0;

        this.currentPoint;
    }

    get angle() {
        return this.theta + (this.alpha || 0);
    }

    get centerPoint() {
        if (!this.currentPoint) return;

        const [x, y] = this.currentPoint;

        const width = Math.abs(this.endPos[0] - this.startPos[0]);
        const height = Math.abs(this.endPos[1] - this.startPos[1]);

        return [x + width/2, y + height/2];
    }

    getBounds() {
        if (!this.completed) return {};

        const [sx, sy] = this.startPos;
        const [ex, ey] = this.endPos;

        let bounds = {
            TL: [sx < ex ? sx : ex , sy < ey ? sy : ey],
            BL: [sx < ex ? sx : ex , sy > ey ? sy : ey],
            TR: [sx > ex ? sx : ex , sy < ey ? sy : ey],
            BR: [sx > ex ? sx : ex , sy > ey ? sy : ey],
        };

        bounds.width = bounds.TR[0] - bounds.TL[0];
        bounds.height = bounds.BL[1] - bounds.TL[1];

        return bounds;
    }

    capture(canvas, x, y) {
        this.artist.moveCanvas(x, y);
        this.artist.resizeCanvas(canvas.width, canvas.height);
        this.artist.showCanvas();

        this.artist.capture(canvas);

        this.startPos = [x + canvas.width, y + canvas.height];
        this.endPos = [x, y];

        this.started = true;
        this.completed = true;
    }

    start(e) {
        const x = e.pageX|0;
        const y = e.pageY|0;

        this.startPos = [x, y];

        this.artist.moveCanvas(x, y);
        this.artist.resizeCanvas(0, 0);
        this.artist.showCanvas();

        this.started = true;
    }

    change(e) {
        const x = e.pageX|0;
        const y = e.pageY|0;

        const dx = x - this.startPos[0];
        const dy = y - this.startPos[1];

        this.artist.resizeCanvas(Math.abs(dx), Math.abs(dy));

        this.artist.moveCanvas(
            dx <= 0 ? x : null,
            dy <= 0 ? y : null
        );
    }

    end(e) {
        this.isSelecting = false;

        const { width, height, x, y } = this.artist.canvas.getBoundingClientRect();

        if (!width || !height) {
            this.cancel();
            return;
        }

        this.artist.capture(this.penArtist.canvas, x, y);

        if (!this.copyMode) {
            this.penArtist.clear(x, y, width, height);
        }

        this.endPos = [e.pageX|0, e.pageY|0];

        this.currentPoint = this.getSelectionHandle(e);

        this.completed = true;
    }

    getSelectionHandle(e) {
        const x = e.pageX|0;
        const y = e.pageY|0;
        const dx = this.endPos[0] - this.startPos[0];
        const dy = this.endPos[1] - this.startPos[1];

        return [dx > 0 ? x - dx : x, dy > 0 ? y - dy : y];
    }

    move(e) {
        const [x, y] = this.getSelectionHandle(e);
        this.currentPoint = [x, y];

        this.artist.moveCanvas(x, y);
    }

    apply(e) {
        this.artist.rotateRedraw(this.angle);

        this.penArtist.capture(
            this.artist.canvas,
            0, 0,
            ...this.artist.getCoordinates()
        );

        this.artist.rotateCanvas(0);
        this.artist.clear();
        this.artist.hideCanvas();
    }

    delete(key, clipboard) {
        clipboard.register(key);

        this.artist.clear();
        this.artist.hideCanvas();
    }

    cancel() {
        this.artist.clear();
        this.artist.hideCanvas();
    }
}
