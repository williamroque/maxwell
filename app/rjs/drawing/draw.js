const C2S = require('canvas-to-svg');

class Artist {
    constructor(canvas) {
        this.canvas = canvas;

        // real canvas context
        this._realCtx = this.canvas.getContext('2d');

        // virtual SVG context for canvas-to-svg
        this._svgCtx = new C2S(this.canvas.width || 800, this.canvas.height || 600);

        // unified context used throughout the file
        this.ctx = createDualContext(this._realCtx, this._svgCtx);

        this.DOMElements = [];
        // Store raw SVG fragments (strings) for shapes that can't be produced
        // by the canvas-to-svg recorder directly (e.g. KaTeX output).
        this._svgFragments = [];
        // MathJax integration (lazy init)
        this._mathjaxInited = false;
        this._mathjax = null;
        // ensure a shared global fragment store so exported SVG includes fragments from any artist
        try {
            if (typeof window !== 'undefined') {
                window.__maxwell_svg_fragments = window.__maxwell_svg_fragments || [];
            }
        } catch (e) {}

        this._realCtx.imageSmoothingEnabled = false;
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
            about = [this.canvas.width / 2, this.canvas.height / 2];
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

        const size = Math.sqrt(width ** 2 + height ** 2);
        const coords = this.getCoordinates();

        this.resizeCanvas(size, size);

        this.moveCanvas(
            coords[0] + width / 2 - size / 2,
            coords[1] + height / 2 - size / 2
        );

        this.clear();
        this.rotate(theta);
        this.capture(
            bufferCanvas,
            0, 0,
            size / 2 - width / 2,
            size / 2 - height / 2
        );
        this.rotate(0);
    }

    hideCanvas() {
        this.canvas.classList.add('hide');
    }

    showCanvas() {
        this.canvas.classList.remove('hide');
    }

    moveCanvas(x, y) {
        try {
            if (this.canvas && this.canvas.style) {
                this.canvas.style.left = (x || 0) + 'px';
                this.canvas.style.top = (y || 0) + 'px';
            }
        } catch (e) {
            console.warn('[moveCanvas] failed to move canvas:', e);
        }
        // Also move overlays so previews track the canvas
        try { this.moveCanvasOverlay(x, y); } catch (e) {}
        // Move the global SVG overlay (committed vector elements) as well
        try {
            if (typeof window !== 'undefined' && window.__maxwell_svg_overlay) {
                const overlay = window.__maxwell_svg_overlay;
                overlay.style.left = (x || 0) + 'px';
                overlay.style.top = (y || 0) + 'px';
            }
        } catch (e) {}
    }

    // Also move any overlay DOM elements (SVG previews) so they track the canvas
    // position used by the pen tool.
    moveCanvasOverlay(x, y) {
        try {
            for (const el of this.DOMElements) {
                try {
                    if (el && el.dataset && el.dataset.preview === 'latex') {
                        el.style.left = (x || 0) + 'px';
                        el.style.top = (y || 0) + 'px';
                    }
                } catch (e) {}
            }
        } catch (e) {
            // ignore
        }
    }

    getCoordinates() {
        try {
            if (this.canvas && typeof this.canvas.getBoundingClientRect === 'function') {
                const r = this.canvas.getBoundingClientRect();
                return [r.left, r.top];
            }
            if (this.canvas && this.canvas.style) {
                return [parseFloat(this.canvas.style.left) || 0, parseFloat(this.canvas.style.top) || 0];
            }
        } catch (e) {
            console.warn('[getCoordinates] failed to get canvas position:', e);
        }
        return [0, 0];
    }

    async _ensureMathJax() {
        if (this._mathjaxInited) return;
        this._mathjaxInited = true;

        // Prefer an existing global MathJax if present (e.g., loaded via script tag)
        try {
            if (typeof window !== 'undefined' && window.MathJax) {
                // Create a small adapter around the global MathJax
                this._mathjax = {
                    adaptor: window.MathJax.adaptor || null,
                    doc: window.MathJax.startup && window.MathJax.startup.getDocument ? window.MathJax.startup.getDocument() : null
                };
                return;
            }
        } catch (e) {
            // fall through to require()
        }

        // Try to require mathjax-full in the renderer environment
        try {
            const mj = require('mathjax-full/js/mathjax').mathjax;
            const TeX = require('mathjax-full/js/input/tex').TeX;
            const SVG = require('mathjax-full/js/output/svg').SVG;
            const liteAdaptor = require('mathjax-full/js/adaptors/liteAdaptor').liteAdaptor;
            const RegisterHTMLHandler = require('mathjax-full/js/handlers/html').RegisterHTMLHandler;

            const adaptor = liteAdaptor();
            RegisterHTMLHandler(adaptor);

            const doc = mj.document('', {
                InputJax: new TeX({ packages: ['base'] }),
                OutputJax: new SVG({ fontCache: 'none' })
            });

            this._mathjax = { mathjax: mj, adaptor: adaptor, doc: doc };
            return;
        } catch (e) {
            console.warn('[draw.js] failed to init mathjax via require():', e);
        }

        // If all else fails, leave _mathjax null so caller falls back to KaTeX
        this._mathjax = null;
    }

