const { ipcRenderer } = require('electron');
const fs = require('fs');
const { spawn } = require('child_process');

const canvas = document.querySelector('#python-canvas');
const ctx = canvas.getContext('2d');


window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}, false);


function drawRect(args) {
    const { x, y, cx, cy, fillColor, borderColor } = args;

    ctx.fillStyle = fillColor;
    ctx.strokeStyle = borderColor;

    ctx.fillRect(x, y, cx, cy);
    ctx.strokeRect(x, y, cx, cy);
}

function drawArrowHead(r, theta, origin) {
    const alpha = 2*Math.PI/3;

    let points = [];

    for (let i = 0; i < 3; i++) {
        points.push([
            r * Math.cos(theta + i * alpha) + origin[0],
            r * Math.sin(theta + i * alpha) + origin[1]
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

function drawLineSet(args) {
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
            drawArrowHead(arrowSize, theta, points[1]);
        }

        if (arrows & 2) {
            drawArrowHead(-arrowSize, theta, points[0]);
        }
    }
}

function drawArc(args) {
    const { x, y, radius, theta_1, theta_2, fillColor, borderColor } = args;

    ctx.fillStyle = fillColor;
    ctx.strokeStyle = borderColor;

    ctx.beginPath();

    ctx.arc(x, y, radius, theta_1, theta_2, true);

    ctx.fill();
    ctx.stroke();
}

function drawImage(args) {
    const { src, x, y, width, height, isTemporary } = args;

    const image = new Image();
    image.src = src;

    image.onload = () => {
        ctx.drawImage(image, x, y, width, height);

        if (isTemporary) {
            spawn('rm', [src]);
        }
    };
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

function draw(args) {
    if (args.type === 'rect') {
        drawRect(args);
    } else if (args.type === 'lineset') {
        drawLineSet(args);
    } else if (args.type === 'arc') {
        drawArc(args);
    } else if (args.type === 'image') {
        drawImage(args);
    } 
}

function clearCanvas(opacity) {
    ctx.fillStyle = `#171414${((opacity * 255) | 0).toString(16)}`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

let isPlaying = false;

ipcRenderer.on('parse-message', (_, data) => {
    if (data.command === 'draw') {
        draw(data.args);
    } else if (data.command === 'clear') {
        clearCanvas(data.args.opacity);
    } else if (data.command === 'awaitEvent') {
        function temporaryEventListener(e) {
            canvas.removeEventListener(data.args.type, temporaryEventListener);

            ipcRenderer.sendSync('send-results', data.args.dataKeys.map(k => e[k]));
        }

        canvas.addEventListener(data.args.type, temporaryEventListener);
    } else if (data.command === 'awaitProperties') {
        ipcRenderer.sendSync(
            'send-results',
            data.args.keys.map(k => Properties[k])
        );
    } else if (data.command === 'downloadCanvas') {
        downloadCanvas(data.args.fileName);
    } else if (data.command === 'renderScene') {
        isPlaying = true;

        function renderFrame(frames) {
            if (frames.length < 1) return;

            const frame = JSON.parse(frames.shift());

            clearCanvas(1);
            Object.values(frame).forEach(shape => {
                draw(shape);
            });

            if (isPlaying) {
                setTimeout(renderFrame, data.args.frameDuration * 1000, frames);
            }
        }
        renderFrame(data.args.frames);
    }
});

document.addEventListener('keydown', e => {
    if (e.key === 'c' && e.ctrlKey) {
        isPlaying = false;
    }
}, false)
