function createDualContext(realCtx, svgCtx) {
    // Return a Proxy that forwards method calls and property sets to both contexts.
    // Method return values come from the real (display) context.
    const functionCache = new Map();

    return new Proxy({}, {
        get(_, prop) {
            // Special-case non-function properties that should be read from realCtx
            if (typeof realCtx[prop] !== 'function') {
                return realCtx[prop];
            }

            // Cache wrapper functions to avoid recreating on each access
            if (!functionCache.has(prop)) {
                const wrapper = (...args) => {
                    const realFn = realCtx[prop];
                    const svgFn = svgCtx[prop];

                    let result;
                    if (typeof realFn === 'function') {
                        result = realFn.apply(realCtx, args);
                    }

                    if (typeof svgFn === 'function') {
                        try {
                            svgFn.apply(svgCtx, args);
                        } catch (e) {
                            // swallow svg errors for unsupported ops
                        }
                    }

                    return result;
                };
                functionCache.set(prop, wrapper);
            }

            return functionCache.get(prop);
        },

        set(_, prop, value) {
            try { realCtx[prop] = value; } catch (e) {}
            try { svgCtx[prop] = value; } catch (e) {}
            return true;
        },

        has(_, prop) {
            return prop in realCtx || prop in svgCtx;
        }
    });
}