function awaitEvent(args) {
    const { type, dataKeys } = args;

    function temporaryEventListener(e) {
        document.removeEventListener(type, temporaryEventListener);

        ipcRenderer.sendSync('send-results', dataKeys.map(k => e[k]));

        Properties.awaitingEvent = false;
    }

    document.addEventListener(type, temporaryEventListener);

    Properties.awaitingEvent = true;
}


function awaitProperties(args) {
    const { keys } = args;

    ipcRenderer.sendSync('send-results', keys.map(k => Properties[k]));
}


ipcRenderer.on('parse-message', (_, data) => {
    const canvasAssociation = {
        'default': [artist, () => {}],
        'background': [backgroundArtist, () => {}],
        'pen': [penArtist, () => currentPen.history.takeSnapshot()]
    };

    const functionAssociation = {
        draw: args => {
            args['callback'] = canvasAssociation[args.canvas][1];
            canvasAssociation[args.canvas][0].draw(args);
        },
        drawGroup: args => {
            args['callback'] = canvasAssociation[args.canvas][1];
            for (const shape of args.shapes) {
                canvasAssociation[args.canvas][0].draw(shape);
            }
        },
        clear: args => clearCanvas(args.background),
        clearLatex: args => backgroundArtist.clearLatex() || artist.clearLatex(),
        awaitEvent: awaitEvent,
        awaitProperties: awaitProperties,
        renderScene: args => { sequence = Sequence.runFromArgs(artist, backgroundArtist, args) },
        toggleBackground: toggleBackground,
        setLightMode: setLightMode,
        setDarkMode: setDarkMode,
        setBackground: args => setBackground(args.background)
    };

    functionAssociation[data.command](data.args);
});
