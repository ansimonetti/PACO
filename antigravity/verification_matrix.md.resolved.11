# Callback Verification Matrix (Comprehensive)

## 5. Strategy (Optimization)
| ID | User Action | Callback | Status |
|----|-------------|----------|--------|
| 5.1 | **Find Strategy (Standard)**: Click "Find Strategy" | CB19 | ✅ PASSED |
| 5.2 | **Find (Impossible)**: Bound < Min Cost -> Alert | CB19 | ✅ PASSED |
| 5.3 | **Find (Loose/All)**: Bound > Max Cost -> "Any choice" | CB19 | ✅ PASSED |
| 5.4 | **Find (Strict/Subset)**: Min < Bound < Max -> "Found" | CB19 | ✅ PASSED |

## 8. Stress Tests
| ID | User Action | Callback | Status |
|----|-------------|----------|--------|
| 8.1 | **Model Change during Sim**: Modify Expression while T>0 | Sim Reset | ✅ PASSED |
| 8.2 | **View Switch during Sim**: Switch to PetriNet | State Persists | ✅ PASSED |
| 8.3 | **Dynamic Impact**: Add Impact during Sim | Sim Updates | ✅ PASSED |

## 9. Integration Tests (Strategy -> Simulator)
| ID | Scenario | Expected Behavior | Status |
|----|----------|-------------------|--------|
| 9.1 | **Integration Test**: Select Strategy -> Run Sim | Sim displays "Strategy Suggestion" / Enforces Path A | ✅ PASSED |

## 10. Chatbot (Copilot)
| ID | Scenario | Description | Status |
|----|----------|-------------|--------|
| 10.1| **Simple Sequence**: "Task A followed by Task B" | Check BPMN Update (A->B) | ⏳ PENDING |
| 10.2| **Choice**: "Choose between Pizza or Pasta" | Check BPMN Update (Choice Gateway) | ⏳ PENDING |
| 10.3| **Complex Use Case**: "Marine Container Terminal" (Full Text) | Check BPMN Update (Complex Graph) | ⏳ PENDING |