    clearDOMElements() {
        for (const element of this.DOMElements) {
            element.remove();
        }

        this.DOMElements = [];
    }

    clear(x = 0, y = 0, width = this.canvas.width, height = this.canvas.height) {
        this.clearDOMElements();
        this.ctx.clearRect(x, y, width, height);
    }

    clearCircle(x, y, radius) {
        this.ctx.save();
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI, false);
        this.ctx.clip();
        this.ctx.clearRect(x - radius - 1, y - radius - 1, radius * 2 + 2, radius * 2 + 2);
        this.ctx.restore();
    }

    capture(canvas, sourceX = 0, sourceY = 0, targetX = 0, targetY = 0) {
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
        let [x, y] = point;

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

        const alpha = 2 * Math.PI / 3;

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
        const { points, smooth, color, width, arrowHead, fillColor, dashed } = args;

        if (points.length < 1) return;

        if (smooth) {
            this.ctx.lineCap = 'round';
            this.ctx.lineJoin = 'round';
        } else {
            this.ctx.lineCap = 'butt';
            this.ctx.lineJoin = 'butt';
        }

        if (dashed) {
            this.ctx.setLineDash([5, 10]);
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

        this.ctx.setLineDash([]);
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

    async drawLatex(args, latexContainer, callback) {
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

        // First attempt: render using MathJax to get pure SVG vector output.
        await this._ensureMathJax();

        if (this._mathjax) {
            try {
                const node = this._mathjax.doc.convert(source, { display: true });
                const outer = this._mathjax.adaptor.outerHTML(node);
                const svgMatch = outer.match(/<svg[\s\S]*?<\/svg>/i);
                let svgString = svgMatch ? svgMatch[0] : outer;

                // Apply inline styles for size/color where possible
                try {
                    const requestedSize = (fontSize !== undefined && fontSize !== null) ? fontSize : 12;
                    const requestedColor = color || 'black';
                    if (/\bstyle\s*=\s*"/i.test(svgString)) {
                        svgString = svgString.replace(/<svg([^>]*)style\s*=\s*"/i, `<svg$1style="font-size: ${requestedSize}pt; color: ${requestedColor}; fill: ${requestedColor}; stroke: ${requestedColor}; `);
                    } else {
                        svgString = svgString.replace(/<svg(\s*)/i, `<svg style="font-size: ${requestedSize}pt; color: ${requestedColor}; fill: ${requestedColor}; stroke: ${requestedColor};" $1`);
                    }
                } catch (e) { }

                // Determine intrinsic width/height from attributes or viewBox
                let adjustedWidth = null;
                let adjustedHeight = null;
                try {
                    const wMatch = svgString.match(/\swidth=\"([0-9.]+)\"/i);
                    const hMatch = svgString.match(/\sheight=\"([0-9.]+)\"/i);
                    if (wMatch) adjustedWidth = parseFloat(wMatch[1]);
                    if (hMatch) adjustedHeight = parseFloat(hMatch[1]);
                    if ((!adjustedWidth || !adjustedHeight)) {
                        const vbMatch = svgString.match(/viewBox=\"([0-9.\s-]+)\"/i);
                        if (vbMatch) {
                            const parts = vbMatch[1].trim().split(/\s+/).map(parseFloat);
                            if (parts && parts.length === 4) {
                                adjustedWidth = adjustedWidth || parts[2];
                                adjustedHeight = adjustedHeight || parts[3];
                            }
                        }
                    }
                } catch (e) { }

                // Compute scale/size for preview
                const requestedPt = (fontSize !== undefined && fontSize !== null) ? fontSize : 12;
                const requestedPx = requestedPt * (96 / 72);
                const displayMultiplier = 2.0;
                const targetHeight = requestedPx * displayMultiplier;

                const baseH = adjustedHeight || 1;
                const scale = targetHeight / baseH || 1;

                const w = (adjustedWidth || 1) * scale;
                const h = Math.max(1, baseH * scale);

                const px = (point && point[0] !== undefined) ? point[0] : 0;
                const py = (point && point[1] !== undefined) ? point[1] : 0;

                // Create a DOM SVG overlay for preview
                try {
                    const parser = new DOMParser();
                    const tmp = parser.parseFromString(svgString, 'image/svg+xml');
                    let svgEl = tmp.querySelector('svg');
                    if (!svgEl) {
                        svgEl = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                        svgEl.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                        svgEl.innerHTML = svgString;
                    }
                        svgEl.setAttribute('width', Math.max(1, Math.round(w)));
                        svgEl.setAttribute('height', Math.max(1, Math.round(h)));
                        svgEl.style.position = 'absolute';
                        const canvasLeftPage = Math.round(px - w / 2);
                        const canvasTopPage = Math.round(py - h / 2);
                        svgEl.style.left = canvasLeftPage + 'px';
                        svgEl.style.top = canvasTopPage + 'px';
                    svgEl.style.pointerEvents = 'none';
                    svgEl.style.zIndex = 9999;
                    const previewColor = (color !== undefined && color !== null) ? color : 'black';
                    svgEl.style.color = previewColor;
                    svgEl.style.fill = previewColor;
                    svgEl.style.stroke = previewColor;
                        // Also size/position the latex canvas so pen calculations
                        // that rely on `latexArtist.canvas.width/height` still work.
                        try {
                            this.canvas.style.left = canvasLeftPage + 'px';
                            this.canvas.style.top = canvasTopPage + 'px';
                            this.canvas.width = Math.max(1, Math.round(w));
                            this.canvas.height = Math.max(1, Math.round(h));
                        } catch (e) {}

                        svgEl.dataset.preview = 'latex';
                        document.body.appendChild(svgEl);
                        this.DOMElements.push(svgEl);

                        // Also rasterize the SVG into the latex artist's real canvas
                        // (hidden) so committing the latex (capture) copies a proper
                        // raster preview into the main canvas while keeping on-screen
                        // preview as vector.
                        try {
                            const img = new Image();
                            const svgDataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);
                            img.onload = () => {
                                try {
                                    this._realCtx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                                    this._realCtx.drawImage(
                                        img,
                                        0, 0, img.naturalWidth || img.width || this.canvas.width, img.naturalHeight || img.height || this.canvas.height,
                                        0, 0, this.canvas.width, this.canvas.height
                                    );
                                } catch (e) { console.warn('[drawLatex] failed to draw raster preview to latex canvas:', e); }
                            };
                            img.onerror = () => {};
                            img.src = svgDataUrl;
                        } catch (e) { }
                } catch (err) {
                    console.warn('[drawLatex][MathJax] failed to create SVG overlay preview:', err);
                }

                // Compute main-canvas coordinates for exported fragment
                let pxMain = px;
                let pyMain = py;
                if (window && window.artist && window.artist.canvas) {
                    try {
                        const mainRect = window.artist.canvas.getBoundingClientRect();
                        const mainScaleX = (mainRect.width > 0) ? (window.artist.canvas.width / mainRect.width) : 1;
                        const mainScaleY = (mainRect.height > 0) ? (window.artist.canvas.height / mainRect.height) : 1;
                        pxMain = (px - mainRect.left) * mainScaleX;
                        pyMain = (py - mainRect.top) * mainScaleY;
                    } catch (e) { console.warn('[drawLatex][MathJax] failed to compute main canvas coords:', e); }
                }

                const innerTranslateX = -((adjustedWidth || 1) * scale) / 2;
                const innerTranslateY = -((adjustedHeight || 1) * scale) / 2;

                let innerSvgContent = svgString;
                let isFullSvg = false;
                try {
                    const m = svgString.match(/<svg[\s\S]*?<\/svg>/i);
                    if (m && m[0]) {
                        innerSvgContent = m[0];
                        isFullSvg = true;
                    }
                } catch (e) { innerSvgContent = svgString; }

                const fragColor = (color !== undefined && color !== null) ? color : 'black';
                const fragStyleAttr = ` style="color: ${fragColor}; fill: ${fragColor}; stroke: ${fragColor};"`;

                let svgFragment;
                if (isFullSvg) {
                    // If we have intrinsic width/height, center the full <svg>
                    let innerW = adjustedWidth || null;
                    let innerH = adjustedHeight || null;
                    try {
                        if ((!innerW || !innerH)) {
                            const vbMatch = innerSvgContent.match(/viewBox=\"([0-9.\s-]+)\"/i);
                            if (vbMatch) {
                                const parts = vbMatch[1].trim().split(/\s+/).map(parseFloat);
                                if (parts && parts.length === 4) {
                                    innerW = innerW || parts[2];
                                    innerH = innerH || parts[3];
                                }
                            }
                        }
                    } catch (e) { }

                    const tx = (innerW ? (pxMain - (innerW / 2)) : pxMain);
                    const ty = (innerH ? (pyMain - (innerH / 2)) : pyMain);

                    svgFragment = `\n<g transform="translate(${tx}, ${ty})"${fragStyleAttr}>` + innerSvgContent + `</g>`;
                } else {
                    svgFragment = `\n<g transform="translate(${pxMain}, ${pyMain})"${fragStyleAttr}>` +
                        `<g transform="translate(${innerTranslateX}, ${innerTranslateY}) scale(${scale})">` +
                        `${innerSvgContent}</g></g>`;
                }

                this._svgFragments.push(svgFragment);
                try { if (typeof window !== 'undefined') window.__maxwell_svg_fragments.push(svgFragment); } catch (e) { }

                if (callback !== undefined) callback();
                try { latexContainer.remove(); } catch (e) { }
                return;
            } catch (e) {
                console.warn('MathJax conversion failed, falling back to KaTeX foreignObject:', e);
                // fallthrough to KaTeX fallback below
            }
        }

        // Fallback: use KaTeX foreignObject embedding (existing behavior)
        katex.render(source, latexContainer, {
            throwOnError: false,
            displayMode: true
        });

        if (embed) {
            // Measure rendered HTML
            const adjustedWidth = latexContainer.offsetWidth;
            const adjustedHeight = latexContainer.offsetHeight;

            if (point === undefined) {
                point = [0, 0];
            }

            // Position and size this latex artist's canvas to content and draw preview into its real ctx
            const canvasLeftPage = Math.round(point[0] - adjustedWidth / 2);
            const canvasTopPage = Math.round(point[1] - adjustedHeight / 2);
            try {
                this.canvas.style.left = canvasLeftPage + 'px';
                this.canvas.style.top = canvasTopPage + 'px';
                this.canvas.width = Math.max(1, adjustedWidth);
                this.canvas.height = Math.max(1, adjustedHeight);
            } catch (e) {
                console.warn('[drawLatex][KaTeX] failed to resize latex canvas:', e);
            }

            const svgFull = `<?xml version="1.0" encoding="utf-8"?>` +
                `<svg xmlns="http://www.w3.org/2000/svg" width="${adjustedWidth}" height="${adjustedHeight}">` +
                `<foreignObject width="100%" height="100%">` +
                `<div xmlns="http://www.w3.org/1999/xhtml" style="font-size: ${fontSize}pt; color: ${color}; margin:0; padding:0;">${latexContainer.innerHTML}</div>` +
                `</foreignObject></svg>`;

            try {
                // Render preview as a DOM SVG overlay (vector) instead of rasterizing.
                const parser = new DOMParser();
                const tmp = parser.parseFromString(svgFull, 'image/svg+xml');
                let svgEl = tmp.querySelector('svg');
                if (!svgEl) {
                    svgEl = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    svgEl.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
                    svgEl.innerHTML = svgFull;
                }

                svgEl.setAttribute('width', Math.max(1, adjustedWidth));
                svgEl.setAttribute('height', Math.max(1, adjustedHeight));
                svgEl.style.position = 'absolute';
                svgEl.style.left = canvasLeftPage + 'px';
                svgEl.style.top = canvasTopPage + 'px';
                svgEl.style.pointerEvents = 'none';
                svgEl.style.zIndex = 9999;

                // Align the latex canvas so pen logic that captures from the canvas
                // continues to function. We keep the canvas sized (but hidden)
                // while the visible preview is the SVG overlay.
                try {
                    this.canvas.style.left = canvasLeftPage + 'px';
                    this.canvas.style.top = canvasTopPage + 'px';
                    this.canvas.width = Math.max(1, adjustedWidth);
                    this.canvas.height = Math.max(1, adjustedHeight);
                } catch (e) {}

                svgEl.dataset.preview = 'latex';
                document.body.appendChild(svgEl);
                this.DOMElements.push(svgEl);

                // Rasterize into latex canvas for capture-on-click
                try {
                    const img = new Image();
                    img.onload = () => {
                        try {
                            this._realCtx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                            this._realCtx.drawImage(
                                img,
                                0, 0, img.naturalWidth || img.width || this.canvas.width, img.naturalHeight || img.height || this.canvas.height,
                                0, 0, this.canvas.width, this.canvas.height
                            );
                        } catch (e) { console.warn('[drawLatex][KaTeX] failed to draw raster to latex canvas:', e); }
                    };
                    img.onerror = () => {};
                    img.src = svgDataUrl;
                } catch (e) {}

                if (callback !== undefined) callback();
            } catch (err) {
                console.warn('[drawLatex][KaTeX] failed to create SVG overlay preview:', err);
                if (callback !== undefined) callback();
            }

            // Compute main-canvas coordinates for exported fragment (if main artist exists)
            let pxMain = point[0];
            let pyMain = point[1];
            if (window && window.artist && window.artist.canvas) {
                try {
                    const mainRect = window.artist.canvas.getBoundingClientRect();
                    const mainScaleX = (mainRect.width > 0) ? (window.artist.canvas.width / mainRect.width) : 1;
                    const mainScaleY = (mainRect.height > 0) ? (window.artist.canvas.height / mainRect.height) : 1;
                    pxMain = (point[0] - mainRect.left) * mainScaleX;
                    pyMain = (point[1] - mainRect.top) * mainScaleY;
                } catch (e) {
                    console.warn('[drawLatex][KaTeX] failed to compute main canvas coords:', e);
                }
            }


            // Ensure the exported fragment carries an explicit color/style so
            // appearance matches what was previewed. KaTeX content is HTML
            // inside a foreignObject; we still wrap it with a styled group
            // so external SVG editors/renderers preserve the color.
            const katexFragColor = (color !== undefined && color !== null) ? color : 'black';
            const katexStyleAttr = ` style="color: ${katexFragColor}; fill: ${katexFragColor}; stroke: ${katexFragColor};"`;

            const mainSvgFragment = `\n<g transform="translate(${pxMain - adjustedWidth / 2}, ${pyMain - adjustedHeight / 2})"${katexStyleAttr}>` +
                `<foreignObject width="${adjustedWidth}" height="${adjustedHeight}">` +
                `<div xmlns=\"http://www.w3.org/1999/xhtml\" style=\"font-size: ${fontSize}pt; color: ${katexFragColor}; margin:0; padding:0;\">${latexContainer.innerHTML}</div>` +
                `</foreignObject></g>`;

            // store fragment locally and in the shared global list
            this._svgFragments.push(mainSvgFragment);
            try { if (typeof window !== 'undefined') window.__maxwell_svg_fragments.push(mainSvgFragment); } catch (e) { }
            // remove the temporary latex container from the DOM
            try { latexContainer.remove(); } catch (e) { }
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

    getSVGData() {
        // Prepend any stored SVG fragments (e.g., LaTeX foreignObjects) so
        // they're included in the final exported SVG alongside the canvas-to-svg output.
        let serialized = this._svgCtx.getSerializedSvg();

        // Strip out raster <image> elements that may have been recorded as previews.
        try {
            serialized = serialized.replace(/<image[\s\S]*?>\s*<\/image>/gi, '');
            serialized = serialized.replace(/<image[\s\S]*?\/>/gi, '');
        } catch (e) {
            // ignore regex failures
        }

        // Collect fragments from the current artist and from the shared global list.
        let fragments = [];
        if (this._svgFragments && this._svgFragments.length > 0) fragments = fragments.concat(this._svgFragments);
        try { if (typeof window !== 'undefined' && Array.isArray(window.__maxwell_svg_fragments)) fragments = fragments.concat(window.__maxwell_svg_fragments); } catch (e) { }

        // Deduplicate identical fragments (avoid inserting duplicates if stored
        // both locally and in the global list, or if drawLatex was called twice).
        try {
            const seen = new Set();
            fragments = fragments.filter(f => {
                if (seen.has(f)) return false;
                seen.add(f);
                return true;
            });
        } catch (e) {
            // if dedupe fails for any reason, continue with un-deduped fragments
        }

        if (fragments.length === 0) {
            // nothing to inject; clear local fragments to avoid leakage
            try { this._svgFragments = []; } catch (e) { }
            try { if (typeof window !== 'undefined' && Array.isArray(window.__maxwell_svg_fragments)) window.__maxwell_svg_fragments = []; } catch (e) { }
            return serialized;
        }

        // Before inserting fragments, extract any <defs> blocks from fragments
        // (MathJax often emits <defs> with fonts/styles) so we can merge them
        // into the root SVG's <defs> section. Remove the extracted <defs>
        // from the fragment strings so we don't duplicate them.
        let mergedDefs = '';
        try {
            fragments = fragments.map(f => {
                try {
                    const defsMatch = f.match(/<defs[^>]*>([\s\S]*?)<\/defs>/i);
                    if (defsMatch && defsMatch[1]) {
                        mergedDefs += defsMatch[1];
                        // remove the defs from fragment
                        return f.replace(/<defs[^>]*>[\s\S]*?<\/defs>/i, '');
                    }
                } catch (e) { }
                return f;
            });
        } catch (e) {
            // ignore
        }

        // If we found merged defs, we'll merge them in when we reconstruct
        // the final single-root SVG below (rather than naively inserting into
        // the possibly malformed serialized string).

        // Rebuild the final SVG using DOM parsing to avoid brittle regex issues
        try {
            // Parse the serialized SVG string into a DOM document
            const parser = new DOMParser();
            const parsedDoc = parser.parseFromString(serialized, 'image/svg+xml');
            const firstRoot = parsedDoc.querySelector('svg');

            // Create a fresh output SVG document
            const NS = 'http://www.w3.org/2000/svg';
            const outDoc = document.implementation.createDocument(NS, 'svg', null);
            const outRoot = outDoc.documentElement;

            // Copy attributes from the recorder's root if present
            if (firstRoot) {
                for (const attr of Array.from(firstRoot.attributes || [])) {
                    outRoot.setAttribute(attr.name, attr.value);
                }
            }

            // Helper to import nodes from an SVG/XML string into outDoc
            const importFromString = (str) => {
                const tmp = parser.parseFromString(`<svg xmlns="${NS}">${str}</svg>`, 'image/svg+xml');
                const tmpRoot = tmp.querySelector('svg');
                const nodes = [];
                if (tmpRoot) {
                    for (const child of Array.from(tmpRoot.childNodes)) {
                        nodes.push(outDoc.importNode(child, true));
                    }
                }
                return nodes;
            };

            // Create a single <defs> element in the output and merge defs into it
            const outDefs = outDoc.createElementNS(NS, 'defs');
            let hasDefs = false;

            // Merge defs: first take any defs from the recorder root
            if (firstRoot) {
                const rootDefs = firstRoot.querySelector('defs');
                if (rootDefs) {
                    for (const child of Array.from(rootDefs.childNodes)) {
                        outDefs.appendChild(outDoc.importNode(child, true));
                        hasDefs = true;
                    }
                }
            }

            // Then merge collected defs from fragments (mergedDefs string)
            if (mergedDefs) {
                const defsNodes = importFromString(mergedDefs);
                for (const n of defsNodes) {
                    outDefs.appendChild(n);
                    hasDefs = true;
                }
            }

            if (hasDefs) outRoot.appendChild(outDefs);

            // Append other children from the recorder root (excluding defs)
            if (firstRoot) {
                for (const child of Array.from(firstRoot.childNodes)) {
                    if (child.nodeName && child.nodeName.toLowerCase() === 'defs') continue;
                    // If the recorder accidentally nested an <svg> wrapper, unwrap it
                    // and import its children instead of importing the svg element
                    // itself to avoid empty/nested root SVGs.
                    if (child.nodeName && child.nodeName.toLowerCase() === 'svg') {
                        for (const sub of Array.from(child.childNodes)) {
                            outRoot.appendChild(outDoc.importNode(sub, true));
                        }
                    } else {
                        outRoot.appendChild(outDoc.importNode(child, true));
                    }
                }
            }

            // If we have a live global overlay of committed vector elements,
            // prefer importing those DOM nodes directly into the output SVG.
            // The overlay contains the normalized, positioned groups created
            // at commit time and avoids unit/viewBox mismatch from original
            // MathJax-produced fragments.
            try {
                if (typeof window !== 'undefined' && window.__maxwell_svg_overlay) {
                    const liveOverlaySvg = window.__maxwell_svg_overlay.querySelector('svg');
                    if (liveOverlaySvg) {
                        for (const child of Array.from(liveOverlaySvg.childNodes)) {
                            outRoot.appendChild(outDoc.importNode(child, true));
                        }
                        // We've already included committed vectors; clear fragments
                        // to avoid double-insertion of the same visual content.
                        fragments = [];
                    }
                }
            } catch (e) {
                // ignore overlay import failures and fall back to fragment import
            }

            // Finally, append each cleaned fragment into the output root.
            // Normalize fragments so nested <svg> or translated groups are
            // converted to groups positioned in the main SVG coordinate space.
            for (const frag of fragments) {
                try {
                    // Parse the fragment into a temporary document so we can
                    // inspect its structure (g wrappers, nested svg, viewBox).
                    const tmpFragDoc = parser.parseFromString(`<svg xmlns="${NS}">${frag}</svg>`, 'image/svg+xml');
                    const fragRoot = tmpFragDoc.querySelector('svg');

                    // Helper to import a node into outDoc
                    const importNode = (node) => outDoc.importNode(node, true);

                    // If fragment is a single <svg> or a <g> wrapping an <svg>,
                    // unwrap and normalize.
                    const firstChild = fragRoot && fragRoot.firstElementChild;
                    if (firstChild) {
                        // Case A: <svg> ... </svg> (fragment was full svg)
                        if (firstChild.nodeName.toLowerCase() === 'svg') {
                            const inner = firstChild;
                            // Get viewBox offsets if present
                            let minX = 0, minY = 0;
                            try {
                                const vb = inner.getAttribute('viewBox');
                                if (vb) {
                                    const parts = vb.trim().split(/\s+/).map(parseFloat);
                                    if (parts && parts.length === 4) {
                                        minX = parts[0] || 0;
                                        minY = parts[1] || 0;
                                    }
                                }
                            } catch (e) {}

                            const wrapper = outDoc.createElementNS(NS, 'g');
                            if (minX !== 0 || minY !== 0) {
                                wrapper.setAttribute('transform', `translate(${-minX}, ${-minY})`);
                            }

                            for (const child of Array.from(inner.childNodes)) {
                                wrapper.appendChild(importNode(child));
                            }

                            outRoot.appendChild(wrapper);
                            continue;
                        }

                        // Case B: top-level <g> that may contain an <svg> child
                        if (firstChild.nodeName.toLowerCase() === 'g') {
                            const topG = firstChild;
                            const innerSvg = topG.querySelector('svg');
                            if (innerSvg) {
                                // extract translate from topG if present
                                let tx = 0, ty = 0;
                                try {
                                    const tf = topG.getAttribute('transform');
                                    if (tf) {
                                        const m = tf.match(/translate\(\s*([\-0-9.+eE]+)(?:[,\s]+([\-0-9.+eE]+))?\s*\)/i);
                                        if (m) {
                                            tx = parseFloat(m[1]) || 0;
                                            ty = parseFloat(m[2]) || 0;
                                        }
                                    }
                                } catch (e) {}

                                // get inner svg viewBox offset
                                let minX = 0, minY = 0;
                                try {
                                    const vb = innerSvg.getAttribute('viewBox');
                                    if (vb) {
                                        const parts = vb.trim().split(/\s+/).map(parseFloat);
                                        if (parts && parts.length === 4) {
                                            minX = parts[0] || 0;
                                            minY = parts[1] || 0;
                                        }
                                    }
                                } catch (e) {}

                                // Compute adjusted translation so that inner svg content
                                // is located correctly in the root coordinate space.
                                const adjX = tx - minX;
                                const adjY = ty - minY;

                                const wrapper = outDoc.createElementNS(NS, 'g');
                                if (adjX !== 0 || adjY !== 0) {
                                    wrapper.setAttribute('transform', `translate(${adjX}, ${adjY})`);
                                }

                                // Import inner svg children into wrapper
                                for (const child of Array.from(innerSvg.childNodes)) {
                                    wrapper.appendChild(importNode(child));
                                }

                                outRoot.appendChild(wrapper);
                                continue;
                            }
                        }
                    }

                    // Default: fallback to importing whatever nodes we parsed
                    const nodes = importFromString(frag);
                    for (const n of nodes) outRoot.appendChild(n);
                } catch (e) {
                    // if parsing a fragment fails, append as a text node
                    outRoot.appendChild(outDoc.createTextNode(frag));
                }
            }

            // Serialize the constructed document
            const serializer = new XMLSerializer();
            const result = serializer.serializeToString(outDoc);

            // Clear fragment stores so subsequent exports start fresh.
            try { this._svgFragments = []; } catch (e) { }
            try { if (typeof window !== 'undefined' && Array.isArray(window.__maxwell_svg_fragments)) window.__maxwell_svg_fragments = []; } catch (e) { }

            return result;
        } catch (e) {
            console.warn('[getSVGData] DOM-based rebuild failed, falling back to string append:', e);
        }

        // fallback: append fragments
        try {
            const result = serialized + '\n' + fragments.join('\n');
            try { this._svgFragments = []; } catch (e) { }
            try { if (typeof window !== 'undefined' && Array.isArray(window.__maxwell_svg_fragments)) window.__maxwell_svg_fragments = []; } catch (e) { }
            return result;
        } catch (e) {
            // as a last resort return original serialized
            try { this._svgFragments = []; } catch (e) { }
            try { if (typeof window !== 'undefined' && Array.isArray(window.__maxwell_svg_fragments)) window.__maxwell_svg_fragments = []; } catch (e) { }
            return serialized;
        }
    }

    // Commit a cleaned SVG fragment into the main artist as a vector element.
    // This appends the fragment into a shared overlay SVG (so it appears
    // immediately as vector in the UI) and records it in the fragment lists
    // so exports include it as vector.
    commitSVGFragment(fragmentString, opts = {}) {
        try {
            const NS = 'http://www.w3.org/2000/svg';
            if (typeof window === 'undefined') return;

            // Ensure global overlay exists and is aligned with artist.canvas
            if (!window.__maxwell_svg_overlay) {
                const overlay = document.createElement('div');
                overlay.style.position = 'absolute';
                try {
                    const r = this.canvas.getBoundingClientRect();
                    overlay.style.left = Math.round(r.left) + 'px';
                    overlay.style.top = Math.round(r.top) + 'px';
                    overlay.style.width = Math.round(r.width) + 'px';
                    overlay.style.height = Math.round(r.height) + 'px';
                } catch (e) {
                    overlay.style.left = (this.canvas.style.left || '0px');
                    overlay.style.top = (this.canvas.style.top || '0px');
                }
                overlay.style.pointerEvents = 'none';
                overlay.style.zIndex = 99999;
                overlay.id = '__maxwell_svg_overlay';

                const svgRoot = document.createElementNS(NS, 'svg');
                svgRoot.setAttribute('xmlns', NS);
                svgRoot.setAttribute('width', this.canvas.width);
                svgRoot.setAttribute('height', this.canvas.height);
                svgRoot.setAttribute('viewBox', `0 0 ${this.canvas.width} ${this.canvas.height}`);
                svgRoot.style.width = '100%';
                svgRoot.style.height = '100%';
                overlay.appendChild(svgRoot);
                document.body.appendChild(overlay);
                window.__maxwell_svg_overlay = overlay;
            }

            const overlay = window.__maxwell_svg_overlay;
            const svgRoot = overlay.querySelector('svg');

            // Refresh overlay position/size
            try {
                const r = this.canvas.getBoundingClientRect();
                overlay.style.left = Math.round(r.left) + 'px';
                overlay.style.top = Math.round(r.top) + 'px';
                overlay.style.width = Math.round(r.width) + 'px';
                overlay.style.height = Math.round(r.height) + 'px';
                svgRoot.setAttribute('width', this.canvas.width);
                svgRoot.setAttribute('height', this.canvas.height);
                svgRoot.setAttribute('viewBox', `0 0 ${this.canvas.width} ${this.canvas.height}`);
            } catch (e) { }

            console.debug('[commitSVGFragment] called, fragment length', fragmentString ? fragmentString.length : 0, 'opts', opts);

            const parser = new DOMParser();
            const tmp = parser.parseFromString(`<svg xmlns="${NS}">${fragmentString}</svg>`, 'image/svg+xml');
            const tmpRoot = tmp.querySelector('svg');

            if (!tmpRoot) {
                svgRoot.appendChild(document.createTextNode(fragmentString));
                try { this._svgFragments.push(fragmentString); } catch (e) {}
                try { window.__maxwell_svg_fragments = window.__maxwell_svg_fragments || []; window.__maxwell_svg_fragments.push(fragmentString); } catch (e) {}
                return;
            }

            // Create a temporary offscreen SVG to measure the fragment's bbox
            const tempContainer = document.createElement('div');
            tempContainer.style.position = 'absolute';
            tempContainer.style.left = '-99999px';
            tempContainer.style.top = '-99999px';
            tempContainer.style.width = '1px';
            tempContainer.style.height = '1px';
            tempContainer.style.overflow = 'hidden';
            tempContainer.style.pointerEvents = 'none';
            document.body.appendChild(tempContainer);

            const tempSVG = document.createElementNS(NS, 'svg');
            tempSVG.setAttribute('xmlns', NS);
            tempContainer.appendChild(tempSVG);

            const tempWrapper = document.createElementNS(NS, 'g');
            tempSVG.appendChild(tempWrapper);

            // Import fragment contents into the temp wrapper (unwrap nested svg)
            const children = Array.from(tmpRoot.childNodes);
            for (const child of children) {
                if (child.nodeName && child.nodeName.toLowerCase() === 'svg') {
                    for (const sub of Array.from(child.childNodes)) {
                        tempWrapper.appendChild(document.importNode(sub, true));
                    }
                } else {
                    tempWrapper.appendChild(document.importNode(child, true));
                }
            }

            // Try to measure the bbox
            let bbox = null;
            try {
                bbox = tempWrapper.getBBox();
                console.debug('[commitSVGFragment] temp bbox', bbox);
            } catch (e) {
                console.debug('[commitSVGFragment] getBBox failed on temp wrapper', e);
            }

            // Compute desired target position in overlay coordinate space
            let desiredX = 0;
            let desiredY = 0;
            try {
                const mainRect = this.canvas.getBoundingClientRect();
                const scaleX = (mainRect.width > 0) ? (this.canvas.width / mainRect.width) : 1;
                const scaleY = (mainRect.height > 0) ? (this.canvas.height / mainRect.height) : 1;

                if (opts && opts.latexArtist && Array.isArray(opts.latexArtist.DOMElements)) {
                    const previewEl = opts.latexArtist.DOMElements.find(el => el && el.dataset && el.dataset.preview === 'latex');
                    if (previewEl) {
                        const pr = previewEl.getBoundingClientRect();
                        desiredX = (pr.left - mainRect.left) * scaleX;
                        desiredY = (pr.top - mainRect.top) * scaleY;
                        console.debug('[commitSVGFragment] using latexArtist preview bounding rect', pr, '=>', desiredX, desiredY);
                    }
                }

                if ((desiredX === 0 && desiredY === 0) && opts && typeof opts.pageX === 'number' && typeof opts.pageY === 'number') {
                    desiredX = (opts.pageX - mainRect.left) * scaleX;
                    desiredY = (opts.pageY - mainRect.top) * scaleY;
                    console.debug('[commitSVGFragment] using page coords', opts.pageX, opts.pageY, '=>', desiredX, desiredY);
                }

                // Fallback to center of canvas
                if (!isFinite(desiredX) || !isFinite(desiredY)) {
                    desiredX = this.canvas.width / 2;
                    desiredY = this.canvas.height / 2;
                    console.debug('[commitSVGFragment] falling back to canvas center', desiredX, desiredY);
                }
            } catch (e) {
                console.debug('[commitSVGFragment] failed to compute desired position', e);
                desiredX = this.canvas.width / 2;
                desiredY = this.canvas.height / 2;
            }

            // Compute translation so that the fragment's bbox top-left lands at desiredX/Y
            let dx = desiredX;
            let dy = desiredY;
            if (bbox && isFinite(bbox.x) && isFinite(bbox.y)) {
                dx = desiredX - bbox.x;
                dy = desiredY - bbox.y;
            }

            // Create wrapper in real overlay and set computed translation
            const wrapper = document.createElementNS(NS, 'g');
            wrapper.setAttribute('transform', `translate(${dx}, ${dy})`);
            svgRoot.appendChild(wrapper);

            // Import actual fragment nodes into wrapper (unwrap nested svg)
            for (const child of children) {
                try {
                    if (child.nodeName && child.nodeName.toLowerCase() === 'svg') {
                        for (const sub of Array.from(child.childNodes)) {
                            wrapper.appendChild(document.importNode(sub, true));
                        }
                    } else {
                        wrapper.appendChild(document.importNode(child, true));
                    }
                } catch (e) {
                    try { wrapper.appendChild(child.cloneNode(true)); } catch (ee) { /* ignore */ }
                }
            }

            // Cleanup temp container
            try { tempContainer.remove(); } catch (e) { /* ignore */ }

            // Record fragment for export
            try { this._svgFragments.push(fragmentString); } catch (e) {}
            try { window.__maxwell_svg_fragments = window.__maxwell_svg_fragments || []; window.__maxwell_svg_fragments.push(fragmentString); } catch (e) {}
        } catch (e) {
            console.warn('[commitSVGFragment] failed to commit fragment:', e);
        }
    }
}
