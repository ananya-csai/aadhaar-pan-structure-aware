"""Generate the Section VII tables and figure data from committed results.

Reads experiments/results/analysis/test/analysis.json (Step 16-17 analyses) and
experiments/results/fresh/*_fresh.json, confirmatory.json; writes
paper/generated/res_*.tex. No number in these tables is typed by hand.

    python paper/scripts/make_results_tables.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = json.loads((ROOT / "experiments/results/analysis/test/analysis.json").read_text(encoding="utf-8"))
FRESH = ROOT / "experiments/results/fresh"
OUT = ROOT / "paper/generated"
S = A["systems"]


def f1(x):
    return "--" if x is None else f"{x:.1f}"


def rci(cell, bold=False):
    v = f1(cell["value"])
    v = rf"\textbf{{{v}}}" if bold else v
    return rf"{v} {{\tiny[{cell['ci'][0]:.1f}, {cell['ci'][1]:.1f}]}}"


def sgn(x):
    return f"{x:+.1f}".replace("-", "$-$")


def pfmt(p):
    return r"$<\!10^{-4}$" if p == 0 else (f"{p:.4f}" if p < 0.01 else f"{p:.3f}")


# ---------------------------------------------------------------- main table
rows = [
    ("Single source", None),
    ("Visual (tiles)", "visual", "--", r"$t_v$, 5\%"),
    ("Whole-card CNN", "base", "--", r"own $t$, 5\%"),
    ("Rules", "rules_GT", "GT", "--"),
    ("Rules", "rules_OCR", "OCR", "--"),
    ("Fusion, ground-truth text", None),
    ("OR", "OR_GT", "GT", "inherited"),
    ("AND", "AND_GT", "GT", "inherited"),
    ("A4 logistic", "A4_GT", "GT", r"5\%"),
    ("Fusion, OCR text", None),
    ("OR", "OR_OCR", "OCR", "inherited"),
    ("AND", "AND_OCR", "OCR", "inherited"),
    ("A4 logistic", "A4_OCR", "OCR", r"5\%"),
    ("A4 logistic", "A4_OCR@rules", "OCR", "= Rules-OCR"),
    ("A4 logistic", "A4_OCR@OR", "OCR", "= OR-OCR"),
    (r"Per-check fusion (post-hoc, \S\ref{subsec:res-a5})", None),
    (r"A5 per-check", "A5_OCR", "OCR", r"5\%"),
    (r"A5 per-check", "A5_OCR@rules", "OCR", "= Rules-OCR"),
]
L = [r"\begin{table*}[!t]",
     r"\caption{Detection on the v1 test split (1{,}620 images of 45 people; 540 genuine and 270 per "
     r"forgery category) at the operating points fixed on validation. Recall (all forged images) and FPR "
     r"(genuine images) in \%, with 95\% person-clustered bootstrap intervals. C1--C4: recall per "
     r"category. ``$=$ X'': threshold set on validation to the FPR that system X reaches there. "
     r"A5 with ground-truth text makes the same decisions as A4 and is not listed. "
     r"FNR $=100-{}$Recall; confusion matrices of all systems are released with the results.}",
     r"\label{tab:main}", r"\centering", r"\footnotesize", r"\setlength{\tabcolsep}{4.2pt}",
     r"\renewcommand{\arraystretch}{1.08}",
     r"\begin{tabular}{@{}l l l r r r c r r r r@{}}", r"\toprule",
     r"System & Text & Threshold & \multicolumn{1}{c}{Recall} & \multicolumn{1}{c}{FPR} & Prec. & F1 "
     r"& C1 & C2 & C3 & C4 \\", r"\midrule"]
for r in rows:
    if r[1] is None:
        if L[-1] != r"\midrule":
            L.append(r"\midrule")
        L.append(rf"\multicolumn{{11}}{{@{{}}l}}{{\emph{{{r[0]}}}}} \\")
        continue
    name, key, text, thr = r
    s = S[key]
    L.append(rf"\quad {name} & {text} & {thr} & {rci(s['forged'], key in ('A4_GT', 'A5_OCR'))} & "
             rf"{rci(s['c0'])} & {f1(s['precision'])} & {s['f1']:.3f} & "
             + " & ".join(f1(s[c]["value"]) for c in ("C1", "C2", "C3", "C4")) + r" \\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
(OUT / "res_main.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- RQ1 table
ev = A["E_vis"]
grp = [("All C1", "c1", "c1"), ("Fine-trace", "c1_fine", "c1_fine"),
       (r"\quad recompression", "c1/local_recompression", "c1/local_recompression"),
       (r"\quad resampling", "c1/resample_patch", "c1/resample_patch"),
       ("Coarse", "c1_coarse", "c1_coarse"),
       (r"\quad font substitution", "c1/font_substitution", "c1/font_substitution"),
       (r"\quad field displacement", "c1/field_displacement", "c1/field_displacement"),
       (r"\quad patch splice", "c1/patch_splice", "c1/patch_splice"),
       ("Clean capture", "c1/clean", "c1/clean"), ("Mild capture", "c1/mild", "c1/mild"),
       ("Severe capture", "c1/severe", "c1/severe")]
L = [r"\begin{table}[!t]",
     r"\caption{C1 detection by the tile model and the whole-card CNN on the test split. Recall (\%) at "
     r"each model's frozen threshold (test FPR 4.8\% and 5.2\%), tile model with 95\% interval; AUROC "
     r"against all genuine images, or against the genuine images of the same tier in the tier rows.}",
     r"\label{tab:rq1}", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{2.6pt}",
     r"\renewcommand{\arraystretch}{1.06}",
     r"\begin{tabular}{@{}l r r r c c@{}}", r"\toprule",
     r" & & \multicolumn{2}{c}{Recall} & \multicolumn{2}{c}{AUROC} \\ \cmidrule(lr){3-4}\cmidrule(l){5-6}",
     r"C1 subset & $n$ & Tiles & Whole & Tiles & Whole \\", r"\midrule"]
for i, (lab, rk, ek) in enumerate(grp):
    if i in (8,):
        L.append(r"\midrule")
    n = A["counts"][rk]
    e = ev[ek]
    L.append(rf"{lab} & {n} & {rci(S['visual'][rk])} & {f1(S['base'][rk]['value'])} & "
             rf"{e['visual']['auroc']:.3f} & {e['base']['auroc']:.3f} \\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(OUT / "res_rq1.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- tests table
F = A["families"]
lab = {"1a": r"C1 fine-trace recall: tiles $-$ whole card",
       "1b": r"C1 coarse recall: tiles $-$ whole card",
       "3a": r"A4-GT $-$ visual, 5\% FPR",
       "3b": r"A4-OCR $-$ visual, 5\% FPR",
       "3c": r"A4-OCR $-$ Rules-OCR, matched FPR",
       "3d": r"A4-OCR $-$ OR-OCR, matched FPR",
       "4a": r"A4-GT $-$ A4-OCR, 5\% FPR",
       "4b": r"Rule coverage: GT $-$ OCR",
       "4c": r"Rules FPR: OCR $-$ GT",
       "5a": r"$\Delta_{\mathrm{GT}}$: Aadhaar $-$ PAN",
       "5b": r"$\Delta_{\mathrm{OCR}}$: Aadhaar $-$ PAN",
       "6a": r"Rules-OCR FPR: PAN $-$ Aadhaar",
       "6b": r"Rules-OCR FPR: severe $-$ clean",
       "Pa": r"A5-OCR $-$ A4-OCR, recall",
       "Pb": r"A5-OCR $-$ A4-OCR, FPR"}
fam_name = {"F1 (RQ1, E-vis)": "RQ1", "F3 (RQ3)": "RQ3", "F4 (RQ4)": "RQ4", "F5 (RQ5)": "RQ5",
            "F6 (RQ6)": "RQ6"}
L = [r"\begin{table}[!t]",
     r"\caption{Paired comparisons on the test split (percentage points). 95\% person-clustered "
     r"bootstrap intervals ($B=10{,}000$); $p$ Holm-adjusted within each family. "
     r"Recall unless stated. $p<10^{-4}$: no replicate crossed zero. Post-hoc rows are not corrected "
     r"and not confirmatory.}",
     r"\label{tab:tests}", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{2.8pt}",
     r"\renewcommand{\arraystretch}{1.06}",
     r"\begin{tabular}{@{}l l r c r@{}}", r"\toprule",
     r"Fam. & Comparison & Diff. & 95\% CI & $p_{\mathrm{Holm}}$ \\", r"\midrule"]
first = True
for fam, rws in F.items():
    if not first:
        L.append(r"\addlinespace[1.5pt]")
    first = False
    for k, x in enumerate(rws):
        L.append(rf"{fam_name[fam] if k == 0 else ''} & {lab[x['id']]} & {sgn(x['diff'])} & "
                 rf"[{sgn(x['ci'][0])}, {sgn(x['ci'][1])}] & {pfmt(x['p_holm'])} \\")
L.append(r"\midrule")
for k, x in enumerate([p for p in A["posthoc_A5"] if p["id"] in ("Pa", "Pb")]):
    L.append(rf"{'Post-hoc' if k == 0 else ''} & {lab[x['id']]} & {sgn(x['diff'])} & "
             rf"[{sgn(x['ci'][0])}, {sgn(x['ci'][1])}] & ({pfmt(x['p'])}) \\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(OUT / "res_tests.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- RQ4/RQ6 table
E6, E8 = A["E6"], A["E8"]
L = [r"\begin{table}[!t]",
     r"\caption{Genuine (C0) test images by document type and capture tier ($n=90$ each). "
     r"OCR-induced: rule verdict PASS on ground-truth text but FAIL on OCR text; this equals the "
     r"Rules-OCR FPR, since the rules never fail on ground-truth text. FPR (\%) of the systems that "
     r"read OCR text, and of the visual branch.}",
     r"\label{tab:rq46}", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{3pt}",
     r"\renewcommand{\arraystretch}{1.06}",
     r"\begin{tabular}{@{}l l r r r r r@{}}", r"\toprule",
     r"Doc. & Tier & OCR-ind. & Rules-OCR [95\% CI] & A4-OCR & A5-OCR & Visual \\", r"\midrule"]
for d, dn in (("aadhaar", "Aadhaar"), ("pan", "PAN")):
    for t in ("clean", "mild", "severe"):
        c = E8["rules_OCR"][f"{d}/{t}"]
        L.append(rf"{dn if t == 'clean' else ''} & {t} & {E6[f'C0/{d}/{t}']['ocr_induced']} & "
                 rf"{f1(c['fpr'])} {{\tiny[{c['ci'][0]:.1f}, {c['ci'][1]:.1f}]}} & "
                 rf"{f1(E8['A4_OCR'][f'{d}/{t}']['fpr'])} & {f1(E8['A5_OCR'][f'{d}/{t}']['fpr'])} & "
                 rf"{f1(E8['visual'][f'{d}/{t}']['fpr'])} \\")
    if d == "aadhaar":
        L.append(r"\addlinespace[1.5pt]")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(OUT / "res_rq46.tex").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- RQ5 figure data
D = A["delta_rho"]
coords = {}
for tag in ("GT", "OCR", "OCR_A5"):
    pts = []
    for key, lab_ in (("forged/aadhaar", "Aadhaar"), ("forged/pan", "PAN"), ("forged", "Both")):
        c = D[f"Delta_{tag}/{key}"]
        lo, hi = c["value"] - c["ci"][0], c["ci"][1] - c["value"]
        pts.append(f"({lab_},{c['value']:.1f}) += (0,{hi:.1f}) -= (0,{lo:.1f})")
    coords[tag] = " ".join(pts)
fig = r"""\begin{figure}[!t]
\centering
\begin{tikzpicture}
\begin{axis}[
  width=\columnwidth, height=4.4cm,
  ybar, bar width=7pt, ymin=-8, ymax=55,
  ylabel={$\Delta$ (recall points over visual)}, ylabel style={font=\scriptsize},
  symbolic x coords={Aadhaar, PAN, Both},
  xtick=data, xticklabel style={font=\scriptsize},
  yticklabel style={font=\scriptsize}, ytick={0,10,20,30,40,50},
  ymajorgrids, grid style={cgrey!20},
  legend style={font=\scriptsize, at={(0.5,1.03)}, anchor=south,
                legend columns=3, draw=none, column sep=4pt},
  enlarge x limits=0.25, axis lines*=left, extra y ticks={0},
  extra y tick style={grid style={black!60}},
  every axis plot/.append style={draw=none},
  error bars/y dir=both, error bars/y explicit,
  error bars/error bar style={black!70, line width=0.5pt},
]
\addplot[fill=cfuse!80] coordinates {@GT@};
\addplot[fill=cbad!70]  coordinates {@OCR@};
\addplot[fill=crule!80] coordinates {@A5@};
\legend{{A4, GT text},{A4, OCR text},{A5, OCR text (post-hoc)}}
\end{axis}
\end{tikzpicture}
\caption{Incremental value $\Delta$ of rule evidence over the visual branch at the 5\% operating
point, by document type (test split, 95\% intervals). With ground-truth text PAN gains twice as much
as Aadhaar; with OCR text and a single rule input (A4) the PAN gain vanishes, and per-check fusion
(A5) restores most of it.}
\label{fig:delta}
\end{figure}
"""
fig = fig.replace("@GT@", coords["GT"]).replace("@OCR@", coords["OCR"]).replace("@A5@", coords["OCR_A5"])
(OUT / "res_delta_fig.tex").write_text(fig, encoding="utf-8")

# ---------------------------------------------------------------- fresh replication
fr = {k: json.loads((FRESH / f"{k}_fresh.json").read_text(encoding="utf-8")) for k in
      ("visual", "rules_GT", "rules_OCR", "A4_logistic_GT", "A4_logistic_OCR",
       "A4_logistic_OCR_at_FPR_of_rules_OCR", "A5_perCheck_OCR", "OR_OCR")}
pairs = [("Visual (tiles)", "visual", "visual"), ("Rules, GT", "rules_GT", "rules_GT"),
         ("Rules, OCR", "rules_OCR", "rules_OCR"), ("OR, OCR", "OR_OCR", "OR_OCR"),
         ("A4, GT", "A4_GT", "A4_logistic_GT"), ("A4, OCR", "A4_OCR", "A4_logistic_OCR"),
         (r"A4, OCR, $=$Rules", "A4_OCR@rules", "A4_logistic_OCR_at_FPR_of_rules_OCR"),
         ("A5, OCR", "A5_OCR", "A5_perCheck_OCR")]
L = [r"\begin{table}[!t]",
     r"\caption{Replication on the fresh set (3{,}240 images of 90 unseen people) with every parameter "
     r"frozen. Recall and FPR in \%; fresh-set values with 95\% person-clustered intervals.}",
     r"\label{tab:fresh}", r"\centering", r"\scriptsize", r"\setlength{\tabcolsep}{3pt}",
     r"\renewcommand{\arraystretch}{1.06}",
     r"\begin{tabular}{@{}l r r r r@{}}", r"\toprule",
     r" & \multicolumn{2}{c}{v1 test} & \multicolumn{2}{c}{Fresh set} \\ \cmidrule(lr){2-3}\cmidrule(l){4-5}",
     r"System & Recall & FPR & Recall & FPR \\", r"\midrule"]
for lab_, tk, fk in pairs:
    f = fr[fk]
    o, b = f["overall"], f["bootstrap_ci_95"]
    L.append(rf"{lab_} & {f1(S[tk]['forged']['value'])} & {f1(S[tk]['c0']['value'])} & "
             rf"{100 * o['recall']['value']:.1f} {{\tiny[{100 * b['recall']['lo']:.1f}, {100 * b['recall']['hi']:.1f}]}} & "
             rf"{100 * o['fpr']['value']:.1f} {{\tiny[{100 * b['fpr']['lo']:.1f}, {100 * b['fpr']['hi']:.1f}]}} \\")
L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(OUT / "res_fresh.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote", ", ".join(p.name for p in sorted(OUT.glob("res_*.tex"))))
