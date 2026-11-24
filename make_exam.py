"""Generate the HW4 practice exam, its worked answer key and the grading rubric (HTML -> PDF).

Every number in the key is computed here, so the key can't contain arithmetic slips.
Run: python3 make_exam.py   -> exam.html/.pdf, answer_key.html/.pdf, answers.json
"""
import json
import math
import os
import subprocess
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
Z95_1, Z80, Z975 = 1.645, 0.842, 1.96          # class table values


def sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def f(x, d=4):
    return f"{x:,.{d}f}"


A = {}   # answers for the tests
Q = []   # (number, points, topic, question_html, key_html, rubric_list)


def add(pts, topic, q, key, rubric):
    Q.append((len(Q) + 1, pts, topic, q, key, rubric))


# ---------------------------------------------------------------- Part 1: A/B testing
add(3, "Test design",
    "A travel site shows checkout page A Monday–Thursday and page B Friday–Sunday for two weeks, then compares conversion. Name the problem, say which way it biases the result if weekend shoppers convert better, and give the fix.",
    "The two pages see <b>different visitors</b> (weekday vs weekend), so the day mix is confounded with the page. If weekend shoppers convert better, B looks <b>better than it is</b>. "
    "<b>Fix:</b> randomize each visitor to A or B every day (e.g. 50/50 by a hash of the visitor ID), and keep returning visitors on their version.",
    ["1 pt: confounding / the groups differ", "1 pt: correct direction (B inflated)", "1 pt: per-visitor randomization on every day"])

xA, nA, xB, nB = 2400, 40000, 2610, 40000
pA, pB = xA / nA, xB / nB
pool = (xA + xB) / (nA + nB)
se_pool = math.sqrt(pool * (1 - pool) * (1 / nA + 1 / nB))
z0 = (pB - pA) / se_pool
p0 = sf(z0)
A["q2"] = {"pool": pool, "se": se_pool, "z": z0, "p": p0}
add(7, "Two-proportion z-test",
    f"Version A: {xA:,} bookings from {nA:,} visitors. Version B: {xB:,} from {nB:,}. Test H₀: p_B ≤ p_A against H₁: p_B &gt; p_A at α = 0.05 (one-sided, pooled SE). Report p̂ (pooled), the SE, z, the p-value and your decision.",
    f"p_A = {pA:.4f}, p_B = {pB:.4f}, lift = {pB - pA:.4f}.<br>Pooled p̂ = ({xA:,} + {xB:,}) / {nA + nB:,} = <b>{pool:.6f}</b>.<br>"
    f"SE = √(p̂(1−p̂)(1/n_A + 1/n_B)) = √({pool:.6f} × {1 - pool:.6f} × {1 / nA + 1 / nB:.6f}) = <b>{se_pool:.6f}</b>.<br>"
    f"z = {pB - pA:.4f} / {se_pool:.6f} = <b>{z0:.3f}</b>; one-sided p = 1 − Φ({z0:.3f}) = <b>{p0:.5f}</b> &lt; 0.05 → <b>reject H₀</b>: B converts better.",
    ["1 pt: rates and lift", "2 pts: pooled p̂ and SE", "2 pts: z", "1 pt: p-value", "1 pt: decision in words"])

d0 = 0.003
z1 = (pB - pA - d0) / se_pool
p1 = sf(z1)
A["q3"] = {"z": z1, "p": p1}
add(4, "Testing against a minimum lift",
    "Finance only funds changes with a lift of at least 0.3 percentage points. Using the data and pooled SE from Q2, test H₀: p_B − p_A ≤ 0.003. Then explain in one sentence how Q2 and Q3 can both be right.",
    f"z = ({pB - pA:.4f} − 0.003) / {se_pool:.6f} = <b>{z1:.3f}</b>; one-sided p = <b>{p1:.4f}</b> &gt; 0.05 → <b>fail to reject</b>: the lift isn't shown to be ≥ 0.3 pts.<br>"
    f"Both are right: the observed lift ({100 * (pB - pA):.3f} pts) is clearly above 0 but within about {100 * Z95_1 * se_pool:.2f} pts (one-sided 95%) of 0.3, so it's clearly positive but not clearly ≥ 0.3.",
    ["2 pts: z and p", "1 pt: decision", "1 pt: reconciliation"])

