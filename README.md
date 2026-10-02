# EDE — Evidence-aware Dynamics & Design Engine 1.0

A locally runnable full-stack prototype for observing operational systems, reconstructing trajectories, testing counterfactual implementation architectures, measuring actor-level burden incidence, and stress-testing designs.

## What is included
- Browser dashboard with working EDE modules
- CSV, JSON and XES ingestion
- SQLite persistence
- Evidence/provenance/readiness assessment
- Trajectory dynamics and review signals
- Evidence-derived system discovery and graph
- Actor coupling and boundary audit
- Counterfactual estimation modes
- 8-dimensional BurdenFlow
- Structural / analogue / pilot-calibrated / expert / hybrid estimation
- Architecture search and Pareto frontier
- Historical what-if replay
- Mechanism trace
- Dynamic queue / rework / capacity simulation
- Shock testing and robustness sensitivity
- Pilot observation intake and prediction validation
- Real Sepsis benchmark record (results only)
- CLI and Windows/macOS/Linux launchers
- Docker support
- Automated unittest suite

## Requirements
Python 3.10+. The default local application uses the Python standard library and requires no package installation.

## Start
Windows: double-click `START_EDE.bat`.

macOS/Linux:
```bash
chmod +x START_EDE.sh
./START_EDE.sh
```

Manual:
```bash
python run.py --port 8899
```
Open http://127.0.0.1:8899/

## CLI
```bash
python ede_cli.py status
python ede_cli.py import data/demo_caseflow.csv
python ede_cli.py report --unit A0001
python ede_cli.py export-events exports/events.csv
python ede_cli.py test
python -m unittest discover -s tests -v
```

## Data
EDE accepts CSV, JSON and XES with flexible aliases for case/unit, activity, timestamp, actor/resource, state, source and evidence confidence fields.

## Evidence boundary
Synthetic counterfactual values are scenario assumptions until analogue or pilot observations are supplied. The repository includes the verified real-data benchmark result, but not the source hospital data.

## Product flow
`Observe → Discover → Model → Intervene → Search → Replay → Simulate → Stress → Compare → Validate`

## License / status
Working prototype for demonstration and pilot deployment. The counterfactual layer is decision support, not causal inference.
