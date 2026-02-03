# BPMN+CPI Process Design Template

## Overview
This template helps you design complex business processes using **BPMN+CPI** (Business Process Model and Notation with Choice, Probability, and Impact). Use this template to systematically define your process structure, tasks, decision points, and resource impacts.

---

## 0. LLM Instruction: How to Parse Natural Language Descriptions

**When a user provides a high-level process description, systematically extract the following:**

### Step 1: Identify All Tasks
Look for action words, activities, or work items:
- Keywords: "do", "execute", "perform", "make", "create", "check", "process", "handle"
- Examples: "cutting material", "quality check", "send invoice", "pack items"
- Extract: Task names (use descriptive names from user's language)

### Step 2: Identify Flow Patterns
Determine how tasks relate to each other:

**Sequential**: Look for temporal indicators
- Keywords: "then", "after", "followed by", "next", "before", "first", "finally"
- Pattern: `Task1, Task2, Task3`
- Example: "First cut, then drill" → `Cutting, Drilling`

**Parallel**: Look for simultaneity indicators  
- Keywords: "simultaneously", "at the same time", "both", "in parallel", "together", "all at once"
- Pattern: `(Task1 || Task2 || Task3)`
- Example: "Both quality check and documentation happen together" → `(QualityCheck || Documentation)`

**Choice** (Strategic Decision): Look for decision points under your control
- Keywords: "choose", "decide", "option", "select", "either...or", "alternative"
- Pattern: `(TaskA /[C#] TaskB)`
- Example: "We can choose between fast expensive method or slow cheap method" → `(FastExpensive /[C1] SlowCheap)`

**Nature** (Probabilistic): Look for uncertain outcomes beyond control
- Keywords: "might", "probability", "chance", "sometimes", "if it fails", "randomly", "based on conditions"
- Pattern: `(TaskA ^[N#] TaskB)`
- Example: "80% chance of passing quality check, 20% failure" → `(Pass ^[N1] Fail)` with probability 0.8

**Loop**: Look for repetition with exit conditions
- Keywords: "repeat", "retry", "until", "keep doing", "loop"
- Pattern: `<[L#] TaskBody>`
- Example: "Retry connection until successful" → `<[L1] RetryConnection>`

### Step 3: Extract Task Details

**For each identified task, extract:**

**Impacts**: Look for resource consumption
- Keywords: "costs", "takes time", "uses energy", "requires workers", "emissions", "consumes"
- Numbers with units: "$50", "2 hours", "10 kWh", "3 worker-hours"
- Default: If not specified, use 0.0 for each impact category

**Durations**: Look for time windows
- Keywords: "takes between X and Y time", "minimum duration", "maximum duration", "can take up to"
- Pattern: `[min, max]`
- Example: "takes 1 to 5 hours" → `[1, 5]`
- Default: `[0, 1]` for instant tasks, `[1, 100]` for undefined durations

### Step 4: Extract Gateway Details

**For Choices**, extract:
- Delay: "takes X time to decide", "decision delay"
- Default: 0 if not specified

**For Natures**, extract:
- Probability: "X% chance", "probability of X", "happens with probability X"
- Convert to 0-1 range: 80% → 0.8
- Default: 0.5 (50/50) if not specified

**For Loops**, extract: (but its not yet supported)
- Exit probability: "X% chance to exit", "succeeds with probability X"
- Max rounds: "try up to N times", "maximum N iterations"
- Defaults: exit_probability=0.3, max_rounds=10


### Step 5: Identify Impact Categories

Look for types of resources mentioned:
- **Cost**: "$", "dollars", "budget", "expense", "price"
- **Time**: "hours", "minutes", "days", "duration"
- **Energy**: "kWh", "electricity", "power consumption"
- **Emissions**: "CO2", "carbon", "emissions", "pollution"
- **Workers**: "staff", "employees", "person-hours", "labor"

If user mentions specific impacts, use those names. Otherwise, default to ["cost", "time"].

### Step 6: Build the Expression

Follow operator precedence and nesting rules:
1. Group parallel sections in parentheses: `((A || B), C)`
2. Group choice/nature branches in parentheses: `(A /[C1] (B, C))`
3. Sequential has lowest precedence: just comma-separate
4. Ensure SESE: single entry, single exit (except for gateways)

### Step 7: Validation Before Output

Before generating the final dictionary, check:
- ✓ All tasks in expression exist in impacts dict
- ✓ All tasks in expression exist in durations dict
- ✓ All choice IDs [C#] exist in delays dict
- ✓ All nature IDs [N#] exist in probabilities dict
- ✓ All loop IDs [L#] exist in loop_probability and loop_round dicts
- ✓ All impact values are ≥ 0
- ✓ All durations are [min, max] with min ≤ max
- ✓ All probabilities are between 0 and 1
- ✓ Expression syntax is valid (balanced parentheses)

### Examples of Parsing

**User Input:** "First we cut the material, then we can choose between polishing or painting, finally we ship"

**Parsing Steps:**
1. Tasks: Cutting, Polishing, Painting, Shipping
2. Flow: Sequential → Choice → Sequential
3. Expression: `Cutting, (Polishing /[C1] Painting), Shipping`
4. Choice C1: no delay specified → delay = 0
5. Impacts: not specified → default to 0.0
6. Durations: not specified → use [0, 1]

**User Input:** "We do quality check and documentation in parallel. There's 90% chance QC passes, otherwise we rework"

**Parsing Steps:**
1. Tasks: QualityCheck, Documentation, Pass, Rework
2. Flow: Parallel (QC, Doc) then Nature (Pass vs Rework)
3. Expression: `(QualityCheck || Documentation), (Pass ^[N1] Rework)`
4. Nature N1: 90% chance → probability = 0.9
5. Continue parsing for impacts and durations...

---

## 1. Process Information

### Process Name
**Name:** _[e.g., Manufacturing Workflow, Order Processing, etc.]_

### Process Description
_Provide a high-level description of what this process accomplishes:_

```
[Describe the overall goal and flow of your process]
```

### Impact Categories
_Define what resources or metrics you want to track (e.g., cost, time, energy, CO2 emissions, worker hours):_

- Impact 1: **____________** (unit: ______)
- Impact 2: **____________** (unit: ______)
- Impact 3: **____________** (unit: ______)

---

## 2. Expression Definition

### Process Expression
The expression defines the control flow structure using BPMN+CPI syntax.

**Syntax Guide:**
- `,` = Sequential execution (A then B)
- `||` = Parallel execution (A and B simultaneously)
- `/[C#]` = Choice gateway (strategic decision between alternatives)
- `^[N#]` = Nature gateway (probabilistic branching)
- `@[L#]` = Loop with probabilistic exit
- `()` = Grouping operations

**Your Expression:**
```
expression = ""
```

**Expression Explanation:**
_Describe the flow in natural language:_

```
[Example: "First we execute Cutting, then in parallel we do (Bending followed by 
a nature split between HighPrecision and LowPrecision) alongside (Milling followed 
by a choice between FastDrill and RegularDrill), finally we make a choice between 
HighPowerHighSpeed and LowPowerLowSpeed finishing"]
```

---

## 3. Task Definitions

For each task in your expression, define its impacts and duration.

### Task Template
```
Task Name: _______________
Description: _____________________________________________
Impacts: [impact_1, impact_2, impact_3, ...]
Duration Range: [min_time, max_time]
```

### Your Tasks

#### Task 1: `_________`
- **Description:** ___________________________________
- **Impacts:** `[__, __, __]`  ← _[cost, hours, energy, etc.]_
- **Duration:** `[__, __]`  ← _[minimum time, maximum time in time units]_
- **Notes:** ___________________________________________

#### Task 2: `_________`
- **Description:** ___________________________________
- **Impacts:** `[__, __, __]`
- **Duration:** `[__, __]`
- **Notes:** ___________________________________________

#### Task 3: `_________`
- **Description:** ___________________________________
- **Impacts:** `[__, __, __]`
- **Duration:** `[__, __]`
- **Notes:** ___________________________________________

_[Add more tasks as needed]_

---

## 4. Choice Points (Strategic Decisions)

Choices represent decision points where a **strategy can be selected** to minimize impacts.

### Choice Template
```
Choice ID: C#
Description: _____________________________________________
Left Branch: _________ (Task or sub-expression)
Right Branch: _________ (Task or sub-expression)
Delay: __ (time to make decision)
Strategy Context: ____________________________________
```

### Your Choices

#### Choice C1: `_________`
- **Decision Question:** _"Should we _____ or _____?"_
- **Left Branch:** `_________`  ← _[Higher cost/faster option]_
- **Right Branch:** `_________`  ← _[Lower cost/slower option]_
- **Delay:** `__`  ← _[time units to decide]_
- **When to use Left:** ___________________________
- **When to use Right:** __________________________

#### Choice C2: `_________`
- **Decision Question:** _"Should we _____ or _____?"_
- **Left Branch:** `_________`
- **Right Branch:** `_________`
- **Delay:** `__`
- **Notes:** _______________________________________

_[Add more choices as needed]_

---

## 5. Nature Points (Probabilistic Events)

Nature points represent **probabilistic branching** beyond your control (e.g., machine failure, weather, customer behavior).

### Nature Template
```
Nature ID: N#
Description: _____________________________________________
Left Branch: _________ (Task or sub-expression)
Right Branch: _________ (Task or sub-expression)
Probability (Left): ___% (probability of left branch occurring)
```

### Your Natures

#### Nature N1: `_________`
- **Event Description:** _"What probabilistic event occurs?"_
- **Left Branch:** `_________`  ← _[e.g., Success scenario]_
- **Right Branch:** `_________`  ← _[e.g., Failure scenario]_
- **Probability (Left):** `____` ← _[value between 0 and 1, e.g., 0.8 = 80%]_
- **Real-world Meaning:** ___________________________
  - _Example: "80% chance of high-quality material, 20% chance of standard quality"_

#### Nature N2: `_________`
- **Event Description:** _________________________________
- **Left Branch:** `_________`
- **Right Branch:** `_________`
- **Probability (Left):** `____`
- **Notes:** _______________________________________

_[Add more natures as needed]_

---

## 6. Loops (Optional)

Loops allow repeating sections with probabilistic exit conditions.

### Loop Template
```
Loop ID: L#
Description: _____________________________________________
Loop Body: _________ (expression that repeats)
Exit Probability: ___% (probability of exiting per iteration)
Max Rounds: __ (optional bound on iterations)
```

### Your Loops

#### Loop L1: `_________`
- **Loop Purpose:** _"Why does this repeat?"_
- **Body:** `_________`  ← _[Tasks that repeat]_
- **Exit Probability:** `____` ← _[probability to exit after each iteration]_
- **Max Rounds:** `__`  ← _[maximum iterations allowed]_
- **Example:** _______________________________________

_[Add more loops as needed]_

---

## 7. Bound Constraints

Define the **maximum allowed impacts** (resource budgets) that feasible strategies must respect.

### Bound Vector
```
bound = [max_impact_1, max_impact_2, max_impact_3, ...]
```

**Your Bounds:**
- **Impact 1 (_________):** Maximum = `____` [units]
- **Impact 2 (_________):** Maximum = `____` [units]
- **Impact 3 (_________):** Maximum = `____` [units]

**Constraint Rationale:**
_Why these bounds? (budget limits, regulations, physical constraints, etc.)_

```
[Example: "We have a budget of $1000 and maximum 40 working hours available"]
```

---

## 8. Complete BPMN+CPI Dictionary

Once you've filled out all sections above, compile into the standard format:

```python
from src.utils.env import EXPRESSION, IMPACTS, DURATIONS, IMPACTS_NAMES, PROBABILITIES, DELAYS, LOOP_PROBABILITY, LOOP_ROUND, H

bpmn = {
    EXPRESSION: "",  # Your expression from Section 2
    
    H: 0,  # Horizon parameter (usually 0)
    
    IMPACTS_NAMES: [],  # List from Section 1: ["cost", "hours", "energy", ...]
    
    IMPACTS: {
        # From Section 3:
        # "TaskName": [impact1, impact2, ...],
    },
    
    DURATIONS: {
        # From Section 3:
        # "TaskName": [min_time, max_time],
    },
    
    DELAYS: {
        # From Section 4:
        # "C1": delay_value,
    },
    
    PROBABILITIES: {
        # From Section 5:
        # "N1": probability_value,  # between 0 and 1
    },
    
    LOOP_PROBABILITY: {
        # From Section 6:
        # "L1": exit_probability,
    },
    
    LOOP_ROUND: {
        # From Section 6:
        # "L1": max_rounds,
    }
}

# Bound vector from Section 7
bound = []  # [max_impact1, max_impact2, ...]
```

---

## 9. Validation Checklist

Before running your process through PACO/RESPISE, verify:

- [ ] **Expression Syntax:** All parentheses balanced, operators correctly used
- [ ] **All Tasks Defined:** Every task in expression has impacts and duration
- [ ] **All Choices Defined:** Every choice ID has a delay value
- [ ] **All Natures Defined:** Every nature ID has a probability (0 < p < 1)
- [ ] **Impact Dimensions:** All tasks have same number of impacts matching `IMPACTS_NAMES`
- [ ] **Positive Values:** All impacts, durations, and delays are non-negative
- [ ] **Bound Vector:** Length matches `IMPACTS_NAMES`

---

## 10. Expected Outcomes

### Strategy Synthesis Goal
_What strategic decisions are you trying to optimize?_

```
[Example: "Find a strategy that minimizes expected cost while staying under 
the 40-hour time budget and handling probabilistic quality variations"]
```

### Key Questions
1. **Is there a feasible strategy?** _Can we complete the process within bounds?_
2. **What choices should we make?** _Which decisions at each choice point?_
3. **Expected impacts?** _What are the anticipated resource consumptions?_
4. **Guaranteed bounds?** _What are the worst-case scenarios?_

### Success Criteria
_How will you know if the synthesized strategy is good enough?_

```
[Define thresholds or acceptance criteria]
```

---

## 11. Process Visualization

After defining your BPMN+CPI, you can visualize:

1. **BPMN Diagram:** Shows tasks, gateways, and flow
2. **Parse Tree (Region Tree):** Hierarchical structure
3. **Execution Tree:** All possible execution paths
4. **Strategy Explanation:** Labeled choices showing decisions

_[Insert or reference generated visualizations here]_

---

## 12. Design Notes & Refinement

### Design Decisions
_Document why you structured the process this way:_

```
[Example: "We placed the quality check (Nature N1) before the choice C1 because 
the material quality affects which drilling method is feasible"]
```

### Assumptions
- _Assumption 1:_ ___________________________________
- _Assumption 2:_ ___________________________________
- _Assumption 3:_ ___________________________________

### Alternative Designs Considered
_What other process structures did you consider?_

```
[Document alternatives and why you chose this design]
```

### Iteration History
| Version | Date | Changes | Reason |
|---------|------|---------|--------|
| v1.0    |      | Initial | First draft |
| v1.1    |      |         |        |

---

## 13. Testing & Validation

### Test Scenarios

#### Scenario 1: _____________
- **Description:** ___________________________________
- **Expected Bound:** `[__, __, __]`
- **Expected Outcome:** _____________________________
- **Test Result:** ☐ Pass ☐ Fail
- **Notes:** ________________________________________

#### Scenario 2: _____________
- **Description:** ___________________________________
- **Expected Bound:** `[__, __, __]`
- **Expected Outcome:** _____________________________
- **Test Result:** ☐ Pass ☐ Fail
- **Notes:** ________________________________________

### Edge Cases to Test
- [ ] Minimum bound (infeasible)
- [ ] Maximum bound (trivial - any strategy works)
- [ ] Balanced tradeoffs
- [ ] Worst-case probabilistic outcomes

---

## 14. Implementation Details

### Code Integration
```python
# Import and setup
from src.paco.solver import paco
import numpy as np

# Your BPMN definition (from Section 8)
bpmn = { ... }
bound = np.array([...])

# Run solver
result_text, result_dict, times = paco(bpmn, bound)

# Extract strategy
if "strategy_tree" in result_dict:
    strategy = result_dict["strategy_tree"]
    expected_impacts = result_dict["strategy_expected_impacts"]
    print(f"Expected impacts: {expected_impacts}")
```

### API Usage (if applicable)
```python
# If using the GUI or API
import requests

url = "http://localhost:8050/"
resp = requests.get(f'{url}solve', json={'bpmn': bpmn, 'bound': bound.tolist()})
```

---

## 15. References & Resources

### Related Files
- Full example: `example_fig8.ipynb`
- Tutorial: `tutorial.ipynb`
- Documentation: `docs/installation_and_usage.md`

### External References
- BPMN Specification: ___________________________
- Research Paper: ______________________________
- Domain Standards: ____________________________

---

## Appendix: Quick Reference

### Expression Operators
| Operator | Meaning | Example | Description |
|----------|---------|---------|-------------|
| `,` | Sequential | `A, B` | Execute A then B |
| `\|\|` | Parallel | `A \|\| B` | Execute A and B concurrently |
| `/[C#]` | Choice | `A /[C1] B` | Strategic choice between A or B |
| `^[N#]` | Nature | `A ^[N1] B` | Probabilistic branch: A (p) or B (1-p) |
| `@[L#]` | Loop | `A @[L1]` | Repeat A with probabilistic exit |
| `()` | Grouping | `(A, B) \|\| C` | Group operations for precedence |

### Common Patterns

#### Sequential Tasks
```
"T1, T2, T3"  → Execute T1, then T2, then T3
```

#### Parallel Tasks
```
"T1 || T2 || T3"  → Execute all three simultaneously
```

#### Choice with Fallback
```
"(ExpensiveFast /[C1] CheapSlow)"  → Strategic decision
```

#### Nature with Contingency
```
"(Success ^[N1] Failure), Recovery"  → Handle probabilistic outcome
```

#### Complex Manufacturing Flow
```
"Prep, ((QualityCheck, (HighPrec ^[N1] LowPrec)) || (Cutting, (Fast /[C1] Slow))), Finish"
```

---

## Template Usage Tips

1. **Start Simple:** Begin with a linear flow, then add complexity
2. **Validate Incrementally:** Test each section as you add it
3. **Document Assumptions:** Capture why you made each design choice
4. **Iterate:** Refine based on solver results and feedback
5. **Collaborate:** Share this template with domain experts for review

---

