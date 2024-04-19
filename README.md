# BPMN + DCPI

## Description

As business processes become increasingly complex, effectively modeling decision points, their like-
lihood, and resource consumption is crucial for optimizing operations. To address this challenge, this
paper introduces a formal extension of the Business Process Model and Notation (BPMN) that incor-
porates choices, probabilities, and impacts, referred to as BPMN+CPI. This extension is motivated by
the growing emphasis on precise control within business process management, where carefully select-
ing decision pathways is crucial. We propose a timeline-based semantics approach for BPMN+CPI,
offering a temporal representation that is well-suited for analyzing process flows and decision points
over time. The paper explores the implications of assuming that all costs, energies, and resources
utilized are positive and exhibit additive characteristics and we demonstrate that this restriction con-
tributes to favorable computational properties. Finally, the paper illustrates the role of probabilistic
decision models in resource management through real-world examples. We implemented a tool capa-
ble of determining the existence of a strategy based on a timeline-based encoding of the process and
a specified threshold. This work advances the capabilities of BPMN for enhanced business process
management, empowering better decision-making and resource allocation.

### PACO
PACO is an algorithm that given a *BPMN + CPI*  diagram and a bound impact vector can determine if there exists a feasible strategy such that the process can be completed while remaining under the bound vector.


## Installation

To install PACO, you need to download the folder, install the required python packages.

## Usage

To use PACO, you can  follow these steps:
1. Open a terminal or command prompt window.
2. Navigate to the directory containing the unzipped folder.
3. Run the Python script named "app.py" using the following syntax: 
    ```bash
        python3 .\app.py
    ```
4. Open Chrome (or any othe  browser supporting HTML5) and go to `http://127.0.0.1:8050`.

## AUTORS

* **Chini Emanuele**
* **Sala Pietro**
* **Simonetti Andrea**
* **Zare Omid**

## Contributing

If you want to contribute to PACO, you can create your own branch and start programming.

## License

PACO is licensed under MIT license.