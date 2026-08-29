# Experiments — Sections VI–VII (not started)

Will hold run configurations and result tables for the five systems compared in
the paper: visual-only, structural/semantic with ground-truth text,
structural/semantic with OCR text, hybrid, and the hybrid oracle condition.

Two rules carried over from the dataset work:

* **Calibrate on validation, evaluate on test once.** No fusion threshold or
  coefficient is fitted on test data.
* **Report per document type and per forgery category, never pooled alone.** A
  pooled figure is determined largely by the category proportions chosen in
  Section IV and is a property of the dataset rather than of the method.
