from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from utils.env import PATH_IMAGE_BPMN_LARK, PATH_IMAGE_BPMN_LARK_SVG, RESOLUTION
from utils.print_sese_diagram import print_sese_diagram
from utils.automa import calc_strat, calc_strategy_paco
from utils.check_syntax import check_algo_is_usable, checkCorrectSyntax
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# swaggerui al link  http://127.0.0.1:8000/docs
# server al link http://127.0.0.1:8000/
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] 
)
class BPMNDefinition(BaseModel):
    expression: str
    h: Optional[int] = 0
    probabilities: Optional[Dict] = {}
    impacts: Dict = {}
    loop_thresholds: Optional[Dict] = {}    
    durations: Optional[Dict] = {}
    names: Optional[Dict] = {}
    delays: Optional[Dict] = {}
    impacts_names: Optional[List] = []    
    loop_round: Optional[Dict] = {}
    loops_prob: Optional[Dict] = {}

class BPMNPrinting(BaseModel):
    bpmn: BPMNDefinition
    resolution_bpmn: Optional[int] = RESOLUTION
    graph_options: Optional[Dict] = {}

class StrategyFounderAlgo(BaseModel):
    bpmn: dict
    bound: List[int]
    algo: str

@app.get("/")
async def get():
    return f"welcome to PACO server"

@app.get("/print_sese_diagram", response_class=FileResponse)
async def get(request: BPMNPrinting):
    try:
        if not isinstance(request.bpmn, dict):
            return HTTPException(status_code=400, detail="Invalid input")
        if not checkCorrectSyntax(request.bpmn):
            return HTTPException(status_code=400, detail="Invalid BPMN syntax")
        bpmn = request.bpmn
        print(bpmn)
        print_sese_diagram(expression=bpmn.expression,
            h=bpmn.h, 
            probabilities=bpmn.probabilities, 
            impacts=bpmn.impacts, 
            loop_thresholds=bpmn.loop_thresholds, 
            outfile=PATH_IMAGE_BPMN_LARK, 
            outfile_svg=PATH_IMAGE_BPMN_LARK_SVG,
            graph_options=request.graph_options, 
            durations=bpmn.durations, 
            names=bpmn.names, 
            delays=bpmn.delays, 
            impacts_names=bpmn.impacts_names, 
            resolution_bpmn=request.resolution_bpmn, 
            loop_round=bpmn.loop_round, 
            loops_prob=bpmn.loops_prob
        )
        return FileResponse(PATH_IMAGE_BPMN_LARK, media_type='image/png', filename='output.png')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calc_strategy_paco")
async def calc_strategy_paco_api(request: StrategyFounderAlgo):
    try:
        if not isinstance(request.bpmn, dict) or not isinstance(request.bound, list):
            return HTTPException(status_code=400, detail="Invalid input")
        if not checkCorrectSyntax(request.bpmn):
            return HTTPException(status_code=400, detail="Invalid BPMN syntax")
        # if not check_algo_is_usable(request.bpmn, request.algo):
        #     return HTTPException(status_code=400, detail="The algorithm is not usable")
        print(request.bpmn, request.bound)
        result = calc_strategy_paco(request.bpmn, request.bound)# calc_strat(bpmn = request.bpmn, bound = request.bound, algo = request.algo)
        if result.get('error') != None:
            return HTTPException(status_code=400, detail=result.get('error'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == '__main__':   
    uvicorn.run(app, host="127.0.0.1", port=8000) # 0.0.0.0
