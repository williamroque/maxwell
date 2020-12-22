const { ipcRenderer } = require('electron');

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


ipcRenderer.on('parse-message', (_, data) => {
    if (data.command === 'draw') {
        if (data.args.type === 'rect') {
            drawRect(data.args);
        }
    } else if (data.command === 'clear') {
        if (data.args.weak) {
            ctx.fillStyle = '#17141433';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }
});