se_un = math.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
lo, hi = (pB - pA) - Z975 * se_un, (pB - pA) + Z975 * se_un
V, M, BUILD = 150000, 22, 25000
extra = V * (pB - pA)
dollars = extra * M
payback = BUILD / (dollars / 30)
A["q4"] = {"se_un": se_un, "lo": lo, "hi": hi, "dollars": dollars, "payback": payback, "dlo": lo * V * M, "dhi": hi * V * M}
add(7, "Pricing the lift",
    f"With {V:,} visitors a month and a ${M} margin per booking, what is B worth per month? How many days until the ${BUILD:,} build cost pays back (30-day month)? Give a 95% confidence interval for the monthly dollar value (unpooled SE).",
    f"Extra bookings = {V:,} × {pB - pA:.4f} = {extra:,.0f}/month; × ${M} = <b>${dollars:,.0f}/month</b>.<br>"
    f"Payback = {BUILD:,} / ({dollars:,.0f}/30) = <b>{payback:.1f} days</b>.<br>"
    f"Unpooled SE = √(p_A(1−p_A)/n_A + p_B(1−p_B)/n_B) = {se_un:.6f}; 95% CI for the lift = {pB - pA:.4f} ± 1.96 × {se_un:.6f} = [{lo:.5f}, {hi:.5f}];<br>"
    f"× {V:,} × ${M} = <b>[${lo * V * M:,.0f}, ${hi * V * M:,.0f}] per month</b>. (Unpooled, because a CI estimates the difference rather than assuming H₀.)",
    ["2 pts: monthly dollars", "1 pt: payback", "2 pts: unpooled SE and lift CI", "2 pts: dollar CI"])

p1_, p2_ = 0.04, 0.044
n_raw = (Z95_1 + Z80) ** 2 * (p1_ * (1 - p1_) + p2_ * (1 - p2_)) / (p2_ - p1_) ** 2
n_exact = Fraction(2487, 1000) ** 2 * (Fraction(4, 100) * Fraction(96, 100) + Fraction(44, 1000) * Fraction(956, 1000)) / Fraction(4, 1000) ** 2
n = math.ceil(n_exact)
days = 2 * n / 5000
A["q5"] = {"n_raw": float(n_exact), "n": n, "days": days}
add(6, "Sample size",
    "Plan a test to detect 4.0% → 4.4% with one-sided α = 0.05 and 80% power (use z = 1.645 and 0.842, and the unpooled variance p₁(1−p₁) + p₂(1−p₂)). How many visitors per arm? How many days at 5,000 visitors a day (both arms)? Roughly how many visitors per arm would detecting 4.0% → 4.2% need, and why?",
    f"n = (1.645 + 0.842)² × (0.04 × 0.96 + 0.044 × 0.956) / 0.004² = 6.185169 × {0.04 * 0.96 + 0.044 * 0.956:.6f} / 0.000016 = {float(n_exact):,.1f} → <b>{n:,} per arm</b>.<br>"
    f"Days = 2 × {n:,} / 5,000 = {days:.2f} → <b>{math.ceil(days)} days</b>.<br>"
    f"Halving the detectable lift roughly <b>quadruples</b> n (n ∝ 1/d²; the variances barely change): about {4 * n:,} per arm.",
    ["3 pts: n with work shown, rounded up", "1 pt: days", "2 pts: ~4× with the 1/d² reason"])

add(4, "Peeking",
    "A team checks its A/A test (no real difference) every day for 10 days and stops the first time p &lt; 0.05. About what false-positive rate do they really have? Why? Name one fix.",
    "Each look is another chance for noise to cross the threshold, and they stop at the first crossing, so false alarms accumulate: about <b>19%</b> for 10 looks (exactly 19.3% for equally spaced looks), not 5%. "
    "<b>Fixes:</b> fix the sample size and test once at the end; or use a sequential design with alpha spending (e.g. O'Brien–Fleming boundaries).",
    ["1 pt: roughly 15–25%", "2 pts: multiple looks + stopping at the first crossing", "1 pt: a valid fix"])

