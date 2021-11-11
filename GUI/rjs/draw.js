class Artist {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');

        this.DOMElements = [];
    }


    clearLatex() {
        for (const element of this.DOMElements) {
            element.remove();
        }

        this.DOMElements = [];
    }


    clear(x=0, y=0, width=this.canvas.width, height=this.canvas.height) {
        this.clearLatex();
        this.ctx.clearRect(x, y, width, height);
    }


    capture(canvas, sourceX=0, sourceY=0, targetX=0, targetY=0) {
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
            latex: this.drawLatex,
            svg: this.drawSVG,
            table: this.drawTable
        };

        methodAssociation[shape.type].call(this, shape);
    }


    drawRect(args) {
        const { point, width, height, fillColor, borderColor, borderWidth } = args;
        let [ x, y ] = point;

        x -= width / 2;
        y -= height / 2;

        this.ctx.fillStyle = fillColor;
        this.ctx.strokeStyle = borderColor;
        this.ctx.lineWidth = borderWidth;

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
        const { points, color, width, arrowHead, fillColor } = args;

        if (points.length < 1) return;

        this.ctx.strokeStyle = color;
        this.ctx.fillStyle = fillColor;
        this.ctx.lineWidth = width;

        this.ctx.beginPath();

        this.ctx.moveTo(...points[0]);

        let discontinuity = false;

        points.slice(1).forEach(point => {
            if (point[0] === 'Infinity' || point[1] === 'Infinity') {
                if (!discontinuity) {
                    this.ctx.stroke();
                }
                discontinuity = true;
            } else {
                if (discontinuity) {
                    this.ctx.moveTo(...point);
                    discontinuity = false;
                }

                this.ctx.lineTo(...point);
            }
        });

        this.ctx.stroke();

        if (fillColor !== 'transparent') {
            this.ctx.fill();
        }

        if (arrowHead.length > 0) {
            this.ctx.fillStyle = color;
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

        if (borderWidth > 0) {
            this.ctx.stroke();
        }
    }


    drawImage(args) {
        let { src, point, width, height, isTemporary, callback } = args;
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

            callback();
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

    drawLatex(args, latexContainer) {
        const { source, point, fontSize, color, align } = args;

        if (point[0] >= this.canvas.width || point[1] >= this.canvas.height) return;

        if (latexContainer === undefined) {
            latexContainer = document.createElement('div');
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

            this.DOMElements.push(latexContainer);
            document.body.appendChild(latexContainer);
        }

        katex.render(source, latexContainer, {
            throwOnError: false,
            displayMode: true
        });
    }

    drawSVG(args) {
        const { data, point, transform, fillColor } = args;
        const [x, y] = point;

        this.ctx.fillStyle = fillColor;

        this.ctx.setTransform(
            transform[0],
            0, 0,
            transform[1],
            transform[2] + x,
            transform[3] + y
        )

        const path = new Path2D(data);

        this.ctx.fill(path);

        this.ctx.setTransform();
    }

    drawTable(args) {
        const { data, headers, point, color } = args;

        const tableElement = document.createElement('table');

        tableElement.style.color = color;

        const headerRowElement = document.createElement('tr');
        for (const header of headers) {
            const headerElement = document.createElement('th');

            this.drawLatex({
                source: header,
                point: [0, 0],
                fontSize: undefined,
                color: undefined,
                align: undefined
            }, headerElement);

            headerRowElement.appendChild(headerElement);
        }

        tableElement.appendChild(headerRowElement);

        for (const row of data) {
            const rowElement = document.createElement('tr');

            for (const col of row) {
                const columnElement = document.createElement('td');

                this.drawLatex({
                    source: col,
                    point: [0, 0],
                    fontSize: undefined,
                    color: undefined,
                    align: undefined
                }, columnElement);

                if (!isNaN(col)) {
                    columnElement.style.textAlign = 'right';
                }

                rowElement.appendChild(columnElement);
            }

            tableElement.appendChild(rowElement);
        }

        this.DOMElements.push(tableElement);


        document.body.appendChild(tableElement);

        tableElement.style.left = point[0] - tableElement.offsetWidth / 2 + 'px';
        tableElement.style.top = point[1] - tableElement.offsetHeight / 2 + 'px';
    }
}
