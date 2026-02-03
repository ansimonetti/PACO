import argparse

import numpy as np

from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.parser.parse_tree import ParseTree
from src.utils.env import (
    EXPRESSION,
    H,
    IMPACTS,
    DURATIONS,
    IMPACTS_NAMES,
    PROBABILITIES,
    DELAYS,
    LOOP_PROBABILITY,
    LOOP_ROUND,
)
from src.paco.solver import paco

__test__ = False

bpmn_new_example = {
    "bpmn": [{
            "expression": "(ProjectEvaluation, ((ResearchProjectA, (NoProblemA ^ [ProjectRiskA] OverCostDelayA)) / [ProjectSelection] (ResearchProjectB, (NoProblemB ^ [ProjectRiskB] OverCostDelayB))), ((DistributionPlanning /[DistributionChoice] DistributionOutsourcing) || (MarketingPlanning /[MarketingChoice] MarketingOutsourcing ) || (SupplyChainPlanning, (InternalImplementation / [ImplementationChoice] OutsourcedImplementation), (InternalSales / [SalesChoice] OutsourcedSales))))",
            "impacts": {
                "ProjectEvaluation": [50, 5, 10, 3],
                "ResearchProjectA": [300, 15, 40, 20],
                "NoProblemA": [0, 0, 0, 0],
                "OverCostDelayA": [100, 5, 10, 5],
                "ResearchProjectB": [250, 12, 35, 18],
                "NoProblemB": [0, 0, 0, 0],
                "OverCostDelayB": [120, 6, 15, 6],
                "SupplyChainPlanning": [150, 8, 20, 10],
                "DistributionPlanning": [180, 10, 30, 15],
                "DistributionOutsourcing": [200, 10, 30, 15],
                "MarketingPlanning": [250, 12, 40, 20],
                "MarketingOutsourcing": [300, 15, 50, 25],
                "OutsourcedResource": [220, 8, 20, 10],
                "InternalImplementation": [400, 20, 50, 25],
                "OutsourcedImplementation": [450, 18, 40, 20],
                "InternalSales": [300, 15, 40, 20],
                "OutsourcedSales": [350, 17, 45, 22]
            },
            "durations": {
                "ProjectEvaluation": [1, 2],
                "ResearchProjectA": [3, 5],
                "NoProblemA": [0, 0],
                "OverCostDelayA": [1, 2],
                "ResearchProjectB": [2, 4],
                "NoProblemB": [0, 0],
                "OverCostDelayB": [1, 2],
                "SupplyChainPlanning": [2, 3],
                "DistributionPlanning": [3, 4],
                "DistributionOutsourcing": [2, 3],
                "MarketingPlanning": [3, 5],
                "MarketingOutsourcing": [2, 3],
                "OutsourcedResource": [1, 2],
                "InternalImplementation": [4, 7],
                "OutsourcedImplementation": [3, 6],
                "InternalSales": [3, 10],
                "OutsourcedSales": [2, 10]
            },
            "impacts_names": ["cost", "worker hours", "materials", "risk"],
            "probabilities": {
                "ProjectRiskA": 0.7,
                "ProjectRiskB": 0.6
            },
            "delays": {
                "ProjectSelection": 0,
                "ResourceChoice": 0,
                "MarketingChoice": 0,
                "DistributionChoice": 0,
                "ImplementationChoice": 0,
                "SalesChoice": 0
            },
            "loop_round": {},
            "loop_probability": {},
            H:0
        }, [1800, 90, 250, 120]
    ],

"bpmn_logistic": [{
        "expression": "(OrderReceived, ((PrepareShipment || OrderValidation), (((RoadInternal / [RoadOutsource] (RoadCompanyA / [RoadCompany] RoadCompanyB)) ^ [TransportType] ((TrainCompanyA / [TrainCompanyAB] TrainCompanyB) / [TrainCompany] (TrainCompanyC / [TrainCompanyCD] TrainCompanyD)))), (Delivery, (ThermalDelivery / [ThermalOrElectric] ElectricDelivery / [ElectricOrHybrid] HybridDelivery))))",
        "impacts": {
            "OrderReceived": [0, 1, 0, 0],
            "PrepareShipment": [100, 2, 10, 2],
            "OrderValidation": [50, 1, 0, 1],
            "RoadInternal": [300, 6, 50, 6],
            "RoadCompanyA": [350, 5, 55, 5],
            "RoadCompanyB": [340, 5.5, 52, 5],
            "TrainCompanyA": [420, 4.5, 32, 4],
            "TrainCompanyB": [410, 5, 31, 4.5],
            "TrainCompanyC": [430, 4.8, 34, 4.2],
            "TrainCompanyD": [415, 5, 33, 4.1],
            "Delivery": [0,0,0,0],
            "ThermalDelivery": [150, 7, 60, 7],
            "ElectricDelivery": [130, 6, 5, 6],
            "HybridDelivery": [140, 6.5, 20, 6.5]
        },
        "durations": {
            "OrderReceived": [0, 1],
            "PrepareShipment": [0, 2],
            "OrderValidation": [0, 1],
            "RoadInternal": [0, 6],
            "RoadCompanyA": [0, 5],
            "RoadCompanyB": [0, 5.5],
            "TrainCompanyA": [0, 4.5],
            "TrainCompanyB": [0, 5],
            "TrainCompanyC": [0, 4.8],
            "TrainCompanyD": [0, 5],
            "Delivery": [1,1],
            "ThermalDelivery": [0, 7],
            "ElectricDelivery": [0, 6],
            "HybridDelivery": [0, 6.5]
        },
        "impacts_names": ["cost", "worker hours", "emissions", "fuel"],
        "probabilities": {"TransportType": 0.85},
        "delays": {
            "RoadOutsource": 0,
            "RoadCompany": 0,
            "TrainCompany": 0,
            "TrainCompanyAB": 0,
            "TrainCompanyCD": 0,
            "DeliveryChoice": 0,
            "ThermalOrElectric": 0,
            "ElectricOrHybrid": 0
        },
        "loop_round": {},
        "loop_probability": {},
        H: 0
    }, [597,16,65,15]
    ],
}

