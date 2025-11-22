const { app, ipcMain, dialog } = require('electron');

const util = require('util')
const exec = util.promisify(require('child_process').exec);

const net = require('net');

const path = require('path');
const os = require('os');

const fs = require('fs');

const Window = require('./window');

const fixPath = require('fix-path');
fixPath();

const openToNetwork = false;

let mainWindow;

app.on('ready', () => {
    mainWindow = new Window({
        icon: '../assets/icon.png',
        frame: false,
        width: 600,
        height: 500,
        minWidth: 300,
        minHeight: 300,
        resizable: true,
        fullscreen: false,
        fullscreenable: true,
        backgroundColor: '#171414'
    }, 'index.html');
    
    mainWindow.createWindow();
});

app.on('window-all-closed', () => {
    app.exit(0);
});

const server = net.createServer();

server.on('connection', socket => {
    ipcMain.on('send-results', (event, data) => {
        socket.write(JSON.stringify(data));

        event.returnValue = '';
    });

    let accumulated = '';

    socket.on('data', data => {
        data = data.toString().split('\n');

        let last = data.pop();
        if (last !== '') {
            accumulated += last;
        } else if (accumulated) {
            data[0] = accumulated + data[0];
            accumulated = '';
        }

        data.forEach(message => {
            try {
                message = message.replaceAll('-Infinity', 'Infinity');
                message = message.replaceAll('Infinity', '"Infinity"');

                let parsedMessage = JSON.parse(message);

                if (parsedMessage.command === 'resizeWindow') {
                    const { width, height } = parsedMessage.args;

                    const currentBounds = mainWindow.window.getBounds();
                    if (currentBounds.width === width && currentBounds.height === height) {
                        socket.write('[]');
                    } else {
                        mainWindow.dispatchWebEvent('resize-window');

                        mainWindow.window.setBounds({
                            width: width,
                            height: height
                        });
                    }
                } else {
                    mainWindow.dispatchWebEvent('parse-message', parsedMessage);
                }
            } catch(e) {
                console.log(e, message);
            }
        });
    });

    socket.on('close', () => {
        ipcMain.removeAllListeners('send-results');
    });

    socket.on('error', err => {
        console.log(err.stack);
    });
});

try {
    let ipAddress = '127.0.0.1';
    if (openToNetwork) {
        ipAddress =  '0.0.0.0';
    }

    server.listen(1337, ipAddress);
} catch(e) {
    console.log(e, message);
}


function waitForFile(filePath) {
    return new Promise(resolve => {
        while (!fs.existsSync(filePath));
        resolve(fs.readFileSync(filePath).toString());
        fs.unlinkSync(filePath);
    });
}


ipcMain.handle('get-latex-prompt', async event => {
    try {
        await exec('/usr/local/bin/emacsclient -e "(maxwell-get-latex-prompt)"');

        const filePath = path.join(os.homedir(), 'temp.org');

        return waitForFile(filePath);
    } catch {
        return new Promise(resolve => resolve(''));
    }
});


ipcMain.on('save-svg', (event, svgContent) => {
    const filePath = dialog.showSaveDialogSync(mainWindow.window, {
        title: 'Save SVG',
        defaultPath: path.join(os.homedir(), 'drawing.svg'),
        filters: [
            { name: 'SVG Files', extensions: ['svg'] },
        ]
    });

    if (!filePath) {
        return;
    }

    fs.writeFile(filePath, svgContent, err => {
        if (err) {
            console.error(err);
        }
    });

    event.returnValue = '';
});