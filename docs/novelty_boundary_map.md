# Novelty Boundary Map

## Not Novel

- Reward-free exploration.
- Hindsight relabeling.
- Dense shaping.
- Temporal-difference credit propagation.
- Generic predictive world-model losses.

## Plausible Contribution

Use embodied effect events as the credit carrier and evaluate temporal localization against those events.

## V2 Boundary

The contribution survives only if event traces are auditable. Misbound or adversarial traces make the method worse than dense shaping.
