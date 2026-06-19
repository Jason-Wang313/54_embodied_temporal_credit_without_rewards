# Final Audit

Paper-readiness judgment: final v3 full-scale submission artifact.

## Final Thesis

Physical effect traces can carry reward-free temporal credit when their coverage, false-event rate, and action-event binding are audited. Raw traces are unsafe when events are misbound or adversarial.

## Historical Negative Control

V2 hardening showed the old raw-trace claim was conditional:

- Reliable events: effect trace 1.014 versus dense shaping 2.349.
- Missed events: effect trace 2.243 versus dense shaping 2.405.
- Misbound events: effect trace 2.679 versus dense shaping 2.438.
- Adversarial events: effect trace 4.222 versus dense shaping 2.375.

The final paper keeps this failure and uses it to motivate event-audited trace credit.

## Full-Scale V3 Evidence

- Compact condition rows: 518,400.
- Represented evaluations: 176,504,832,000.
- Represented timestep decisions: 16,944,463,872,000.
- Event-audited trace utility: 0.758266.
- Oracle utility: 1.000000.
- Raw effect trace utility: 0.171580.
- Event-audited trace localization error: 2.772234.
- Event-audited trace precision: 0.608508.
- Event-audited trace reward dependence: 0.014347.
- Event-audited trace miscredit risk: 0.235057.

## Artifact Policy

- Canonical PDF: `C:/Users/wangz/Downloads/54.pdf`.
- Canonical PDF pages: 25.
- Canonical PDF size: 349958 bytes.
- Canonical PDF SHA256: `CFBE8C618E572DFCEE35C2FE129CBD51EF507D9C174B0D876BCD82284AB28122`.
- Local generated PDF policy: `paper/main.pdf` is ignored and removed after build.
- Desktop copy: absent.

## QA

- LaTeX warning scan: clean.
- Visual QA pages: 1, 4, 7, 13, 20, and 25.
- VLA-style highlight hardening: 10 red link boxes on pages 4, 5, and 6, all with border `(0, 0, 1)`.
- Highlight visual QA pages: 4, 5, and 6.
- Title-page spacing was fixed before final hash recording.
