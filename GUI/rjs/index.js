const { ipcRenderer } = require('electron');
const fs = require('fs');
const { spawn } = require('child_process');

const canvas = document.querySelector('#python-canvas');
const ctx = canvas.getContext('2d');

const backgroundCanvas = document.querySelector('#background-canvas');
const bgCtx = backgroundCanvas.getContext('2d');


let rerenderBackground = false, sendResizeResponse = false;
function resizeCanvas(_, rerender=true) {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    backgroundCanvas.width = window.innerWidth;
    backgroundCanvas.height = window.innerHeight;

    if (rerender) {
        rerenderBackground = true;
    }

    if (sendResizeResponse) {
        ipcRenderer.sendSync('send-results', []);

        sendResizeResponse = false;
    }
}

ipcRenderer.on('resize-window', () => sendResizeResponse = true);
window.addEventListener('resize', resizeCanvas, false);

let isLightMode = false;

function toggleBackground() {
    document.body.classList.toggle('light-body');
    isLightMode = !isLightMode;
}

function setBackground(background) {
    document.body.style.background = background;
}

function setLightMode() {
    document.body.classList.add('light-body');
    isLightMode = true;
}

function setDarkMode() {
    document.body.classList.remove('light-body');
    isLightMode = false;
}

function drawRect(args, ctx) {
    const { x, y, cx, cy, fillColor, borderColor } = args;

    ctx.fillStyle = fillColor;
    ctx.strokeStyle = borderColor;

    ctx.fillRect(x, y, cx, cy);
    ctx.strokeRect(x, y, cx, cy);
}

function drawArrowHead(r, theta, origin, ctx) {
    const alpha = 2*Math.PI/3;

    let points = [];

    for (let i = 0; i < 3; i++) {
        points.push([
            r * (Math.cos(theta + i * alpha) - Math.cos(theta)) + origin[0],
            r * (Math.sin(theta + i * alpha) - Math.sin(theta)) + origin[1]
        ]);
    }

    ctx.beginPath();

    let firstPoint = points.pop();
    points.push(firstPoint);

    ctx.moveTo(...firstPoint);

    points.forEach(point => {
        ctx.lineTo(...point);
    });

    ctx.closePath();
    ctx.stroke();
    ctx.fill();
}

function drawLineSet(args, ctx) {
    const { points, color, width, arrows, arrowSize } = args;

    if (points.length < 1) return;

    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = width;

    ctx.beginPath();

    ctx.moveTo(...points[0]);

    points.slice(1).forEach(point => {
        ctx.lineTo(...point);
    });

    ctx.stroke();

    if (points.length === 2 && arrows > 0) {
        const dx = points[1][0] - points[0][0];
        const dy = points[1][1] - points[0][1];
        const theta = Math.atan2(dy, dx);

        if (arrows & 1) {
            drawArrowHead(arrowSize, theta, points[1], ctx);
        }

        if (arrows & 2) {
            drawArrowHead(-arrowSize, theta, points[0], ctx);
        }
    }
}

function drawArc(args, ctx) {
    const { x, y, radius, theta_1, theta_2, fillColor, borderColor } = args;

    ctx.fillStyle = fillColor;
    ctx.strokeStyle = borderColor;

    ctx.beginPath();

    ctx.arc(x, y, radius, theta_1, theta_2, true);

    ctx.fill();
    ctx.stroke();
}

let imagePromises = [];
function drawImage(args, ctx) {
    let { src, x, y, width, height, isTemporary } = args;

    const image = new Image();
    image.src = src;

    imagePromises.push(new Promise(resolve => {
        image.onload = function() {
            if (typeof width === 'undefined') {
                width = this.naturalWidth * height / this.naturalHeight;
            }

            ctx.drawImage(image, x, y, width, height);

            if (isTemporary) {
                spawn('rm', [src]);
            }

            resolve();
        };

        image.onerror = () => {
            resolve();
        };
    }));
}

function drawText(args, ctx) {
    const { text, x, y, fontSpec, color, stroked, markdown } = args;

    ctx.font = fontSpec;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (stroked) {
        ctx.strokeStyle = color;
        ctx.strokeText(text, x, y);
    } else {
        ctx.fillStyle = color;
        ctx.fillText(text, x, y);
    }
}

