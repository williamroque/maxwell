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


    renderFrame(i = 0) {
        if (i >= this.frames.length) {
            if (this.awaitsCompletion) {
                ipcRenderer.sendSync('send-results', ['completed']);
                this.awaitsCompletion = false;
            }

            if (this.camera) {
                this.camera.stop();
            }

            return;
        }

        const frame = this.frames[i];

        this.artist.clear();

        if (frame.length === 0) this.renderFrame.call(this, i + 1);

        if (Properties.rerenderBackground) {
            for (const shape of this.background) {
                this.backgroundArtist.draw(shape);
            }

            Properties.rerenderBackground = false;
        }

        for (const shape of frame) {
            this.artist.draw(shape);
        }

        if (this.camera) {
            this.camera.capture();
        }

        if (this.isPlaying) {
            setTimeout(this.renderFrame.bind(this), this.frameDuration, i + 1);
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

        this.renderFrame();
    }

    stop() {
        this.isPlaying = false;

        if (this.awaitsCompletion) {
            ipcRenderer.sendSync('send-results', ['completed']);
            this.awaitsCompletion = false;
        }
    }
}