# ---------------------------------------------------------------- Part 2: choice models
VA, VB = 1.2, 0.8
eA, eB = math.exp(VA), math.exp(VB)
tot = eA + eB + 1
A["q7"] = {"PA": eA / tot, "PB": eB / tot, "P0": 1 / tot}
add(4, "Logit shares",
    "In a logit model, Bundle A has V = 1.2, Bundle B has V = 0.8, and \"Not now\" has V = 0. Compute the three choice probabilities. What does the error term ε represent, and what distribution gives this formula?",
    f"e^1.2 = {eA:.4f}, e^0.8 = {eB:.4f}, e^0 = 1; total = {tot:.4f}.<br>P(A) = <b>{eA / tot:.3f}</b>, P(B) = <b>{eB / tot:.3f}</b>, P(Not now) = <b>{1 / tot:.3f}</b>.<br>"
    "ε is everything about the choice the model can't see (tastes, the trip, mood). Assuming iid <b>Gumbel</b> (type I extreme value) errors gives P_j = e^{V_j}/Σ_k e^{V_k}.",
    ["3 pts: three probabilities", "1 pt: ε and Gumbel"])

coef = {"bag": (0.75, 0.10), "flex": (0.30, 0.20), "price": (-0.025, 0.002)}
wtp_bag, wtp_flex = 0.75 / 0.025, 0.30 / 0.025
A["q8"] = {"wtp_bag": wtp_bag, "wtp_flex": wtp_flex, "z_flex": 0.30 / 0.20, "z_bag": 7.5}
add(7, "Reading a logit fit, WTP",
    "A conditional logit on a fare survey gives: bag 0.75 (SE 0.10), free changes 0.30 (SE 0.20), price −0.025 per dollar (SE 0.002). (a) Which coefficients are reliably different from zero? (b) Compute willingness to pay for a bag and for free changes. (c) A $35 add-on gives both features: is it priced below what customers value it at?",
    f"(a) z = coef/SE: bag 7.5, free changes <b>1.5</b>, price −12.5. Bag and price are significant (|z| &gt; 1.96); <b>free changes is not</b>.<br>"
    f"(b) WTP = coef / (−price): bag = 0.75/0.025 = <b>${wtp_bag:.2f}</b>; free changes = 0.30/0.025 = <b>${wtp_flex:.2f}</b> (imprecise: its z is only 1.5).<br>"
    f"(c) Value ${wtp_bag + wtp_flex:.2f} vs price $35, so it's worth <b>+${wtp_bag + wtp_flex - 35:.2f}</b> to the average customer. Priced below value, though the flex part is uncertain.",
    ["2 pts: z values and significance", "3 pts: both WTPs with the minus sign handled", "2 pts: comparison and caveat"])

VS = 0.9
eS = math.exp(VS)
buy1 = eS / (eS + 1)
buy2 = 2 * eS / (2 * eS + 1)
A["q9"] = {"buy1": buy1, "buy2": buy2}
add(5, "IIA",
    "Standard has V = 0.9 against \"Not now\" (V = 0). The airline adds \"Standard Saver\", identical to Standard in every way (same V). What total purchase share does the logit predict before and after? What would really happen, and which model property causes the gap? Name a model that avoids it.",
    f"Before: e^0.9/(e^0.9 + 1) = <b>{buy1:.3f}</b>. After: 2e^0.9/(2e^0.9 + 1) = <b>{buy2:.3f}</b>.<br>"
    "Really, an identical copy adds nothing new, so buying should stay at about the first number, with Standard's buyers split between two names. "
    "The cause is <b>IIA</b> (independence of irrelevant alternatives, from iid errors): the copy takes share in proportion from every option, including Not now. A <b>nested logit</b> (or a mixed logit with correlated errors) groups the twins.",
    ["2 pts: both shares", "1 pt: realistic outcome", "1 pt: IIA named and explained", "1 pt: alternative model"])

LL, N_SCR = -1250.0, 1400
LL0 = N_SCR * math.log(1 / 3)
rho2 = 1 - LL / LL0
A["q10"] = {"LL0": LL0, "rho2": rho2}
add(3, "McFadden ρ²",
    f"A fit on {N_SCR:,} choice screens (3 options each) has log-likelihood −1,250. Compute LL(0) and McFadden's ρ². Is that a bad fit?",
    f"LL(0) = {N_SCR:,} × ln(1/3) = <b>{LL0:,.2f}</b>; ρ² = 1 − (−1,250)/({LL0:,.2f}) = <b>{rho2:.3f}</b>. "
    "Not bad: ρ² of 0.1–0.3 is typical for choice models; it isn't comparable to a regression R².",
    ["1 pt: LL(0)", "1 pt: ρ²", "1 pt: interpretation"])

