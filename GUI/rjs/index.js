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

function drawLineSet(args) {
    const { points, color, width } = args;

    if (points.length < 1) return;

    ctx.strokeStyle = color;
    ctx.lineWidth = width;

    ctx.beginPath();

    ctx.moveTo(...points.shift());

    points.forEach(point => {
        ctx.lineTo(...point);
    });

    ctx.stroke();
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

ipcRenderer.on('parse-message', (_, data) => {
    if (data.command === 'draw') {
        if (data.args.type === 'rect') {
            drawRect(data.args);
        } else if (data.args.type === 'lineset') {
            drawLineSet(data.args);
        } else if (data.args.type === 'arc') {
            drawArc(data.args);
        } else if (data.args.type === 'image') {
            drawImage(data.args);
        } 
    } else if (data.command === 'clear') {
        ctx.fillStyle = `#171414${((data.args.opacity * 255) | 0).toString(16)}`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
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
    }
});