function drawMarkdown(args, ctx) {
    const { text, x, y, fontSpec, color, stroked } = args;

    ctx.font = fontSpec;
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';

    const italics = /_(.*?)_/g;

    const textParts = text.split(italics);

    let partWidths = [];
    let isItalic = text[0] === '_';
    for (const part of textParts) {
        if (isItalic) {
            ctx.font = 'italic ' + fontSpec;
        } else {
            ctx.font = fontSpec;
        }

        isItalic = !isItalic;

        partWidths.push(ctx.measureText(part).width);
    }

    let currentX = x - partWidths.reduce((a, b) => a + b, 0) / 2;
    isItalic = text[0] === '_';
    for (let i = 0; i < textParts.length; i++) {
        const part = textParts[i];
        const partWidth = partWidths[i];

        if (isItalic) {
            ctx.font = 'italic ' + fontSpec;
        } else {
            ctx.font = fontSpec;
        }

        isItalic = !isItalic;

        if (stroked) {
            ctx.strokeStyle = color;
            ctx.strokeText(part, currentX, y);
        } else {
            ctx.fillStyle = color;
            ctx.fillText(part, currentX, y);
        }

        currentX += partWidth;
    }
}

function downloadCanvas(filePath) {
    const url = canvas.toDataURL('image/png', 0.8);

    const base64Data = url.replace(/^data:image\/png;base64,/, '');

    fs.writeFile(filePath, base64Data, 'base64', () => {});
}

class Properties {
    static get width() {
        return canvas.width;
    }

    static get height() {
        return canvas.height;
    }
}

function draw(args, ctx) {
    if (args.type === 'rect') {
        drawRect(args, ctx);
    } else if (args.type === 'lineset') {
        drawLineSet(args, ctx);
    } else if (args.type === 'arc') {
        drawArc(args, ctx);
    } else if (args.type === 'image') {
        drawImage(args, ctx);
    } else if (args.type === 'text') {
        if (args.markdown) {
            drawMarkdown(args, ctx);
        } else {
            drawText(args, ctx);
        }
    }
}

function clearCanvas(clearBackground) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (clearBackground) {
        bgCtx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

let isPlaying = false, awaitsCompletion = false;

ipcRenderer.on('parse-message', (_, data) => {
    if (data.command === 'draw') {
        draw(data.args, data.args.background ? bgCtx : ctx);
    } else if (data.command === 'clear') {
        clearCanvas(data.args.background);
    } else if (data.command === 'awaitEvent') {
        function temporaryEventListener(e) {
            document.removeEventListener(data.args.type, temporaryEventListener);

            ipcRenderer.sendSync('send-results', data.args.dataKeys.map(k => e[k]));
        }

        document.addEventListener(data.args.type, temporaryEventListener);
    } else if (data.command === 'awaitProperties') {
        ipcRenderer.sendSync(
            'send-results',
            data.args.keys.map(k => Properties[k])
        );
    } else if (data.command === 'downloadCanvas') {
        downloadCanvas(data.args.fileName);
    } else if (data.command === 'renderScene') {
        isPlaying = true;

        const frameCount = data.args.frames.length;
        const frameDuration = data.args.frameDuration * 1000;

        const background = data.args.background;

        for (const shape of background) {
            draw(shape, bgCtx)
        }

        const frames = data.args.frames;

        function renderFrame(i = 0) {
            if (i >= frames.length) return;

            const frame = frames[i];

            clearCanvas(false);

            if (frame.length === 0) renderFrame(i + 1);

            if (rerenderBackground) {
                for (const shape of background) {
                    draw(shape, bgCtx)
                }

                rerenderBackground = false;
            }

            for (const shape of frame) {
                draw(shape, ctx)
            }

            if (isPlaying) {
                setTimeout(renderFrame, frameDuration, i + 1);
            }
        }

        renderFrame();
    } else if (data.command === 'toggleBackground') {
        toggleBackground();
    } else if (data.command === 'setLightMode') {
        setLightMode();
    } else if (data.command === 'setDarkMode') {
        setDarkMode();
    } else if (data.command === 'setBackground') {
        setBackground(data.args.background);
    }
});

document.addEventListener('keydown', e => {
    if (e.ctrlKey) {
        if (e.key === 'c') {
            isPlaying = false;

            if (awaitsCompletion) {
                ipcRenderer.sendSync('send-results', ['completed']);
            }
        } else if (e.key === 'u') {
            clearCanvas(true);
        } else if (e.key === 'b') {
            toggleBackground();
        }
    }
}, false)