# ---------------------------------------------------------------- Part 3: bandits
P = [0.040, 0.055, 0.030]
T, TEST, PRICE = 60000, 15000, 12
oracle = T * max(P)
plan = TEST / 3 * sum(P) + (T - TEST) * max(P)
regret = oracle - plan
A["q11"] = {"oracle": oracle, "plan": plan, "regret": regret, "dollars": regret * PRICE}
add(5, "Regret",
    f"Three versions of an upsell convert at A 4.0%, B 5.5%, C 3.0% (unknown to you). Plan: split the first {TEST:,} of {T:,} visitors evenly, then show the winner (assume it's B). Each upgrade is worth ${PRICE}. Compute the oracle's upgrades, the plan's upgrades, the regret and its dollar cost.",
    f"Oracle = {T:,} × 0.055 = <b>{oracle:,.0f}</b>. Plan = 5,000 × (0.04 + 0.055 + 0.03) + {T - TEST:,} × 0.055 = {TEST / 3 * sum(P):,.0f} + {(T - TEST) * max(P):,.0f} = <b>{plan:,.0f}</b>.<br>"
    f"Regret = <b>{regret:,.0f} upgrades</b> = <b>${regret * PRICE:,.0f}</b>.",
    ["1 pt: oracle", "2 pts: plan", "2 pts: regret and dollars"])

floor = 0.1 * ((0.055 - 0.04) + 0 + (0.055 - 0.03)) / 3 * T
A["q12"] = {"floor": floor}
add(4, "ε-greedy floor",
    "With the same rates and 60,000 visitors, ε-greedy with ε = 0.1 explores uniformly over all three versions. Even if it always exploits B otherwise, what is its expected regret at minimum? Why doesn't this floor shrink with more data, and which strategy avoids it?",
    f"Floor = ε × (average gap over the 3 arms) × T = 0.1 × (0.015 + 0 + 0.025)/3 × {T:,} = <b>{floor:.0f} upgrades</b>.<br>"
    "It explores 10% of the time forever, whatever it has learned. <b>Thompson sampling</b> (or decaying ε / UCB) explores less as it becomes confident.",
    ["2 pts: floor with work", "1 pt: why it persists", "1 pt: alternative"])

eps = 0.15
A["q13"] = {"leader": 1 - eps + eps / 3, "other": eps / 3}
add(3, "ε-greedy probabilities",
    "ε-greedy with ε = 0.15 over three subject lines; C currently has the best average open rate. The random pick on explore is uniform over all three (C included). What's the probability each line is sent next?",
    f"P(C) = 0.85 + 0.15/3 = <b>{1 - eps + eps / 3:.2f}</b>; P(A) = P(B) = 0.15/3 = <b>{eps / 3:.2f}</b>.",
    ["2 pts: P(C) including the explore share", "1 pt: the others"])

post = {"A": (3, 5), "B": (5, 4), "C": (2, 2)}
draws = {"A": 0.48, "B": 0.44, "C": 0.61}
sent = max(draws, key=draws.get)
a, b = post[sent]
A["q14"] = {"sent": sent, "post_after": (a, b + 1), "meanB": 5 / 9}
add(6, "Thompson sampling",
    "Thompson sampling with Beta(1, 1) priors. So far: A opened 2 of 6 sends, B 4 of 7, C 1 of 2. (a) Write each posterior and its mean. (b) This round's draws are A 0.48, B 0.44, C 0.61. Which line is sent? (c) It isn't opened. What is that line's new posterior? (d) Why does C get chosen despite having the least data?",
    "(a) Beta(1 + opens, 1 + non-opens): A Beta(3, 5), mean 0.375; B Beta(5, 4), mean 0.556; C Beta(2, 2), mean 0.500.<br>"
    f"(b) Highest draw: <b>{sent}</b> (0.61).<br>(c) Not opened adds 1 to the second parameter: <b>Beta(2, 3)</b>, mean 0.400.<br>"
    "(d) C's posterior is wide (little data), so it often produces high draws. That's how Thompson explores, and it does less of it as posteriors narrow.",
    ["2 pts: posteriors and means", "1 pt: highest draw (not highest mean)", "2 pts: update", "1 pt: exploration explanation"])

# ---------------------------------------------------------------- Part 4: machine learning
add(3, "Model families",
    "Pick a model family for each and justify in a phrase: (a) loan approvals where every decline must come with reasons; (b) spotting damaged parcels in warehouse photos; (c) predicting delivery delays from 40 tabular order features.",
    "(a) <b>Logistic regression</b> (or a scorecard / shallow tree): interpretable coefficients give reason codes. (b) <b>Convolutional neural network</b> (pretrained, fine-tuned): images need learned spatial features. "
    "(c) <b>Gradient-boosted trees</b>: strong on tabular data with nonlinearities and interactions.",
    ["1 pt each: family plus reason"])