bpmn_ex = {
    # In Notebook
    "loop_example":  [{
        EXPRESSION: "T1, <[L1] T2 >",
        H: 0,
        IMPACTS: {"T1": [11, 15], "T2": [4, 2]},
        DURATIONS: {"T1": [0, 100], "T2": [0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {}, DELAYS: {}, LOOP_PROBABILITY: {'L1': 0.5}, LOOP_ROUND: {'L1': 10}
    }, [19, 19]
    ],
    # In Notebook
    "decision_based_example" : [{
        EXPRESSION: '((T1 /[C1] T2) || (( (T3 ^[N2] T4), TU1) ^[N1] ( (T5 ^[N3] T6), TU2)))',
        IMPACTS_NAMES: ['a', 'b'],
        IMPACTS: {'T1': [3, 1], 'T2': [1, 3], 'T3': [2, 0], 'T4': [0, 2], 'TU1': [3, 1], 'T5': [2, 0], 'T6': [0, 2], 'TU2': [1, 3]},
        DURATIONS: {'T1': [0, 1], 'T2': [0, 1], 'T3': [0, 1], 'T4': [0, 1], 'TU1': [0, 1], 'T5': [0, 1], 'T6': [0, 1], 'TU2': [0, 1]},
        PROBABILITIES: {'N2': 0.2, 'N1': 0.3, 'N3': 0.4},
        LOOP_PROBABILITY: {},
        DELAYS: {'C1': 1}, LOOP_ROUND: {}, H: 0,
        }, [5, 6]
    ],
    "natures of natures": [{
        EXPRESSION: "(Task1 ^ [N1] T2) ^[N] (T3 ^ [N2] T4)",
        H: 0,
        IMPACTS: {"Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
        DURATIONS: {"Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N": 0.5, "N1": 0.6, "N2": 0.7}, DELAYS: {}, LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [23.3, 24.4]],

    "only natures, no strategy (no choice)": [{
        EXPRESSION: "SimpleTask1, (Task1 ^ [N1] T2)",
        H: 0,
        IMPACTS: {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1]},
        DURATIONS: {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6}, DELAYS: {},LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [14.7, 16.7]],

    "bpmn_seq_natures": [{
        EXPRESSION: "SimpleTask1,  (Task1 ^ [N1] T2),  (T3 ^ [N2] T4)",
        H: 0,
        IMPACTS: {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
        DURATIONS: {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6, "N2": 0.7}, DELAYS: {}, LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [23.3, 24.4]],

    "bpmn_choices_natures": [{
        EXPRESSION: "(Cutting, ((HP ^ [N1]LP ) || ( FD / [C1] RD)), (HPHS / [C2] LPLS))",
        H: 0,
        IMPACTS: {"Cutting": [11, 15], "HP": [4, 2], "LP": [3, 1] , "FD": [8, 9], "RD": [10, 5] , "HPHS": [4, 7], "LPLS": [3, 8]},
        DURATIONS: {"Cutting": 1, "HP": 1, "LP": 1, "FD": 1, "RD":1 , "HPHS": 1, "LPLS": 1},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6},
        DELAYS: {"C1": 0, "C2": 0}, LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [26, 33.3]],

    "bpmn_prof": [{
        EXPRESSION: "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3)",
        H: 0,
        IMPACTS: {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0]},
        DURATIONS: {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100},
        IMPACTS_NAMES: ["cost", "r", "s", "e"],
        PROBABILITIES: {"N1": 0.5, "N2": 0.5},
        LOOP_PROBABILITY: {},
        DELAYS: {"c1": 0}, LOOP_ROUND: {}
    }, [1, 1, 1, 1]],

    "bpmn_unavoidable_tasks": [{
        EXPRESSION: "(TaskA ^ [C1] TaskB), Task2",
        H: 0,
        IMPACTS: {"TaskA": [10], "TaskB": [10], "Task2": [10]},
        DURATIONS: {"TaskA": 100, "TaskB": 100, "Task2": 100},
        IMPACTS_NAMES: ["cost"],
        PROBABILITIES: {"C1": 0.5}, DELAYS: {"C1": 0},LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [20]],
    "choice not explained": [{
        EXPRESSION: "(T1, ((TA_N1 ^[N1] TB_N1) || ( TA_C1 / [C1] TB_C1)), (TA_C2 / [C2] TB_C2))",
        H: 0,
        IMPACTS: {"T1": [11, 15], "TA_N1": [4, 2], "TB_N1": [3, 1] , "TA_C1": [8, 9], "TB_C1": [10, 5] , "TA_C2": [4, 7], "TB_C2": [3, 8]},
        DURATIONS: {"T1": 1, "TA_N1": 1, "TB_N1": 1, "TA_C1": 1, "TB_C1":1 , "TA_C2": 1, "TB_C2": 1},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6},
        DELAYS: {"C1": 0, "C2": 0},LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [30, 30]],

    #TODO
    "complete coloring strategy tree example": [{
        EXPRESSION: "(T1, ((TA_N1 ^[N1] TB_N1) || ( TA_C1 / [C1] TB_C1)), ((TA_C2 / [C2] TB_C2) || (TA_N2 ^[N2] TB_N2)))",
        H: 0,
        IMPACTS: {"T1": [1, 2], "TA_N1": [10, 5], "TB_N1": [5, 10] , "TA_C1": [20, 10], "TB_C1": [21, 11] , "TA_C2": [20, 10], "TB_C2": [10, 20], "TA_N2": [10, 5], "TB_N2": [5, 10]},
        DURATIONS: {"T1": 1, "TA_N1": 1, "TB_N1": 1, "TA_C1": 1, "TB_C1":1 , "TA_C2": 1, "TB_C2": 1, "TA_N2": 1, "TB_N2": 1},
        IMPACTS_NAMES: ["A", "B"],
        PROBABILITIES: {"N1": 0.6, "N2": 0.5},
        DELAYS: {"C1": 1, "C2": 0},LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [57, 48]],

    # TODO "multi condition BDD"
}



def run_calc_strategy_paco(bpmn_ex_dicts:dict, selected:int = -1):
    if selected == -1:
        for name, example in bpmn_ex_dicts.items():
            print(example[0], example[1])
            print('Type bpmn: ', name)
            print(paco(example[0], example[1]))

            #ask a string in input if the string is not yes exit
            answer = input("Do you want to continue? (yes/no): ")
            if answer != "yes" and answer != "y":
                break
    else:
        name, example = list(bpmn_ex_dicts.items())[selected]
        print(paco(example[0], example[1]))


bpmn_paper_example = {
    "Figure 1": [{
        EXPRESSION: "(Cutting, ((Bending, (HP^[N1]LP)) || (Milling, (FD/[C1]RD))), (HPHS / [C2] LPLS))",
        H: 0,
        IMPACTS: {"Cutting": [10, 1], "Bending": [20, 1], "Milling": [50, 1], "HP": [5, 4], "LP": [8, 1], "FD": [30, 1], "RD": [10, 1], "HPHS": [40, 1], "LPLS": [20, 3]},
        DURATIONS: {"Cutting": [0, 1], "Bending": [0, 1], "Milling": [0, 1], "HP": [0, 2], "LP": [0, 1], "FD": [0, 1], "RD": [0, 1], "HPHS": [0, 1], "LPLS": [0, 2]},
        IMPACTS_NAMES: ["electric energy", "worker hours"],
        PROBABILITIES: {"N1": 0.2}, DELAYS: {"C1": 0, "C2": 0},LOOP_PROBABILITY : {}, LOOP_ROUND: {}
        }, [135, 9]], #[135, 7]
    "Explainer Figure": [{
        EXPRESSION: "((t0p0 ^[p0] t1p0), (t0p5 /[p5] t1p5), (tp11, (t0p13 /[p13] t1p13),(t0p24 /[p24] t1p24) || (t0p12, tp20, (t0p22 ^[p22] t1p22) ^[p12] t1p12, tp21, (t0p23 ^ [p23] t1p23) ) ) )",
        H: 0,
        IMPACTS: {"t0p0": [2, 1, 0, 0, 0, 0], "t1p0": [1, 2, 0, 0, 0, 0], "t0p5": [1, 2, 0, 0, 0, 0], "t1p5": [2, 1, 0, 0, 0, 0], "tp11": [4, 2, 0, 0, 0, 0],
                  "t0p13": [0, 0, 8, 0, 0, 0], "t1p13": [0, 0, 0, 8, 0, 0], "t0p24": [0, 0, 0, 0, 5, 0], "t1p24": [0, 0, 0, 0, 0, 5], "t0p12": [3, 5, 0, 0, 0, 0],
                  "t1p12": [3, 5, 0, 0, 0, 0], "t0p23": [0, 0, 0, 0, 8, 1], "t1p23": [0, 0, 0, 0, 1, 8], "t0p22": [0, 0, 0, 0, 8, 1], "t1p22": [0, 0, 0, 0, 1, 8],
                  "tp20": [0, 0, 8, 0, 0, 0], "tp21": [0, 0, 0, 8, 0, 0]},

        DURATIONS: {"t0p0": [0, 1], "t1p0": [0, 1], "t0p5": [0, 1], "t1p5": [0, 1], "tp11": [0, 1], "t0p13": [0, 1], "t1p13": [0, 1], "t0p24": [0, 1], "t1p24": [0, 1], "t0p12": [0, 2], "t1p12": [0, 2], "t0p23": [0, 1], "t1p23": [0, 1], "t0p22": [0, 1], "t1p22": [0, 1], "tp20": [0, 1], "tp21": [0, 1] },
        IMPACTS_NAMES: ["A", "B", "C", "D", "E", "F"],
        PROBABILITIES: {"p0": 0.5, "p12": 0.5, "p22": 0.99, "p23":0.01}, DELAYS: {"p5": 0, "p13": 0, "p24": 0},LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [10,10,8,8,7,7]],
    "Explainer Figure_1": [{
        EXPRESSION: "((p1 ^[p0] p2), (p6 /[p5] p7), ((p16, (p28 /[p21] p29),(p35 /[p33] p36)) || (p19, p26 ^[p15] p20, p27) || (p13, (p22 ^[p17] p23) ^[p11] p14, (p24 ^ [p18] p25) )) )",
        H: 0,
        IMPACTS: {"p1": [2, 1, 0, 0, 0, 0], "p2": [1, 2, 0, 0, 0, 0], "p6": [1, 2, 0, 0, 0, 0], "p7": [2, 1, 0, 0, 0, 0], "p16": [0, 0, 0, 0, 0, 0],
                  "p35": [0, 0, 8, 0, 0, 0], "p36": [0, 0, 0, 8, 0, 0], "p28": [0, 0, 0, 0, 5, 0], "p29": [0, 0, 0, 0, 0, 5], "p19": [0, 0, 0, 0, 0, 0],
                  "p20": [0, 0, 0, 0, 0, 0], "p24": [0, 0, 0, 0, 8, 1], "p25": [0, 0, 0, 0, 1, 8], "p22": [0, 0, 0, 0, 8, 1], "p23": [0, 0, 0, 0, 1, 8],
                  "p13": [0, 0, 0, 0, 0, 0], "p14": [0, 0, 0, 0, 0, 0], "p26": [0, 0, 8, 0, 0, 0], "p27": [0, 0, 0, 8, 0, 0]},
        DURATIONS: {"p1": [0, 1], "p2": [0, 1], "p6": [0, 1], "p7": [0, 1], "p16": [0, 1], "p28": [0, 1],
                    "p29": [0, 1], "p35": [0, 1], "p36": [0, 1], "p19": [0, 3], "p20": [0, 3], "p24": [0, 1],
                    "p25": [0, 1], "p22": [0, 1], "p23": [0, 1], "p13": [0, 1], "p14": [0, 1], "p26": [0, 1], "p27": [0, 1],
                    },
        IMPACTS_NAMES: ["A", "B", "C", "D", "E", "F"],
        PROBABILITIES: {"p0": 0.5, "p11": 0.5, "p15": 0.5, "p17": 0.99, "p18":0.01},
        DELAYS: {"p5": 0, "p21": 0, "p33": 0}, LOOP_PROBABILITY : {}, LOOP_ROUND: {}
    }, [3.5, 3.5,11, 12, 9.5, 9.5]], #[3,3,8,8,7,7]
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PACO solver on built-in examples.")
    parser.add_argument("--suite", choices=["examples", "paper"], default="examples", help="Example suite.")
    parser.add_argument("--index", type=int, default=0, help="Index of the example in the suite.")
    args = parser.parse_args()

    if args.suite == "paper":
        run_calc_strategy_paco(bpmn_paper_example, args.index)
    else:
        run_calc_strategy_paco(bpmn_ex, args.index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


