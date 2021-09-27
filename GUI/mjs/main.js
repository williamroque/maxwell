const { app, ipcMain } = require('electron');
const net = require('net');

const Window = require('./window');

const fixPath = require('fix-path');
fixPath();

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
        backgroundColor: '#171414',
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

        console.log(data);

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
    server.listen(1337, '127.0.0.1');
} catch(e) {
    console.log(e, message);
}