NN, RATE = 30000, 0.08
val = int(NN * 0.15)
sd = math.sqrt(val * RATE * (1 - RATE))
A["q16"] = {"train": int(NN * 0.7), "val": val, "pos_val": int(val * RATE), "sd": sd}
add(4, "Splits",
    f"{NN:,} labeled rows, {RATE:.0%} positive. Split 70/15/15 with stratification: give each set's size and number of positives. Without stratification, what's the standard deviation of the number of positives in the validation set (binomial)?",
    f"Train <b>{int(NN * 0.7):,} ({int(NN * 0.7 * RATE):,} positives)</b>, validation <b>{val:,} ({int(val * RATE):,})</b>, test <b>{val:,} ({int(val * RATE):,})</b>.<br>"
    f"SD = √(n·p·(1−p)) = √({val:,} × 0.08 × 0.92) = √{val * RATE * (1 - RATE):.0f} = <b>{sd:.1f}</b> positives.",
    ["2 pts: sizes and positives", "2 pts: SD"])

table = [(0, 2.10, 2.15), (1, 1.62, 1.70), (2, 1.05, 1.12), (3, 0.98, 1.20), (5, 0.71, 1.95), (9, 0.00, 14.30)]
rows = "".join(f"<tr><td>{d}</td><td>{tr:.2f}</td><td>{va:.2f}</td></tr>" for d, tr, va in table)
add(5, "Overfitting, Ridge and LASSO",
    f"A polynomial is fit to 10 training points. <table class='mini'><tr><th>Degree</th><th>Train RMSE</th><th>Validation RMSE</th></tr>{rows}</table> (a) Which degree would you pick, and which degrees under- or overfit? (b) Why is degree 9's training error exactly 0? (c) How do Ridge and LASSO differ in what they do to coefficients?",
    "(a) <b>Degree 2</b>: lowest validation RMSE (1.12). Degrees 0–1 underfit (both errors high); 3 and up overfit (training keeps falling, validation rises, exploding at 9).<br>"
    "(b) Degree 9 has 10 parameters for 10 points, so it <b>interpolates</b> every point: it fits the noise, which is memorizing, not learning.<br>"
    "(c) Ridge (λΣβ²) shrinks all coefficients smoothly toward zero; LASSO (λΣ|β|) sets some <b>exactly</b> to zero, so it also selects features. Neither penalizes the intercept.",
    ["2 pts: degree 2 and the under/overfit ranges", "1 pt: interpolation", "2 pts: Ridge vs LASSO"])

cm = {"0.3": (150, 220, 50, 1580), "0.6": (95, 40, 105, 1760)}
CFP, CFN = 200, 900
costs = {k: CFP * v[1] + CFN * v[2] for k, v in cm.items()}
acc = {k: (v[0] + v[3]) / sum(v) for k, v in cm.items()}
A["q18"] = {"costs": costs, "acc": acc, "breakeven": CFP / (CFP + CFN)}
add(7, "Cutoffs and costs",
    f"A churn model's results on 2,000 customers at two cutoffs (TP, FP, FN, TN): α = 0.3 → (150, 220, 50, 1,580); α = 0.6 → (95, 40, 105, 1,760). A false positive (an unneeded retention offer) costs ${CFP}; a false negative (a lost customer's margin) costs ${CFN}. (a) Compute accuracy, precision, recall and cost at each cutoff. (b) Which cutoff would you use and why? (c) If the scores are calibrated, what's the break-even cutoff?",
    "".join(f"(a) α = {k}: accuracy {acc[k]:.3f}, precision {v[0] / (v[0] + v[1]):.3f}, recall {v[0] / (v[0] + v[2]):.3f}, cost {CFP}×{v[1]} + {CFN}×{v[2]} = <b>${costs[k]:,}</b>.<br>" for k, v in cm.items()) +
    (lambda cheap, other: f"(b) <b>α = {cheap}</b>: it costs ${costs[cheap]:,} vs ${costs[other]:,}" + (f", even though α = {other} is more accurate ({acc[other]:.3f} vs {acc[cheap]:.3f})" if acc[other] > acc[cheap] else "") + f". Misses cost {CFN / CFP:.1f}× as much as false alarms, so the cheaper rule is the one that flags {'more' if cheap == '0.3' else 'fewer'} customers.<br>")(min(costs, key=costs.get), max(costs, key=costs.get)) +
    f"(c) Flag when p × {CFN} &gt; (1 − p) × {CFP}, i.e. p &gt; {CFP}/({CFP} + {CFN}) = <b>{CFP / (CFP + CFN):.3f}</b>.",
    ["3 pts: metrics and costs", "2 pts: choice by cost (not accuracy)", "2 pts: break-even"])

