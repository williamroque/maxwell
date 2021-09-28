ipcRenderer.on('resize-window', () => Properties.sendResizeResponse = true);
window.addEventListener('resize', resizeCanvas, false);


function areEqual(setA, setB) {
    if (setA.size !== setB.size)
        return false;

    return [...setA].every(element => setB.has(element));
}


document.addEventListener('keydown', e => {
    const potentialModifiers = ['Control', 'Shift'];
    const activeModifiers = new Set(potentialModifiers.filter(e.getModifierState.bind(e)));

    for (const binding in keymap) {
        const components = binding.split('+');

        const modifiers = new Set(components.slice(0, components.length - 1));
        const key = components[components.length - 1];

        if (e.key.toLowerCase() === key && areEqual(modifiers, activeModifiers)) {
            keymap[binding]();
            break;
        }
    }
}, false)
