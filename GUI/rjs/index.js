const pen = new Pen(penArtist, penPreviewArtist, selectionArtist);


function awaitEvent(args) {
    const { type, dataKeys } = args;

    function temporaryEventListener(e) {
        document.removeEventListener(type, temporaryEventListener);

        ipcRenderer.sendSync('send-results', dataKeys.map(k => e[k]));

        awaitingEvent = false;
    }

    document.addEventListener(type, temporaryEventListener);

    awaitingEvent = true;
}


function awaitProperties(args) {
    const { keys } = args;

    ipcRenderer.sendSync('send-results', keys.map(k => Properties[k]));
}


ipcRenderer.on('parse-message', (_, data) => {
    const functionAssociation = {
        draw: args => (args.background ? backgroundArtist : artist).draw(args),
        clear: args => clearCanvas(args.background),
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