pos = [0.9, 0.7, 0.6, 0.4]
neg = [0.8, 0.6, 0.3, 0.2, 0.1]
pairs = sum(1 if p > q else 0.5 if p == q else 0 for p in pos for q in neg)
A["q19"] = {"pairs": pairs, "auc": pairs / 20}
add(6, "ROC and AUC",
    "Scores: positives 0.9, 0.7, 0.6, 0.4; negatives 0.8, 0.6, 0.3, 0.2, 0.1. (a) Compute the AUC by pair counting (ties count ½). (b) What does that number mean in words? (c) What are TPR and FPR at cutoff 0.6 (flag if score ≥ 0.6)?",
    f"(a) For each positive, count negatives below it (+½ per tie): 0.9 → 5, 0.7 → 4, 0.6 → 3 + ½, 0.4 → 3; total {pairs} of 4 × 5 = 20 pairs → <b>AUC = {pairs / 20:.3f}</b>.<br>"
    f"(b) A randomly chosen positive scores higher than a randomly chosen negative {pairs / 20:.1%} of the time.<br>"
    "(c) Flagged: positives 0.9, 0.7, 0.6 → TPR = <b>3/4 = 0.75</b>; negatives 0.8, 0.6 → FPR = <b>2/5 = 0.40</b>.",
    ["3 pts: pair counting with ties", "1 pt: interpretation", "2 pts: TPR and FPR"])

add(7, "Audit a model report",
    "An analyst writes: \"Readmission model, predicting at discharge. Random 80/20 split of 60,000 hospital stays (many patients have several stays). Features: age, length of stay, prior admissions, follow-up visit attended. Test: TP 300, FP 100, FN 300, TN 5,300. Accuracy 93.3%, precision 0.80. Longer stays cause readmissions, so shortening stays would cut readmissions.\" Find three problems, name the audit question each fails (leakage, metric, matrix, or claim), and give the fix.",
    "Any three, with fixes:<br>• <b>Leakage:</b> <i>follow-up visit attended</i> happens after discharge. Drop it or use only what's known at discharge. Also: a random split by stay puts the same patient in train and test. Split by patient or by time.<br>"
    "• <b>Matrix:</b> precision = 300/400 = <b>0.75</b>, not 0.80; recall = 300/600 = <b>0.50</b>, unreported. Recompute every metric from the matrix and report recall.<br>"
    "• <b>Metric:</b> accuracy (5,600/6,000 = 0.933) is close to the 0.90 from predicting \"no readmission\" for everyone. Compare with the baseline and use cost or recall.<br>"
    "• <b>Claim:</b> \"cause\" from a predictive model. Restate it as association; test with a randomized change if it matters.",
    ["2 pts per problem (1 for naming it + its audit question, 1 for a workable fix), up to 3 problems", "1 pt: at least one numeric recomputation (0.75 or 0.50 or the 0.90 baseline)"])

assert len(Q) == 20 and sum(q[1] for q in Q) == 100, (len(Q), sum(q[1] for q in Q))

