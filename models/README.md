# Models — Section V (not started)

Will hold the visual detection branch and the evidence-fusion code.

Planned, per Section V of the paper:

* **Visual branch** — an ImageNet-pretrained ResNet-50 with a two-unit head,
  trained on C0 versus C1 only. It is a *baseline*, not a contribution: its job
  is to give the incremental-value measurement something credible to be
  incremental to.
* **Fusion** — three transparent rules evaluated in order of complexity:
  disjunctive, conjunctive, and a logistic model that keeps the Aadhaar and PAN
  rule outcomes as separate features so the evidential asymmetry between the two
  formats survives fusion instead of being averaged away.

**Open decision that must be settled before anything is trained.** A C1 edit is
a font substitution or a 5–11 px field displacement on a 1012×638 card. At a
224×224 input that is roughly two pixels. A gradient-boosted probe over
downscaled images already failed to separate C0 from C1 at better than chance
(balanced accuracy 0.491), which is a warning that the resolution, not the
science, may decide RQ1. Resolve it with a higher input resolution or
patch-based inference, and record the choice in `docs/DECISIONS.md`.
