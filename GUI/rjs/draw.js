class Artist {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');

        this.ctx.imageSmoothingEnabled = false;

        this.DOMElements = [];
    }

    getCoordinates() {
        return [
            parseInt(this.canvas.style.left),
            parseInt(this.canvas.style.top)
        ];
    }

    moveCanvas(x, y) {
        if (x !== null) {
            this.canvas.style.left = x + 'px';
        }

        if (y !== null) {
            this.canvas.style.top = y + 'px';
        }
    }

    resizeCanvas(width, height) {
        this.canvas.width = width;
        this.canvas.height = height;

        this.ctx.imageSmoothingEnabled = false;
    }

    rotateCanvas(theta, about) {
        if (about) {
            this.canvas.style.transformOrigin = `${about[0]}px ${about[1]}px`;
        } else {
            this.canvas.style.transformOrigin = null;
        }

        this.canvas.style.transform = 'rotate(' + -theta + 'rad)';
    }

    rotate(theta, about) {
        if (!about) {
            about = [this.canvas.width/2, this.canvas.height/2];
        }

        this.ctx.setTransform(1, 0, 0, 1, 0, 0);

        this.ctx.translate(...about);
        this.ctx.rotate(-theta);
        this.ctx.translate(-about[0], -about[1]);
    }

    rotateRedraw(theta) {
        const bufferCanvas = this.canvas.cloneNode();
        const bufferCtx = bufferCanvas.getContext('2d');

        const width = this.canvas.width;
        const height = this.canvas.height;

        bufferCtx.drawImage(
            this.canvas,
            0, 0, width, height,
            0, 0, width, height
        )

        const size = Math.sqrt(width**2 + height**2);
        const coords = this.getCoordinates();

        this.resizeCanvas(size, size);

        this.moveCanvas(
            coords[0] + width/2 - size/2,
            coords[1] + height/2 - size/2
        );

        this.clear();
        this.rotate(theta);
        this.capture(
            bufferCanvas,
            0, 0,
            size/2 - width/2,
            size/2 - height/2
        );
        this.rotate(0);
    }

    hideCanvas() {
        this.canvas.classList.add('hide');
    }

    showCanvas() {
        this.canvas.classList.remove('hide');
    }

    clearDOMElements() {
        for (const element of this.DOMElements) {
            element.remove();
        }

        this.DOMElements = [];
    }

    clear(x=0, y=0, width=this.canvas.width, height=this.canvas.height) {
        this.clearDOMElements();
        this.ctx.clearRect(x, y, width, height);
    }

    capture(canvas, sourceX=0, sourceY=0, targetX=0, targetY=0) {
        const { width, height } = canvas;

        this.ctx.drawImage(
            canvas,
            sourceX, sourceY, width, height,
            targetX, targetY, width, height
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

    calculateArrowHead(r, start, end, origin) {
        const theta = Math.atan2(
            end[1] - start[1],
            end[0] - start[0]
        );

        const alpha = 2*Math.PI/3;

        let points = [];

        for (let i = 0; i < 3; i++) {
            points.push([
                r * (Math.cos(theta + i * alpha) - Math.cos(theta)) + origin[0],
                r * (Math.sin(theta + i * alpha) - Math.sin(theta)) + origin[1]
            ]);
        }

        return points;
    }

    drawArrowHead(points) {
        const dashes = this.ctx.getLineDash();
        this.ctx.setLineDash([]);

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

        this.ctx.setLineDash(dashes);
    }

    drawCurve(args) {
        const { points, smooth, color, width, arrowHead, fillColor } = args;

        if (points.length < 1) return;

        if (smooth) {
            this.ctx.lineCap = 'round';
            this.ctx.lineJoin = 'round';
        } else {
            this.ctx.lineCap = 'butt';
            this.ctx.lineJoin = 'butt';
        }

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

    drawBezier(args) {
        const { points, color, width } = args;

        if (points.length !== 4) return;

        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = width;

        this.ctx.beginPath();
        this.ctx.moveTo(...points[0]);
        this.ctx.bezierCurveTo(...points[1], ...points[2], ...points[3]);
        this.ctx.stroke();
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

    drawLatex(args, latexContainer, callback) {
        let { source, point, fontSize, color, align, embed } = args;

        if (latexContainer === undefined) {
            latexContainer = document.createElement('div');
            latexContainer.style.fontSize = fontSize + 'pt';
            latexContainer.style.color = color;
            latexContainer.classList.add('latex-container');

            if (embed) {
                latexContainer.style.top = '-1000px';
                latexContainer.style.left = '-1000px';
            } else {
                latexContainer.style.top = point[1] + 'px';
                latexContainer.style.left = point[0] + 'px';
                this.DOMElements.push(latexContainer);
            }

            document.body.appendChild(latexContainer);

            if (align === 'center') {
                latexContainer.classList.add('latex-align-center');
            } else if (align === 'right') {
                latexContainer.classList.add('latex-align-right');
            }
        }

        katex.render(source, latexContainer, {
            throwOnError: false,
            displayMode: true
        });

        if (embed) {
            const margin = 1.2;

            const width = latexContainer.offsetWidth * margin;
            const height = latexContainer.offsetHeight;

            html2canvas(
                latexContainer,
                {backgroundColor: null}
            ).then(canvas => {
                if (point === undefined) {
                    point = [0, 0];
                }

                this.resizeCanvas(width, height);
                this.capture(canvas, 0, 0, ...point);

                if (callback !== undefined) {
                    callback();
                }
            });

            latexContainer.remove();
        }
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
                align: undefined,
                embed: false
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
                    align: undefined,
                    embed: false
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
