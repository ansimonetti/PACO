# RESPISE
![Build Status](https://github.com/danielamadori/PACO/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/github/license/danielamadori/PACO)
![Docker Pulls](https://img.shields.io/docker/pulls/danielamadori/paco)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/danielamadori/PACO)
![GitHub issues](https://img.shields.io/github/issues/danielamadori/PACO)
![GitHub pull requests](https://img.shields.io/github/issues-pr/danielamadori/PACO)
![GitHub contributors](https://img.shields.io/github/contributors/danielamadori/PACO)


## Strategy finder for *BPMN + CPI*

## Features

- Models complex business processes with probabilistic decision points
- Provides a strategy synthesis algorithm for BPMN+CPI diagrams
- Web-based interface using Dash for visualizations

## Description

In the context of increasingly complex business processes, accurately modeling decision points, their probabilities, and resource utilization is essential for optimizing operations. To tackle this challenge, we propose an extension to the Business Process Model and Notation (BPMN) called BPMN+CPI. This extension incorporates choices, probabilities, and impacts, emphasizing precise control in business process management. Our approach introduces a timeline-based semantics for BPMN+CPI, allowing for the analysis of process flows and decision points over time. Notably, we assume that all costs, energies, and resources are positive and exhibit additive characteristics, leading to favorable computational properties. Real-world examples demonstrate the role of probabilistic decision models in resource management.

### Solver
RESPISE is an algorithm that given a *BPMN + CPI*  diagram and a bound impact vector can determine if there exists a feasible strategy such that the process can be completed while remaining under the bound vector. Moreover, We explain the synthesized strategies to users by labeling choice gateways in the BPMN diagram, making the strategies more interpretable and actionable.
![alt text](image.png)

### Usage
To set up the project (install dependencies or build Docker image), you can use the automated scripts:

- **Linux/macOS**: `./run.sh` (use `--docker` for Docker mode)
- **Windows**: `.\run.bat` (use `--docker` for Docker mode)

Please refer to the [Installation and Usage Documentation](docs/installation_and_usage.md) for detailed instructions and all available options.


## Contributing

If you want to contribute to RESPISE, you can create your own branch and start programming.

## License

Licensed under MIT license.
