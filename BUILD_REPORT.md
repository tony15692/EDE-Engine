# EDE public repository build report

Public repository: https://github.com/tony15692/EDE-Engine

## Stack
Python 3.10+ standard library, SQLite, browser HTML/CSS/JavaScript, Docker.

## Public demo
- 13 demo events across 2 units
- 4 observed actors in the demo data
- 6 actors in the design compiler
- 156 generated architectures

## Quality control
From repository root:

    python -m unittest discover -s tests -v

Expected result for the current commit:

    Ran 7 tests
    OK

The suite checks ingestion, observation, trajectory metrics, discovery, architecture generation, simulation, replay/mechanism trace and JSON ingestion.

## Evidence boundary
The repository contains a verified real Sepsis benchmark result record only; source hospital data are not redistributed. Counterfactual outputs in the demo are scenario assumptions until analogue, expert or pilot evidence is supplied.
