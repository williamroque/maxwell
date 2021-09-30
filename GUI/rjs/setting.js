function zoom(factor, relative=true) {
    isZoom = true;

    if (relative) {
        factor = factor + webFrame.getZoomFactor();
    }

    webFrame.setZoomFactor(Math.max(1, factor));
}


function resizeCanvas(_, rerender=true) {
    if (isZoom) {
        isZoom = false;
        return;
    }

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    backgroundCanvas.width = window.innerWidth;
    backgroundCanvas.height = window.innerHeight;

    penCanvas.width = window.innerWidth;
    penCanvas.height = window.innerHeight;

    pen.history.travel(0);

    if (rerender && sequence && sequence.isPlaying) {
        Properties.rerenderBackground = true;
    }

    if (Properties.sendResizeResponse) {
        ipcRenderer.sendSync('send-results', []);

        Properties.sendResizeResponse = false;
    }
}


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
