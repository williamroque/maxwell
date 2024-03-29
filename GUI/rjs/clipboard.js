class Clipboard {
    constructor(pen, selectionArtist) {
        this.pen = pen;
        this.selectionArtist = selectionArtist;

        this.items = [];
        this.registry = {};
    }

    changePen(pen) {
        this.pen = pen;
    }

    createBuffer() {
        const bufferCanvas = document.createElement('canvas');
        const bufferCtx = bufferCanvas.getContext('2d');

        bufferCanvas.width = this.selectionArtist.canvas.width;
        bufferCanvas.height = this.selectionArtist.canvas.height;

        bufferCtx.drawImage(this.selectionArtist.canvas, 0, 0);

        return bufferCanvas;
    }

    store() {
        const bufferCanvas = this.createBuffer();

        this.items.unshift(bufferCanvas);
        this.items.splice(10);
    }

    register(key) {
        if (key) {
            this.registry[key] = this.createBuffer();
            this.store();
        }
    }

    paste(key) {
        const index = key.toLowerCase() === 'p' ? 0 : parseInt(key);

        if (this.pen.currentPoint) {
            const [ x, y ] = this.pen.currentPoint;

            if (isNaN(key) && key in this.registry && key.toLowerCase() !== 'p') {
                const selection = new Selection(
                    this.selectionArtist,
                    this.pen.artist
                );
                selection.capture(this.registry[key], x, y);
                this.pen.selection = selection;
                this.pen.mode = penModes.SELECTION;

                this.pen.history.takeSnapshot();
            } else if (index < this.items.length) {
                const selection = new Selection(
                    this.selectionArtist,
                    this.pen.artist
                );
                selection.capture(this.items[index], x, y);
                this.pen.selection = selection;
                this.pen.mode = penModes.SELECTION;

                this.pen.history.takeSnapshot();
            }
        }
    }
}
