# Embodied Temporal Credit Without Rewards

Paper 54 in the robotics 60-paper batch.

Decision: workshop-only.

The thesis is that physical effect traces can carry temporal credit before scalar rewards are available. The v1 diagnostic supports the mechanism under usable traces: effect-trace credit reduces mean temporal localization error from 3.550 for delayed-reward TD and 2.342 for dense shaping to 0.862.

V2 hardening adds an event-reliability stress:

- Reliable events: effect-trace error 1.014 versus dense shaping 2.349.
- Missed events: effect-trace error 2.243 versus dense shaping 2.405.
- Misbound events: effect-trace error 2.679 versus dense shaping 2.438.
- Adversarial events: effect-trace error 4.222 versus dense shaping 2.375.

The supported claim is therefore conditional: reward-free effect traces are useful only when event coverage and action-event binding are audited.

## Reproduction

```powershell
python scripts/v2_event_reliability_stress.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

The canonical built PDF is `C:/Users/wangz/Downloads/54.pdf`.

Local generated PDFs are not tracked. The build script copies the generated PDF to the canonical Downloads path and removes `paper/main.pdf`.
