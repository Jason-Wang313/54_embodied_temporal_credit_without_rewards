# Embodied Temporal Credit Without Rewards

Paper 54 in the robotics 60-paper batch.

This recovery preserves the attempt-two literature sweep and adds a deterministic diagnostic for reward-free temporal credit assignment. The central thesis is that physical effect traces, such as contact changes and object-state transitions, can assign temporal credit before any scalar reward is available.

Key artifacts:

- `docs/related_work_matrix.csv`: 17,754 candidate literature records from the failed runner attempt.
- `docs/temporal_credit_diagnostic.csv`: 2,160 deterministic diagnostic rows.
- `docs/temporal_credit_diagnostic_summary.csv`: aggregate metrics by scenario and method.
- `paper/main.tex` and `paper/main.pdf`: recovered ICLR-style manuscript.

Aggregate result: effect-trace credit reduces mean temporal localization error from 3.550 steps for delayed-reward TD to 0.862 steps while using zero scalar reward dependence.