# ---------------------------------------------------------------- render
CSS = """
@page { size: letter; margin: 0.6in 0.65in; }
body { font: 10.6pt/1.45 Georgia, "Times New Roman", serif; color: #111; margin: 0; }
h1 { font: 700 18pt -apple-system, Arial, sans-serif; margin: 0 0 4px; }
.meta { font: 10pt -apple-system, Arial, sans-serif; color: #444; border-bottom: 1.5px solid #222; padding-bottom: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; }
.instr { font-size: 10pt; background: #f4f4f1; padding: 8px 10px; border-radius: 6px; margin-bottom: 10px; }
h2 { font: 700 12pt -apple-system, Arial, sans-serif; margin: 16px 0 6px; border-bottom: 1px solid #bbb; }
.q { margin: 8px 0 4px; page-break-inside: avoid; }
.q .h { font: 700 10.5pt -apple-system, Arial, sans-serif; }
.q .h span { font-weight: 400; color: #555; }
.space { height: 1.25in; border-bottom: 1px dotted #bbb; margin-bottom: 6px; }
.space.big { height: 1.9in; }
.key { background: #f7f7f4; border-left: 3px solid #3b5bdb; padding: 6px 10px; margin: 4px 0 4px; font-size: 10.2pt; }
.rub { font: 9.3pt -apple-system, Arial, sans-serif; color: #333; margin: 2px 0 10px 16px; }
table.mini { border-collapse: collapse; margin: 4px 0; font: 9.5pt -apple-system, Arial, sans-serif; }
table.mini td, table.mini th { border: 1px solid #bbb; padding: 2px 8px; text-align: right; }
table.grid { border-collapse: collapse; width: 100%; font: 9.5pt -apple-system, Arial, sans-serif; }
table.grid td, table.grid th { border: 1px solid #ccc; padding: 3px 6px; }
.brk { page-break-before: always; }
"""
PARTS = {1: "Part 1 · A/B testing (Q1–Q6)", 7: "Part 2 · Choice models (Q7–Q10)", 11: "Part 3 · Bandits (Q11–Q14)", 15: "Part 4 · Machine learning (Q15–Q20)"}
BIG = {2, 4, 5, 8, 14, 18, 19, 20}


def page(title, body):
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"


exam = [f"<h1>DSO 429 · Practice Exam: A/B Tests, Choice Models, Bandits &amp; ML</h1>",
        "<div class='meta'><span>Time: 2 hours · 20 questions · 100 points</span><span>Name: ______________________</span></div>",
        "<div class='instr'>Show your work: most points are for the method. Calculator allowed. Use z = 1.645 (one-sided 5%), 1.96 (two-sided 5%) and 0.842 (80% power) unless told otherwise. "
        "Round final answers sensibly (proportions to 3–4 decimals, dollars to whole dollars). Budget about 1 minute per point.</div>"]
key = ["<h1>Practice Exam · Answer Key &amp; Grading Rubric</h1>",
       "<div class='meta'><span>Every number below was computed by make_exam.py</span><span>100 points</span></div>"]
for num, pts, topic, q, k, rub in Q:
    if num in PARTS:
        exam.append(f"<h2>{PARTS[num]}</h2>")
        key.append(f"<h2>{PARTS[num]}</h2>")
    exam.append(f"<div class='q'><div class='h'>Q{num}. {topic} <span>({pts} pts)</span></div>{q}</div><div class='space{' big' if num in BIG else ''}'></div>")
    key.append(f"<div class='q'><div class='h'>Q{num}. {topic} <span>({pts} pts)</span></div><div class='key'>{k}</div><ul class='rub'>" + "".join(f"<li>{r}</li>" for r in rub) + "</ul></div>")
grid = "<table class='grid'><tr><th>Q</th><th>Topic</th><th>Points</th><th>Score</th></tr>" + "".join(f"<tr><td>{n}</td><td>{t}</td><td>{p}</td><td></td></tr>" for n, p, t, *_ in Q) + "<tr><th></th><th>Total</th><th>100</th><th></th></tr></table>"
key.append("<h2 class='brk'>Grading rubric · summary</h2><p style='font:9.5pt Arial'>Award method points even when an early arithmetic slip carries through (follow-through), unless the slip makes the problem trivial. Answers within rounding of the key get full credit. "
           "Short answers need the named concept <i>and</i> the reason; a correct name with no reason earns half.</p>" + grid +
           "<p style='font:9.5pt Arial'><b>Grade bands:</b> 90+ excellent · 75–89 solid · 60–74 review Parts with the most lost points · below 60 rework the homework first.</p>")
open(os.path.join(HERE, "exam.html"), "w").write(page("Practice exam", "".join(exam)))
open(os.path.join(HERE, "answer_key.html"), "w").write(page("Answer key", "".join(key)))
json.dump({"questions": [{"n": n, "points": p, "topic": t} for n, p, t, *_ in Q], "answers": A}, open(os.path.join(HERE, "answers.json"), "w"), indent=1, default=float)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for name in ("exam", "answer_key"):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={os.path.join(HERE, name + '.pdf')}",
                    "file://" + os.path.join(HERE, name + ".html")], check=True, stderr=subprocess.DEVNULL)
print("wrote exam.pdf, answer_key.pdf, answers.json")
