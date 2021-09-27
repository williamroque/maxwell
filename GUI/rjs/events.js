ipcRenderer.on('resize-window', () => Properties.sendResizeResponse = true);
window.addEventListener('resize', resizeCanvas, false);

document.addEventListener('keydown', e => {
    const modifierKey = {
        'ctrl': e.ctrlKey
    };

    for (const binding in keymap) {
        const components = binding.split('+');

        const modifiers = components.slice(0, components.length - 1);
        const key = components[components.length - 1];

        if (e.key === key && modifiers.every(mod => modifierKey[mod])) {
            keymap[binding]();
            break;
        }
    }
}, false)
