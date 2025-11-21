class HTMLTree {
    constructor(elements) {
        if (elements) {
            this.elements = elements;
        } else {
            this.elements = {};
        }
    }

    add(element) {
        this.elements[element.name] = element;
    }
}


class HTMLElement {
    constructor(element, name) {
        this.element = element;
        document.body.appendChild(this.element);

        this.name = name;
    }

    getCoordinates() {
        return [
            parseInt(this.element.style.left),
            parseInt(this.element.style.top)
        ];
    }

    move(x, y) {
        if (x !== null) {
            this.element.style.left = x + 'px';
        }

        if (y !== null) {
            this.element.style.top = y + 'px';
        }
    }

    resize(width, height) {
        this.element.width = width;
        this.element.height = height;
    }

    hide() {
        this.element.classList.add('hide');
    }

    show() {
        this.element.classList.remove('hide');
    }

    static create(args) {
        if (args.type === 'button') {
            return new Button(args);
        }
    }
}


class Button extends HTMLElement {
    constructor(args) {
        const element = document.createElement('button');

        element.setAttribute('id', args.name);
        element.setAttribute('value', args.label);

        element.setAttribute('width', args.width);
        element.setAttribute('height', args.height);

        element.classList.add(...args.classes);

        super(element, args.name);
    }
}
