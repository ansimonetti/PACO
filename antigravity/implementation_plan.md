# Implementation Plan - Add Generate BPMN Button

## User Review Required
> [!IMPORTANT]
> This change modifies how the BPMN model is generated. Instead of auto-generating on input change/debounce, it will now require an explicit click on the "Generate" button. This improves performance and user experience for complex expressions.

## Proposed Changes

### GUI Layout
#### [MODIFY] [inputs.py](file:///c:/Users/Emanuele/GithubRepo/PACO/gui/src/view/home/sidebar/bpmn_tab/inputs.py)
- Add a `dbc.Button` with id `generate-bpmn-btn` next to or below the `expression-bpmn` input.
- Layout adjustment: Use `dbc.InputGroup` or a flex container to align the input and button.

### GUI Controller
#### [MODIFY] [expression.py](file:///c:/Users/Emanuele/GithubRepo/PACO/gui/src/controller/home/sidebar/bpmn_tab/expression.py)
- Update `evaluate_expression` callback:
    - Change `Input('expression-bpmn', 'value')` to `State('expression-bpmn', 'value')`.
    - Add `Input('generate-bpmn-btn', 'n_clicks')`.
    - Handle the trigger logic: check if `ctx.triggered_id == 'generate-bpmn-btn'`.
    - Ensure it still handles the initial load or store synchronization if needed, or if we want to keep `expression-bpmn` as an Input for some cases?
        - *Decision*: Better to make the button the ONLY trigger for heavy re-computation.
        - *Refinement*: The `sync_input_with_store` callback (lines 84-93) keeps the input in sync with the store. The main `evaluate_expression` updates the store and SVG.
        - We will change `evaluate_expression` to trigger primarily on button click.

## Verification Plan

### Manual Verification
1.  **Open GUI**: Navigate to `http://127.0.0.1:8050`.
2.  **Sidebar**: Go to BPMN + CPI tab.
3.  **Check UI**: Verify "Generate" button is visible.
4.  **Action**:
    - Type a simple expression (e.g., `(A,B)`).
    - Verify *nothing happens* yet (no auto-update).
    - Click "Generate".
    - Verify diagram updates and "Expression is empty" alert disappears.
5.  **Browser Tool Test**: Create a browser recording to verify this interaction flow automatically.
