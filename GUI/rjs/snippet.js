class Snippet {
    constructor(data, pen) {
        this.type = data['type'];

        switch (this.type) {
        case 'points':
            this.data = this.adjustPoints(data['data']);
            break;
        case 'svg':
            this.data = data['data'];
            break;
        default:
            throw 'Snippet should be of either "points" or "svg" type.';
        }

        this.pen = pen;
    }

    adjustPoints(points) {
        let xMin = Infinity;
        let yMin = Infinity;

        for (const point of points) {
            xMin = Math.min(xMin, point[0]);
            yMin = Math.min(yMin, point[1]);
        }

        let adjustedPoints = [];
        for (const point of points) {
            adjustedPoints.push([
                point[0] - xMin,
                point[1] - yMin,
                point[2],
                point[3]
            ]);
        }

        return adjustedPoints;
    }

    draw(x, y) {
        if (this.type === 'points') {
            const eraserState = this.pen.isEraser;

            for (const point of this.data) {
                this.pen.isEraser = point[3];

                this.pen.drawBrush(
                    point[0] + x,
                    point[1] + y,
                    point[2]
                );
            }

            this.pen.isEraser = eraserState;
        } else if (this.type === 'svg') {
            this.pen.artist.drawSVG({
                data: this.data[0],
                point: [x, y],
                transform: this.data.slice(1),
                fillColor: this.pen.brushColor
            });
        }
    }

    toJSON() {
        return {
            type: this.type,
            data: this.data
        };
    }
}


class SnippetLibrary {
    constructor(pen, path) {
        this.snippets = {};
        this.isRecording = false;

        this.currentKey;

        this.pen = pen;
        this.path = path;

        this.load();
    }

    changePen(pen) {
        this.pen = pen;

        for (const key in this.snippets) {
            this.snippets[key].pen = pen;
        }
    }

    record(key) {
        if (!this.pen.enabled) {
            this.pen.toggle();
        }

        if (this.isRecording) {
            this.isRecording = false;
            this.snippets[this.currentKey] = new Snippet(
                {
                    type: 'points',
                    data: this.pen.recording
                },
                this.pen
            );
            this.pen.stopRecording();
            this.pen.history.thaw();

            this.save();

            return false;
        }

        if (key) {
            this.isRecording = true;
            this.pen.startRecording();
            this.currentKey = key;
            this.pen.history.freeze();
        }

        return true;
    }

    play(key) {
        if (key in this.snippets && this.pen.currentPoint !== undefined) {
            const [ x, y ] = this.pen.currentPoint;

            this.snippets[key].draw(x, y);
            this.pen.history.takeSnapshot();
        }
    }

    load() {
        if (fs.existsSync(this.path)) {
            this.snippets = JSON.parse(fs.readFileSync(this.path));

            for (const key in this.snippets) {
                this.snippets[key] = new Snippet(this.snippets[key], this.pen);
            }
        }
    }

    save() {
        fs.writeFileSync(
            this.path,
            JSON.stringify(this.snippets)
        );
    }
}
