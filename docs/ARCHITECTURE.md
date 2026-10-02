# EDE architecture

EDE is an evidence-aware analytical and simulation platform.

## Core path
1. Ingest event evidence.
2. Reconstruct observed trajectories.
3. Discover the observed process/system graph.
4. State the intervention as a fixed objective.
5. Generate alternative implementation topologies.
6. Estimate actor × dimension burden with explicit source type and interval.
7. Compare designs to a declared baseline.
8. Replay scenarios and trace the model mechanism.
9. Simulate capacity, queues, rework and shocks.
10. Test robustness and accept pilot observations for calibration/validation.

## Evidence rule
Observed events, externally declared values, expert assumptions, analogue observations and pilot observations are different evidence roles. Counterfactual outputs are never relabelled as observations.

## Burden vector
The current dimensions are actions, handling minutes, rework, waiting minutes, financial cost, cognitive load, uncertainty minutes and temporal span days.

## Novel computational object
The key product operation is implementation-incidence analysis: given an observed system and a fixed objective, search feasible implementation topologies and estimate how work and pressure move across actors under alternative designs.

## Boundaries
Long gaps and undeclared actors are surfaced as boundary candidates. EDE does not invent hidden actors from absence of evidence.
