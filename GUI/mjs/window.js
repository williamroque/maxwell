const { BrowserWindow } = require('electron');

const url = require('url');
const path = require('path');

class Window {
    constructor(properties, file, dispatchOnReady) {
        this.properties = properties;
        this.file = file;

        this.properties.webPreferences = {
            nodeIntegration: true,
            'page-visibility': true,
            backgroundThrottling: false
        };

        this.dispatchOnReady = dispatchOnReady;

        this.window = null;
    }

    createWindow() {
        this.window = new BrowserWindow(this.properties);
        this.window.loadURL(url.format({
            pathname: path.join(__dirname, `../html/${this.file}`),
            protocol: 'file:',
            slashes: true
        }));

        if (this.windowState) {
            this.windowState.manage(this.window);
        }

        this.addListener('closed', e => this.window = null);

        this.addWebListener('dom-ready', () => {
            if (typeof this.dispatchOnReady !== 'undefined') {
                this.dispatchWebEvent(...this.dispatchOnReady);
            }
        });
    }

    show() {
        this.window.show();
    }

    isNull() {
        return this.window === null;
    }

    addListener(event, callback) {
        this.window.on(event, callback);
    }

    addWebListener(event, callback) {
        this.window.webContents.once(event, callback);
    }

    dispatchWebEvent(event, message) {
        this.window.webContents.send(event, message);
    }

    toggleDevTools() {
        this.window.webContents.toggleDevTools();
    }
}

module.exports = Window;
