ipcRenderer.on('resize-window', () => Properties.sendResizeResponse = true);
window.addEventListener('resize', resizeCanvas, false);


function areEqual(setA, setB) {
    if (setA.size !== setB.size)
        return false;

    return [...setA].every(element => setB.has(element));
}


document.addEventListener('keydown', e => {
    const potentialModifiers = ['Control', 'Shift', 'Meta'];
    const activeModifiers = new Set(potentialModifiers.filter(e.getModifierState.bind(e)));

    for (const bindingGroup in keymap) {
        const bindings = bindingGroup.split(' ');

        for (const binding of bindings) {
            const components = binding.split('+');

            const modifiers = new Set(components.slice(0, components.length - 1));
            const key = components[components.length - 1];

            if (e.key.toLowerCase() === key.toLowerCase() && areEqual(modifiers, activeModifiers)) {
                keymap[bindingGroup]();
                break;
            }
        }
    }
}, false)


// Temporary events for while Wacom doesn't support Monterey


document.addEventListener('auxclick', e => {
    if (e.which === 2) {
        pen.activateSelection();
    } else if (e.which === 3) {
        if (pen.enabled) {
            pen.deleteSelection();
        }
    } else if (e.which === 4) {
        if (pen.enabled && !pen.movingSelection && !pen.selectionStart) {
            pen.drawingLine = true;
        }
    }
});
