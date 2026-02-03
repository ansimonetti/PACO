import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder

from src.paco.parser.dot.bpmn import get_bpmn_dot_from_parse_tree
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.explainer.bdd.bdds import bdds_to_dict, bdds_to_dict_dot
from src.paco.parser.bpmn_parser import create_parse_tree
from src.paco.parser.create import create
from src.paco.parser.parse_tree import ParseTree
from src.paco.solver import paco
from src.utils import check_syntax as cs
from src.utils.check_syntax import check_bpmn_syntax
from src.utils.env import DURATIONS, IMPACTS_NAMES, EXPRESSION


def register_paco_api(app: FastAPI):
	@app.get("/create_bpmn")
	async def check_bpmn(request: dict) -> dict:
		bpmn = request.get("bpmn")
		if bpmn is None:
			raise HTTPException(status_code=400, detail="No BPMN found")
		if EXPRESSION not in bpmn or bpmn[EXPRESSION] == "":
			raise HTTPException(status_code=400, detail="No BPMN expression found")

		status = request.get("status", {})

		if IMPACTS_NAMES not in bpmn or bpmn[IMPACTS_NAMES] is None:
			raise HTTPException(status_code=400, detail="No impacts names found")
		if not isinstance(bpmn[IMPACTS_NAMES], list) or not all(isinstance(name, str) for name in bpmn[IMPACTS_NAMES]):
			raise HTTPException(status_code=400, detail="Invalid impacts names format, expected a list of strings")

		try:
			lark_tree = check_bpmn_syntax(dict(bpmn))
		except Exception as e:
			raise HTTPException(status_code=400, detail=str(e))

		try:
			parse_tree, _, _, _ = create_parse_tree(bpmn)

			return { "parse_tree" : parse_tree.to_dict(), "bpmn_dot": get_bpmn_dot_from_parse_tree(parse_tree, bpmn[IMPACTS_NAMES], status) }
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@app.get("/create_parse_tree")
	async def get_parse_tree(request: dict) -> dict:
		bpmn = request.get("bpmn")
		if bpmn is None:
			raise HTTPException(status_code=400, detail="No BPMN found")

		try:
			lark_tree = check_bpmn_syntax(dict(bpmn))
		except Exception as e:
			raise HTTPException(status_code=400, detail=str(e))

		try:
			bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])
			parse_tree, pending_choices, pending_natures, pending_loops = create_parse_tree(bpmn)

			return {"parse_tree": parse_tree.to_dict()}

		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@app.get("/create_execution_tree")
	async def get_execution_tree(request: dict) -> dict:
		bpmn = request.get("bpmn")
		if bpmn is None:
			raise HTTPException(status_code=400, detail="No BPMN found")
		try:
			bpmn = dict(bpmn)
			bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])
			lark_tree = check_bpmn_syntax(bpmn)
		except Exception as e:
			raise HTTPException(status_code=400, detail=str(e))

		try:
			parse_tree, pending_choices, pending_natures, execution_tree, times = create(bpmn)
			return {"parse_tree": parse_tree.to_dict(),
					"execution_tree": execution_tree.to_dict(),
					"times": times}

		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))

	@app.get("/create_strategy")
	async def search_strategy(request: dict) -> dict:
		bpmn = request.get("bpmn")
		bound = request.get("bound")
		parse_tree = request.get("parse_tree")
		execution_tree = request.get("execution_tree")
		search_only = request.get("search_only")

		if bpmn is None:
			raise HTTPException(status_code=400, detail="No BPMN found")
		if not isinstance(bpmn, dict):
			raise HTTPException(status_code=400, detail="Invalid BPMN format, expected a dictionary")
		if bound is None or not isinstance(bound, list):
			raise HTTPException(status_code=400, detail="Invalid 'bound' format, expected a list of float")
		if len(bound) != len(bpmn[IMPACTS_NAMES]):
			raise HTTPException(status_code=400, detail="Invalid 'bound' format, expected a list of float with the same size of impacts")
		if parse_tree is None:
			raise HTTPException(status_code=400, detail="No parse tree provided")
		if execution_tree is None:
			raise HTTPException(status_code=400, detail="No execution tree provided")
		if search_only is None or not isinstance(search_only, bool):
			search_only = False

		# BPMN Preprocessing
		try:
			bpmn = dict(bpmn)  # Ensure BPMN is a dictionary
			bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])  # Modify durations
			lark_tree = check_bpmn_syntax(bpmn)  # Validate BPMN syntax and Parse the BPMN expression
			bound = np.array(bound, dtype=np.float64)
			parse_tree, pending_choices, pending_natures = ParseTree.from_json(parse_tree, impact_size=len(bpmn[IMPACTS_NAMES]), non_cumulative_impact_size=0)
			execution_tree = ExecutionTree.from_json(parse_tree, execution_tree, pending_choices, pending_natures)
		except Exception as e:
			raise HTTPException(status_code=400, detail=str(e))

		try:
			text_result, result, times = paco(bpmn, bound, parse_tree=parse_tree, execution_tree=execution_tree, search_only=search_only)

			result_dict = {
				"result": text_result, "times": times,
				"bpmn": result["bpmn"], "bound": str(result["bound"]),
				"parse_tree": result["parse_tree"].to_dict(),
				"execution_tree": result["execution_tree"].to_dict(),
				"possible_min_solution": str([str(bound) for bound in result["possible_min_solution"]]),
				"guaranteed_bounds": str([str(bound) for bound in result["guaranteed_bounds"]])
			}


			x = result.get("expected_impacts")
			y = result.get("frontier_solution")
			if x is not None and y is not None:# Search Win
				result_dict.update({
					"expected_impacts" : str(x),
					"frontier_solution" : str([execution_tree.root.id for execution_tree in y])
				})

			x = result.get("strategy_tree")
			y = result.get("strategy_expected_impacts")
			z = result.get("strategy_expected_time")
			w = result.get("bdds")
			if x is not None and y is not None and z is not None and w is not None: # Strategy Explained Done
				result_dict.update({
					"strategy_tree": x.to_dict(),
					"strategy_expected_impacts": str(y),
					"strategy_expected_time": str(z),
					"bdds": bdds_to_dict(w),
					"bdds_dot": bdds_to_dict_dot(w)
				})

			return jsonable_encoder(result_dict)

		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))
