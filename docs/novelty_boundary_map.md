# Novelty Boundary Map

## Not Novel

- Temporal-difference learning.
- Dense reward shaping.
- Hindsight relabeling.
- Inverse dynamics.
- Self-supervised robot world models.
- Generic event detection.

## Historical Collapse

The original raw effect-trace claim was too broad. V2 showed raw traces lose to dense shaping when events are misbound or adversarial.

## Final Novelty Boundary

The final contribution is an event-audited benchmark and protocol for embodied temporal credit without scalar rewards. The paper claims that trace credit is useful when event coverage, false-event rate, and action-event binding are audited and used to gate or fall back.

## Not Claimed

- Real robot log validation.
- Hardware deployment safety.
- Universal superiority over dense shaping.
- Reward-free learning without event labels.
