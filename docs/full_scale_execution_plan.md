# Paper54 Full-Scale Execution Plan

## Current State

Paper54 is currently a workshop-only mechanism note. The old positive claim is that physical effect traces can assign temporal credit before scalar rewards are available. V1 supports this under usable traces: effect-trace credit has localization error 0.862, versus 3.550 for delayed-reward TD and 2.342 for dense shaping. V2 hardening exposes the missing condition: raw effect traces win under reliable and partially missed events, but lose when event bindings are wrong or adversarial.

The final version must not claim that raw effect traces are universally better than rewards or dense shaping. The stronger submission-grade claim should be:

> Event-audited embodied temporal credit can use physical effect traces before rewards, but only when event coverage, false-event rate, and action-event binding are measured and used to gate or fall back.

## Target Title

Event-Audited Embodied Temporal Credit Without Rewards

## Claim Boundary

- Claim: audited trace credit is the best non-oracle protocol in a large deterministic benchmark when evaluated across event reliability, temporal horizon, sensor channel, proxy conflict, and task-family stress.
- Claim: raw effect trace remains a useful but unsafe baseline; it should fail under misbound and adversarial events.
- Claim: dense shaping remains a strong fallback when event traces are unreliable.
- Claim: reward-free credit is not a deployment proof and not a universal replacement for reinforcement learning.
- Do not claim: real robot validation, safety certification, or superiority when event binding is unaudited.

## Full-Scale Experiment Design

Factor axes:

- 12 embodied task families:
  - block push with delayed displacement
  - door latch release
  - drawer opening
  - peg insertion with delayed seating
  - cable routing
  - cloth unfolding
  - tool use with delayed object motion
  - bimanual handoff
  - stacking with support creation
  - button press with delayed mechanism response
  - pouring with delayed flow onset
  - recovery after failed contact
- 6 event channels:
  - visual object displacement
  - contact onset or loss
  - force impulse
  - constraint release
  - support-graph edit
  - multimodal fused event
- 6 temporal horizon regimes:
  - 1-2 step immediate effects
  - 3-5 step short delay
  - 6-10 step medium delay
  - 11-16 step long delay
  - variable multi-event horizon
  - delayed decoy before true event
- 6 event reliability regimes:
  - reliable events
  - partially missed events
  - high false-event rate
  - action-event misbinding
  - adversarial event injection
  - low-coverage but high-precision events
- 5 proxy/reward regimes:
  - no reward available
  - delayed sparse reward
  - aligned dense shaping
  - deceptive dense shaping
  - conflicting human success label
- 5 sensor/binding regimes:
  - synchronized multimodal logs
  - delayed tactile stream
  - partial observability
  - actuator-latency confound
  - cross-object distractor motion
- 8 credit protocols:
  - delayed reward TD
  - dense shaping proxy
  - hindsight relabel credit
  - inverse-dynamics credit
  - raw effect trace
  - coverage-weighted effect trace
  - event-audited trace credit
  - oracle causal event credit

Scale:

- Compact rows: 12 * 6 * 6 * 6 * 5 * 5 * 8 = 518400.
- Each compact row represents 19 seeds, 7 scene instances, 5 action motifs, 4 detector calibrations, 4 confounder replicas, 32 trials, and 96 control timesteps.
- Represented evaluations per row: 340480.
- Represented frame decisions per row: 32686080.
- Represented evaluations total: 176504832000.
- Represented frame decisions total: 16944463872000.

## Metrics

- Temporal localization error.
- Counterfactual precision.
- Success lift.
- Reward dependence.
- Event coverage.
- Binding accuracy.
- False-event rate.
- Miscredit risk.
- Fallback rate.
- Trace abstention rate.
- Proxy-conflict regret.
- Credit utility.

Utility must penalize localization error, low precision, false binding confidence, high miscredit risk, and hidden reward dependence. It must reward high precision, low reward dependence, and correct fallback under bad event reliability.

## Baseline And Ablation Requirements

