# Experiment Rigor Checklist

- Full-factor benchmark: yes, 12 tasks, 6 event channels, 6 horizons, 6 reliability regimes, 5 proxy/reward regimes, 5 sensor/binding regimes, and 8 protocols.
- RAM-light execution: yes, streamed compact rows and summary accumulators.
- Strong baselines: yes, delayed reward TD, dense shaping, hindsight relabel, inverse dynamics, raw trace, coverage-weighted trace, event-audited trace, and oracle.
- Negative control: yes, v2 misbound/adversarial event failure is preserved.
- Stress tests: reliability, horizon, proxy/reward, sensor/binding, event channel, and task family.
- Multiple represented repetitions: yes, 19 seeds, 7 scene instances, 5 motifs, 4 calibrations, 4 confounders, 32 trials, and 96 timesteps per row.
- Real robot data: no, explicitly stated as future work.
- Decision: final v3 full-scale submission artifact.
