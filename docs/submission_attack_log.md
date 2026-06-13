# Submission Attack Log

## Attack: event-trace reliability is assumed

Result: Sustained. V2 stress shows the method wins only when event traces are reliable or partially missed.

Decision impact: narrow to workshop-only mechanism note.

## Attack: wrong event bindings make trace credit harmful

Result: Sustained. Misbound events raise trace error to 2.679 versus dense shaping 2.438. Adversarial events raise trace error to 4.222 versus dense shaping 2.375.

Decision impact: require event coverage and binding audits.

## Attack: synthetic-only diagnostic cannot support deployment

Result: Sustained. Real manipulation logs remain required.