- Delayed reward TD tests whether scalar reward propagation is sufficient.
- Dense shaping tests whether hand-shaped proxy progress is enough.
- Hindsight relabel credit tests whether goal relabeling explains the result.
- Inverse-dynamics credit tests whether local action prediction explains the result.
- Raw effect trace preserves the v1 method and must fail under misbinding/adversarial regimes.
- Coverage-weighted trace tests whether event coverage alone solves the v2 failure.
- Event-audited trace credit is the proposed method and must combine coverage, false-event, and binding audits.
- Oracle causal event credit is the upper bound and must remain best overall.

## Expected Result Shape

- Oracle should be best overall.
- Event-audited trace credit should be the best non-oracle method by aggregate utility.
- Raw effect trace should win or remain strong under reliable events but degrade under misbound/adversarial events.
- Dense shaping should remain competitive under aligned shaping and bad event reliability.
- Coverage-weighted trace should help missed-event regimes but should not fully solve misbinding.
- Hindsight and inverse-dynamics baselines should help some delayed tasks but should be weaker under proxy conflict and distractor events.
- The final paper should emphasize conditional credit assignment, not reward-free triumphalism.

## Figures And Tables

- Scale table.
- Aggregate protocol table.
- Event-reliability stress table.
- Horizon stress table.
- Proxy/reward stress table.
- Sensor/binding stress table.
- Task-family summary table.
- Figure: utility and localization error by protocol.
- Figure: reliability frontier showing when raw trace flips from helpful to harmful.
- Figure: binding accuracy versus miscredit risk.
- Figure: fallback/abstention by reliability regime.

## Writing Expansion Plan

The final manuscript must be at least 25 pages and the length must come from content:

- Preserve the v2 failure in the main text.
- Reframe the contribution as event-audited trace credit.
- Add full benchmark design and factor rationale.
- Add protocol definitions and equations.
- Add result sections for aggregate, reliability, horizon, proxy, sensor/binding, and task stress.
- Add case studies for reliable trace, missed trace, misbound trace, adversarial event, and deceptive dense shaping.
- Add appendix sections for metric semantics, artifact map, RAM-light execution, reviewer attacks, claim-language guardrails, real-robot extension, and falsification criteria.

## RAM-Light Execution Strategy

- Stream compact rows directly to `results/full_scale/condition_metrics.csv`.
- Store short factor codes in the CSV and human-readable labels in `factor_maps.json`.
- Maintain only summary accumulators in memory.
- Generate small summary CSVs for each factor axis.
- Generate LaTeX tables and PDF figures from summaries, not from the full condition table during manuscript build.
- Keep condition CSV under the 100 MB GitHub hard limit by avoiding repeated long labels and using bounded decimal precision.

## Final Acceptance Checklist

- Detailed plan exists before content edits.
- Full-scale runner completes and writes validation JSON.
- Compact row count is exactly 518400.
- Represented evaluation and frame counts match the design.
- Event-audited trace credit is best non-oracle by utility.
- Oracle remains best overall.
- Raw effect trace visibly fails under misbound/adversarial regimes.
- Dense shaping remains a strong fallback in regimes where event reliability is poor.
- Manuscript is at least 25 pages.
- No canonical PDF is placed in Downloads until the final version is ready.
- Final PDF is `C:/Users/wangz/Downloads/54.pdf`.
- `paper/main.pdf` is removed after build.
- Representative pages are rendered and visually inspected.
- README, status, audit, reproducibility, and readiness docs are updated.
- Git checks pass.
- Commit and push before moving to Paper55.

## Final Outcome

- Status: final v3 full-scale submission artifact.
- Canonical PDF: `C:/Users/wangz/Downloads/54.pdf`.
- Pages: 25.
- PDF size: 349958 bytes.
- SHA256: `2111E596A34169B09585C7875294D0BA1B581D62D47F440207B06F04FF311777`.
- Compact condition rows: 518400.
- Represented evaluations: 176504832000.
- Represented timestep decisions: 16944463872000.
- Visual QA pages: 1, 4, 7, 13, 20, and 25.
