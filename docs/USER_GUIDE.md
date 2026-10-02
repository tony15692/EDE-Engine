# EDE user guide

## Start
Run `python run.py --port 8899` and open http://127.0.0.1:8899/.

## Main workflow
**Dashboard** shows the current event population and evidence readiness.
**Observe** searches the event stream.
**Discover** infers the observed activity graph, path variants, loops and bottleneck candidates.
**Design Lab** generates 156 alternative topologies from the six-actor design model.
**Replay** inserts the counterfactual requirement into an observed case; inserted events are marked scenario-only.
**Simulate** tests capacity, queue, rework and shocks.
**Evidence** shows readiness, boundaries and the real-data benchmark record.
**Pilot** stores post-intervention observations for calibration and validation.

## CLI
`python ede_cli.py status`
`python ede_cli.py import data/demo_caseflow.csv`
`python ede_cli.py report --unit A0001`
`python ede_cli.py export-events exports/events.csv`
`python -m unittest discover -s tests -v`

## Evidence boundary
The public demo is for mechanism demonstration. Real counterfactual calibration requires observed pilot data from a matching implementation.
