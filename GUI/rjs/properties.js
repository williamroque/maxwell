class Properties {
    static sendResizeResponse = false;
    static rerenderBackground = false;
    static isLightMode = false;
    static awaitingEvent = false;
    static isZoom = false;

    static capture;

    static get width() {
        return canvas.width;
    }

    static get height() {
        return canvas.height;
    }
}
