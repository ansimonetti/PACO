import sys
import json
from unittest.mock import MagicMock, patch

# No /app path needed locally if running from root

from gui.src.model import etl
from gui.src.env import EXPRESSION, BOUND, IMPACTS_NAMES

def verify_fix():
    print("Verifying _fetch_strategy_data logic...")

    explanation_svg = "data:image/svg+xml;base64,PHN2Zz5WRVJJRklFRDwvc3ZnPg=="
    bdds_in_db = {"C1": ["counter_execution", explanation_svg]}
    
    mock_record = MagicMock()
    mock_record.bdds = json.dumps(bdds_in_db)

    with patch('gui.src.model.etl.fetch_strategy', return_value=mock_record) as mock_fetch:
        with patch('gui.src.model.etl.extract_nodes', return_value=([], [], [], [])):
            # Correctly use the constant value as key
            with patch('gui.src.model.etl.filter_bpmn', return_value={IMPACTS_NAMES: ["Cost"]}):
                
                bpmn_store = {EXPRESSION: "(A)", IMPACTS_NAMES: ["Cost"]}
                bound_store = {BOUND: {"Cost": 10}}
                
                result = etl._fetch_strategy_data(bpmn_store, bound_store)
                
                if not result:
                    print("FAILURE: Result is None")
                    return
                
                retrieved_svg = result["C1"][1]
                
                if retrieved_svg == explanation_svg:
                    print(f"SUCCESS: SVG retrieved correctly: {retrieved_svg[:30]}...")
                elif "base64,base64" in retrieved_svg:
                    print(f"FAILURE: Double encoding detected! {retrieved_svg[:50]}...")
                else:
                    print(f"FAILURE: Content mismatch. Got: {retrieved_svg[:50]}...")

if __name__ == "__main__":
    verify_fix()
