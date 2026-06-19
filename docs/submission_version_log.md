# Submission Version Log

## v1

- Generated a mechanism paper arguing that physical effect traces can assign temporal credit before reward.
- Reported effect-trace localization error 0.862 versus delayed reward TD 3.550 and dense shaping 2.342.

## v2

- Added event-reliability stress.
- Found that raw effect traces win under reliable/missed events but lose under misbound/adversarial events.
- Reframed the raw-trace mechanism as conditional.

## v3

- Added `scripts/run_full_scale_temporal_credit_suite.py`.
- Generated 518,400 compact condition rows representing 176,504,832,000 evaluations and 16,944,463,872,000 timestep decisions.
- Evaluated 8 protocols across task, event, horizon, reliability, proxy/reward, and sensor/binding factors.
- Rewrote the manuscript as "Event-Audited Embodied Temporal Credit Without Rewards".
- Built the final 25-page canonical PDF at `C:/Users/wangz/Downloads/54.pdf`.
- Final SHA256: `CFBE8C618E572DFCEE35C2FE129CBD51EF507D9C174B0D876BCD82284AB28122`.
- VLA-style highlight hardening verified 10 red link boxes on pages 4, 5, and 6.
