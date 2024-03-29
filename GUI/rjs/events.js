ipcRenderer.on('resize-window', () => Properties.sendResizeResponse = true);
window.addEventListener('resize', resizeCanvas, false);


function areEqual(setA, setB) {
    if (setA.size !== setB.size)
        return false;

    return [...setA].every(element => setB.has(element));
}


function shiftOrEmpty(modifiers) {
    return modifiers.size === 0 || areEqual(new Set(['Shift']), modifiers);
}


let currentOperator;
const operatorLabels = { ' ': 'Space' }

document.addEventListener('keydown', e => {
    const potentialModifiers = ['Control', 'Shift', 'Meta'];
    const activeModifiers = new Set(potentialModifiers.filter(e.getModifierState.bind(e)));

    if (currentOperator !== undefined) {
        if (!potentialModifiers.includes(e.key)) {
            currentOperator(e.key);
            currentOperator = undefined;
            keyPrompt.innerText = '';
        }
        return;
    }

    for (const bindingGroup in keymap) {
        if (bindingGroup[0] === '~') {
            if (shiftOrEmpty(activeModifiers) && e.key === bindingGroup[1]) {
                const isOperator = keymap[bindingGroup][0]();

                if (isOperator) {
                    const operatorKey = bindingGroup[1];

                    currentOperator = keymap[bindingGroup][1];

                    if (operatorKey in operatorLabels) {
                        keyPrompt.innerText = operatorLabels[operatorKey];
                    } else {
                        keyPrompt.innerText = operatorKey;
                    }
                }
            }
        } else {
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
    }
}, false)


// Temporary events until Wacom supports Monterey


document.addEventListener('auxclick', e => {
    if (e.which === 2) {
        currentPen.activateSelection();
    } else if (e.which === 3) {
        if (currentPen.enabled) {
            currentPen.deleteSelection();
        }
    } else if (e.which === 4) {
        if (currentPen.enabled && !currentPen.movingSelection && !currentPen.selectionStart) {
            currentPen.drawingLine = true;
        }
    }
});
