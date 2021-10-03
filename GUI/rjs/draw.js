class Artist {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');

        this.DOMElements = [];
    }


    clear(x=0, y=0, width=this.canvas.width, height=this.canvas.height) {
        for (const element of this.DOMElements) {
            element.remove();
        }

        this.DOMElements = [];

        this.ctx.clearRect(x, y, width, height);
    }


    capture(canvas, sourceX, sourceY, targetX=0, targetY=0) {
        const width = Math.min(canvas.width, this.canvas.width);
        const height = Math.min(canvas.height, this.canvas.height);

        this.ctx.drawImage(
            canvas,
            sourceX, sourceY,
            width,
            height,
            targetX, targetY,
            width,
            height
        );
    }


    draw(shape) {
        const methodAssociation = {
            rect: this.drawRect,
            curve: this.drawCurve,
            arc: this.drawArc,
            image: this.drawImage,
            text: (shape) => shape.markdown ? this.drawMarkdown(shape) : this.drawText(shape),
            latex: this.drawLatex
        };

        methodAssociation[shape.type].call(this, shape);
    }


    drawRect(args) {
        const { point, width, height, fillColor, borderColor } = args;
        let [ x, y ] = point;

        x -= width / 2;
        y -= height / 2;

        this.ctx.fillStyle = fillColor;
        this.ctx.strokeStyle = borderColor;

        this.ctx.fillRect(x, y, width, height);
        this.ctx.strokeRect(x, y, width, height);
    }


    drawArrowHead(points) {
        this.ctx.beginPath();

        let firstPoint = points.pop();
        points.push(firstPoint);

        this.ctx.moveTo(...firstPoint);

        points.forEach(point => {
            this.ctx.lineTo(...point);
        });

        this.ctx.closePath();
        this.ctx.stroke();
        this.ctx.fill();
    }


    drawCurve(args) {
        const { points, color, width, arrowHead, fill } = args;

        if (points.length < 1) return;

        this.ctx.strokeStyle = color;
        this.ctx.fillStyle = color;
        this.ctx.lineWidth = width;

        this.ctx.beginPath();

        this.ctx.moveTo(...points[0]);

        points.slice(1).forEach(point => {
            this.ctx.lineTo(...point);
        });

        this.ctx.stroke();

        if (fill) {
            this.ctx.fill();
        }

        if (arrowHead.length > 0) {
            this.drawArrowHead(arrowHead);
        }
    }


    drawArc(args) {
        const { point, radius, theta_1, theta_2, fillColor, borderColor, borderWidth } = args;

        this.ctx.fillStyle = fillColor;
        this.ctx.strokeStyle = borderColor;
        this.ctx.lineWidth = borderWidth;

        this.ctx.beginPath();

        this.ctx.arc(...point, radius, theta_1, theta_2, true);

        this.ctx.fill();
        this.ctx.stroke();
    }


    drawImage(args) {
        let { src, point, width, height, isTemporary } = args;
        const [x, y] = point;

        const image = new Image();
        image.src = src;

        image.onload = () => {
            if (height === 0) {
                height = image.naturalHeight;
            }

            if (width === 0) {
                width = image.naturalWidth * height / image.naturalHeight;
            }

            this.ctx.drawImage(image, x, y, width, height);

            if (isTemporary) {
                spawn('rm', [src]);
            }
        };
    }


    drawText(args) {
        const { text, x, y, fontSpec, color, stroked, markdown } = args;

        this.ctx.font = fontSpec;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        if (stroked) {
            this.ctx.strokeStyle = color;
            this.ctx.strokeText(text, x, y);
        } else {
            this.ctx.fillStyle = color;
            this.ctx.fillText(text, x, y);
        }
    }


    drawMarkdown(args) {
        const { text, x, y, fontSpec, color, stroked } = args;

        this.ctx.font = fontSpec;
        this.ctx.textBaseline = 'middle';
        this.ctx.textAlign = 'left';

        const italics = /_(.*?)_/g;

        let textParts = text.split(italics);

        let partWidths = [];
        let isItalic = text[0] === '_';

        if (isItalic) {
            textParts.shift();
        }

        for (const part of textParts) {
            if (isItalic) {
                this.ctx.font = 'italic ' + fontSpec;
            } else {
                this.ctx.font = fontSpec;
            }

            isItalic = !isItalic;

            partWidths.push(this.ctx.measureText(part).width);
        }

        let currentX = x - partWidths.reduce((a, b) => a + b, 0) / 2;
        isItalic = text[0] === '_';
        for (let i = 0; i < textParts.length; i++) {
            const part = textParts[i];
            const partWidth = partWidths[i];

            if (isItalic) {
                this.ctx.font = 'italic ' + fontSpec;
            } else {
                this.ctx.font = fontSpec;
            }

            isItalic = !isItalic;

            if (stroked) {
                this.ctx.strokeStyle = color;
                this.ctx.strokeText(part, currentX, y);
            } else {
                this.ctx.fillStyle = color;
                this.ctx.fillText(part, currentX, y);
            }

            currentX += partWidth;
        }
    }

    drawLatex(args) {
        const { source, point, fontSize, color, align } = args;

        const latexContainer = document.createElement('div');
        latexContainer.style.left = point[0] + 'px';
        latexContainer.style.top = point[1] + 'px';
        latexContainer.style.fontSize = fontSize + 'pt';
        latexContainer.style.color = color;
        latexContainer.classList.add('latex-container');

        if (align === 'center') {
            latexContainer.classList.add('latex-align-center');
        } else if (align === 'right') {
            latexContainer.classList.add('latex-align-right');
        }

        document.body.appendChild(latexContainer);

        this.DOMElements.push(latexContainer);

        katex.render(source, latexContainer, {
            throwOnError: false,
            displayMode: true
        });
    }
}
