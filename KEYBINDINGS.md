# Maxwell Keybindings

This document summarizes the keybindings defined in `app/rjs/ui/keymap.js` (as of the latest scan). Bindings are grouped into:

- Global / general bindings (`generalKeymap`) — available application-wide
- Pen bindings (`penKeymap`) — actions that act on the current pen and drawing tools
- Parsed pen-specific bindings (`parsedPenKeymap`) — mappings that are passed to `pen.parse(...)` and therefore vary by pen implementation

Notes
- Bindings that mention `currentPen.enabled` or similar are only active when the pen is enabled (in drawing mode).
- Keys prefixed with `~` are two-stage bindings that accept a subsequent key argument (e.g. `~g` + `<key>`). The code pattern is an array: `[predicate, handler(key)]` where the handler receives the additional key pressed after the initial `~X`.
- Keys that contain spaces like `u Meta+z` are alternate triggers (either `u` or `Meta+z`).

---

## Global / General Keymap

- `Control+c` — Stop the current `sequence` if one is running. (Calls `sequence.stop()`)
- `Control+u` — Clear the canvas (calls `clearCanvas`). Clears both active pen canvas and background when appropriate.
- `Control+b` — Toggle the background (calls `toggleBackground`).
- `Control+l` — Toggle `Properties.externalPrompt` (external vs. inline prompt for text input).
- `Control+p` — Toggle the current pen's enabled state. When enabling/disabling, updates `currentPenLabel` to show the pen name.
- `Meta+Enter` — Toggle full-screen on the current Electron window and call `resizeCanvas()`.
- `=` — If the current pen is enabled, zoom in (`zoom(.2)`). Otherwise no-op.
- `-` — If the current pen is enabled, zoom out (`zoom(-.2)`). Otherwise no-op.
- `0` — If the current pen is enabled, reset zoom (`zoom(1, false)`). Otherwise no-op.

Two-stage / snippet-like global bindings:
- `~q` — Snippet recording: invoked as either `~q` (start) or `~q` + `<key>` to record with a key: 
  - `() => snippetLibrary.record()`
  - `key => snippetLibrary.record(key)`
- `~ ` (tilde + Space) — Snippet playback: predicate checks `currentPen.enabled`. Handlers:
  - `() => currentPen.enabled` (predicate)
  - `key => snippetLibrary.play(key)` — play the snippet bound to `key`.

Other global:
- `Enter` — If `Properties.capture` is set, ensure the pen is enabled, call `captureArea(...Properties.capture)`, and clear `Properties.capturePath`.

---

## Pen Keymap (applies to the current pen)

- `Shift+c` — Clear entire drawing state: `clearCanvas()` plus clear each pen's artist and take a history snapshot for each pen.
- `Escape Control+[` — Cancel snippet recording, stop recording state, and cancel current pen action if enabled. (Sets `snippetLibrary.isRecording = false` and `currentPen.cancel()`)
- `;` — If pen enabled: create LaTeX for the pen (`currentPen.createLatex()`).
- `/` — If pen enabled and pen is in selection mode (`penModes.SELECTION`), rotate the selection (`currentPen.rotate()`).

Two-stage pen bindings (tilde-prefixed — expect an extra key argument):

- `~g` — If `currentPen.enabled`, `key => currentPen.setStyle(key)` (change pen style using `key`).
  - Possible keys: `a`, `d`, `f`.
    - `a` → toggle `arrow` style
    - `d` → toggle `dashed` style
    - `f` → toggle `shape-fill` style

- `~n` — If `currentPen.enabled`, `key => currentPen.createShape(key)` (create a named shape).
  - Possible keys: `r`, `c`, `a`, `t`.
    - `r` → `Rect`
    - `c` → `Circle`
    - `a` → `Arc`
    - `t` → `RTriangle`

- `~p` — If `currentPen.enabled`, `key => clipboardFor(key).paste(key)` (paste from a pen-specific clipboard slot).
  - Possible keys and semantics:
    - numeric strings (`0`, `1`, `2`, ...) — paste the corresponding item index from the pen clipboard history (0 = most recent).
    - `p` (or `P`) — shorthand for the most recent item (treated as index `0`).
    - any non-numeric key present in the clipboard registry (registered previously via `~w`) — will paste the buffer registered under that key.
  - Note: `clipboardFor(key)` chooses `globalClipboard` when the key is uppercase non-numeric; otherwise it uses the current pen's clipboard.

