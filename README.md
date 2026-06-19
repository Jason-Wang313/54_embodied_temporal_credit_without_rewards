# Event-Audited Embodied Temporal Credit Without Rewards

Paper 54 in the robotics 60-paper batch.

Status: final v3 full-scale submission artifact.

The original claim was that physical effect traces can assign temporal credit before scalar rewards are available. V2 hardening showed the raw trace mechanism is conditional: it wins under reliable and partially missed events, but loses when events are misbound or adversarial. The final v3 paper preserves that failure and rebuilds the claim around event-audited trace credit.

## Final Result

- Canonical PDF: `C:/Users/wangz/Downloads/54.pdf`
- Pages: 25
- PDF size: 349958 bytes
- PDF SHA256: `CFBE8C618E572DFCEE35C2FE129CBD51EF507D9C174B0D876BCD82284AB28122`
- VLA-style highlight hardening: 10 red link boxes on pages 4, 5, and 6, all with border `(0, 0, 1)`.
- Compact condition rows: 518,400
- Represented evaluations: 176,504,832,000
- Represented timestep decisions: 16,944,463,872,000
- Best non-oracle protocol: event-audited trace
- Aggregate utility: event-audited trace 0.758266; oracle 1.000000; raw effect trace 0.171580

The final claim is bounded: physical effect traces can carry reward-free temporal credit when event coverage, false-event rate, and action-event binding are audited. This repo does not claim real robot deployment safety or real-log validation.

## Reproduction

```powershell
python scripts/run_full_scale_temporal_credit_suite.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

The build script copies only the final PDF to `C:/Users/wangz/Downloads/54.pdf` and removes `paper/main.pdf`.
