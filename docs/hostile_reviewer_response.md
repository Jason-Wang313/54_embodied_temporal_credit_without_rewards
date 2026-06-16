# Hostile Reviewer Response

The strongest reviewer objection to the old paper was correct: raw effect traces fail when events are misbound or adversarial, and dense shaping can be safer in those regimes.

The final v3 paper answers that objection by:

- preserving the v2 event-reliability failure as a negative control,
- adding event coverage, false-event rate, binding accuracy, fallback, abstention, and miscredit metrics,
- evaluating 8 protocols across 518,400 compact rows,
- showing that event-audited trace credit is best non-oracle while oracle remains best,
- stating that real robot logs remain future work.

The final claim is narrower and stronger: physical traces can carry reward-free temporal credit only when event quality is audited.
