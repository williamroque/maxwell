class Selection {
    constructor(artist, penArtist) {
        this.artist = artist;
        this.penArtist = penArtist;

        this.copyMode = false;

        this.startPos;
        this.endPos;

        this.started = false;
        this.completed = false;
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

        this.artist.moveCanvas(x, y);
    }

    apply(e) {
        const [x, y] = this.getSelectionHandle(e);

        this.penArtist.capture(
            this.artist.canvas,
            0, 0,
            x, y
        );
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
