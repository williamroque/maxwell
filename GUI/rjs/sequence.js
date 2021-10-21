class Camera {
    constructor(canvas, savePath, mimeType) {
        this.canvas = canvas;
        this.savePath = savePath;
        this.mimeType = mimeType;
    }


    start() {
        this.chunks = [];

        this.stream = this.canvas.captureStream(0); 

        this.mediaRecorder = new MediaRecorder(stream, {
            mimeType: this.mimeType
        });

        this.mediaRecorder.ondataavailable = e => this.chunks.push(e.data);
        this.mediaRecorder.onstop = () => this.develop;

        this.mediaRecorder.start();
    }


    capture() {
        this.stream.getVideoTracks()[0].requestFrame();
    }


    stop() {
        this.mediaRecorder.stop();
    }


    develop() {
        const blob = new Blob(this.chunks, { type: this.mimeType });

        let reader = new FileReader();

        reader.onload = () => {
            let buffer = new Buffer(reader.result);

            fs.writeFile(this.savePath, buffer, {}, (err, res) => {
                if (err) {
                    console.error(err);
                    return;
                }
            })
        };

        reader.readAsArrayBuffer(blob);
    }
}


class Sequence {
    constructor(artist, backgroundArtist, frames, frameDuration, savePath, background, awaitsCompletion) {
        this.artist = artist;
        this.backgroundArtist = backgroundArtist;

        this.frames = frames;
        this.frameDuration = frameDuration * 1000;
        this.savePath = savePath;
        this.background = background;
        this.awaitsCompletion = awaitsCompletion;

        this.isPlaying = false;

        this.camera;
    }


    static runFromArgs(artist, backgroundArtist, args) {
        const { frames, frameDuration, savePath, background, awaitsCompletion } = args;

        const sequence = new Sequence(artist, backgroundArtist, frames, frameDuration, savePath, background, awaitsCompletion);

        sequence.play();

        return sequence;
    }


    computeFrames() {
        let frames = [];

        for (const frame of this.frames) {
            const bufferCanvas = document.createElement('canvas');
            const bufferArtist = new Artist(bufferCanvas);

            bufferCanvas.width = this.artist.canvas.width;
            bufferCanvas.height = this.artist.canvas.height;

            for (const shape of frame) {
                bufferArtist.draw(shape);
            }

            frames.push(bufferCanvas);
        }

        return frames;
    }


    renderFrame(frames) {
        if (frames.length === 0) {
            if (this.awaitsCompletion) {
                ipcRenderer.sendSync('send-results', ['completed']);
                this.awaitsCompletion = false;
            }

            return;
        }

        const frame = frames.shift();

        this.artist.clear();

        if (frame.length === 0) {
            this.renderFrame(frames);
        } else {
            if (Properties.rerenderBackground) {
                for (const shape of this.background) {
                    this.backgroundArtist.draw(shape);
                }

                Properties.rerenderBackground = false;
            }

            this.artist.capture(frame);

            if (this.isPlaying) {
                setTimeout(this.renderFrame.bind(this), this.frameDuration, frames);
            }
        }
    }


    play() {
        this.isPlaying = true;

        if (this.savePath !== 'none') {
            this.camera = new Camera(this.artist.canvas, this.savePath, 'video/webm');
        }

        for (const shape of this.background) {
            this.backgroundArtist.draw(shape);
        }

        const computedFrames = this.computeFrames();

        this.renderFrame(computedFrames);
    }

    stop() {
        this.isPlaying = false;

        if (this.awaitsCompletion) {
            ipcRenderer.sendSync('send-results', ['completed']);
            this.awaitsCompletion = false;
        }
    }
}
