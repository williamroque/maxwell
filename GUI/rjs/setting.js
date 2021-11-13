function zoom(factor, relative=true) {
    Properties.isZoom = true;

    if (relative) {
        factor = factor + webFrame.getZoomFactor();
    }

    currentPen.brush.drawPreview();

    webFrame.setZoomFactor(Math.max(1, factor));
}


function compensateViewport(length) {
    return length/window.innerWidth*defaultWidth;
}


function resizeCanvas(_, rerender=true) {
    if (Properties.isZoom) {
        Properties.isZoom = false;
        return;
    }

    penPreviewCanvas.style.right = compensateViewport(5) + 'vw';
    penPreviewCanvas.style.bottom = compensateViewport(5) + 'vw';

    penPreviewCanvas.style.width = compensateViewport(10) + 'vw';
    penPreviewCanvas.style.height = compensateViewport(10) + 'vw';

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    backgroundCanvas.width = window.innerWidth;
    backgroundCanvas.height = window.innerHeight;

    penCanvas.width = window.innerWidth;
    penCanvas.height = window.innerHeight;

    currentPen.history.travel(0);

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