- `~P` — If `currentPen.enabled`, `key => globalClipboard.paste(key)` (paste from the global clipboard slot).
  - Possible keys: same semantics as `~p`, but always targets `globalClipboard`.

- `~w` — If `currentPen.enabled` and there is a completed selection, `key => { clipboardFor(key).register(key); currentPen.cancel(); }` (register selection into clipboard and cancel selection).
  - Possible keys:
    - any non-empty string may be used as a registry key; typical usage is a single character.
    - uppercase (A–Z) non-numeric keys will target the `globalClipboard` (via `clipboardFor(key)`); lowercase/number keys will register in the current pen's clipboard.

- `~x` — If `currentPen.enabled` and selection completed: `key => currentPen.selection.delete(key, clipboardFor(key))` (delete selection and optionally register into clipboard).
  - Possible keys: same conventions as `~w` — any non-empty string; uppercase non-numeric keys use `globalClipboard`, digits use numeric indexing semantics where relevant.

Special two-stage binding `~'` (tilde + apostrophe) — switch pens by single-character name:
- `~'` — If `currentPen.enabled`, then `key` is expected to be a single alphanumeric character matching `/^[A-Za-z0-9]$/`.
  - Possible keys: `A–Z`, `a–z`, `0–9` (single-character only).
  - Behavior:
    - If `key` does not exist in the `pens` map, a new `Pen(...)` is created and initialized under that single-character name.
    - The current pen is disabled and the new pen becomes `currentPen`; the code copies `currentPoint`, updates label/UI, toggles visibility and restores history/clipboard/snippet context.
    - After switching, `keymap` is recomputed as the union of `generalKeymap`, `penKeymap`, and `parseKeymapFor(currentPen)`.

Other pen-specific behaviors:
- `Shift+c` (see above) is a global clear for all pens and snapshots.

---

## Parsed Pen Keymap (`parsedPenKeymap`) — passed to `pen.parse(...)`

These keys are delegated to `pen.parse(...)` and result in pen-specific behavior. The mapping here is the canonical name passed to the pen's parser:

- `e` → `toggle-eraser`
- `c` → `clear`
- `.` → `next-color`
- `,` → `previous-color`
- `]` → `increase-brush-size`
- `[` → `decrease-brush-size`
- `Shift+>` → `increase-sensitivity`
- `Shift+<` → `decrease-sensitivity`
- `u Meta+z` → `undo` (either `u` key or `Meta+z`)
- `Control+r Meta+Shift+z` → `redo` (either `Control+r` or `Meta+Shift+z`)
- `s` → `select` (enter selection mode)
- `Shift+s` → `continuous-selection` (start continuous selection)
- `y` → `yank` (copy to clipboard without leaving selection?)
- `Shift+y` → `yank-with` (calls with `globalClipboard`)
- `d` → `delete` (mapped to `['delete', 'd']` in code; likely `delete` action with parameter `'d'`)
- `Shift+d` → `delete-with` (mapped to `['delete-with', 'D', globalClipboard]`)
- `l` → `draw-line`
- `Shift+l` → `continuous-draw-line`

Because these are fed to `pen.parse(...)`, their actual behavior depends on the pen implementation of `parse`. Typical effects: toggling eraser, changing color/brush size, undo/redo, selection/draw modes, clipboard operations.

---

## Implementation details & caveats

- Many bindings use predicates (e.g. `currentPen.enabled`) — some key handlers do nothing when the predicate is false.
- The `~` prefixed bindings are implemented as an array `[predicate, handler]`; the first function is used as a guard or readiness check, the second receives the following key argument.
- `parseKeymapFor(pen)` constructs a pen-specific `keymap` by iterating over `parsedPenKeymap` and calling `pen.parse(...)` for each entry. So pen-level actions are extensible per `Pen` implementation.
- The `~'` pen-switching binding is stateful and will create new `Pen` instances lazily when required.

---

If you want, I can:
- Generate a compact printable table with columns: `Key`, `When active`, `Action`.
- Expand the `parsedPenKeymap` section to include the exact expected behavior by scanning the `Pen` class implementation and `pen.parse` method.
- Add a quick reference overlay (HTML snippet) that renders this list in-app.

File created: `KEYBINDINGS.md` at repository root.
