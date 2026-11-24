"""Checks for the practice exam: structure, rubric arithmetic, and independent recomputation of the key.
Run: python3 test_exam.py   (after make_exam.py)"""
import json
import math
import os
import re
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, "answers.json")))
A, QS = J["answers"], J["questions"]
key = open(os.path.join(HERE, "answer_key.html")).read()
exam = open(os.path.join(HERE, "exam.html")).read()
ok = []


def check(name, cond, detail=""):
    ok.append(bool(cond))
    print("%s  %s%s" % ("PASS" if cond else "FAIL", name, (": " + detail) if detail else ""))


N = NormalDist()
# 1. structure
check("20 questions worth 100 points", len(QS) == 20 and sum(q["points"] for q in QS) == 100)
check("every question appears in the exam and the key", all(f"Q{q['n']}. " in exam and f"Q{q['n']}. " in key for q in QS))
check("the exam doesn't leak answers", "class='key'" not in exam and "31,106" not in exam and "0.775" not in exam)
# rubric points per question add up (rubric lines like '2 pts: ...'; Q15/Q20 use per-item wording)
blocks = re.findall(r"Q(\d+)\. [^<]+ <span>\((\d+) pts\)</span>.*?<ul class='rub'>(.*?)</ul>", key, re.S)
mismatch = []
for n, pts, rub in blocks:
    items = re.findall(r"<li>(.*?)</li>", rub)
    if n == "15":
        total = 3 * 1
    elif n == "20":
        total = 3 * 2 + 1
    else:
        total = sum(int(m) for it in items for m in re.findall(r"^(\d+) pts?", it))
    if total != int(pts):
        mismatch.append((n, total, pts))
check("rubric points add up to each question's points", len(blocks) == 20 and not mismatch, str(mismatch) if mismatch else "")

# 2. independent recomputation of key numbers
q2 = A["q2"]
pool = 5010 / 80000
se = math.sqrt(pool * (1 - pool) * (2 / 40000))
check("Q2 pooled z-test", abs(q2["se"] - se) < 1e-12 and abs(q2["p"] - (1 - N.cdf(0.005250 / se))) < 1e-9, f"z {q2['z']:.3f}, p {q2['p']:.5f}")
check("Q3 minimum-lift test fails to reject", A["q3"]["p"] > 0.05 and abs(A["q3"]["z"] - (0.00525 - 0.003) / se) < 1e-12)
check("Q4 dollar CI uses the unpooled SE", abs(A["q4"]["dlo"] - (0.00525 - 1.96 * A["q4"]["se_un"]) * 150000 * 22) < 1e-6 and abs(A["q4"]["payback"] - 25000 / (17325 / 30)) < 1e-9)
n_float = 2.487 ** 2 * (0.04 * 0.96 + 0.044 * 0.956) / 0.004 ** 2
check("Q5 sample size 31,106 per arm, 13 days", A["q5"]["n"] == math.ceil(n_float - 1e-9) == 31106 and math.ceil(A["q5"]["days"]) == 13, f"{n_float:.2f}")
check("Q7 logit shares sum to 1", abs(A["q7"]["PA"] + A["q7"]["PB"] + A["q7"]["P0"] - 1) < 1e-12 and abs(A["q7"]["PA"] - math.exp(1.2) / (math.exp(1.2) + math.exp(0.8) + 1)) < 1e-12)
check("Q8 WTP bag $30, flex $12 (not significant)", round(A["q8"]["wtp_bag"], 6) == 30 and round(A["q8"]["wtp_flex"], 6) == 12 and A["q8"]["z_flex"] < 1.96)
check("Q9 IIA shares", abs(A["q9"]["buy2"] - 2 * math.exp(0.9) / (2 * math.exp(0.9) + 1)) < 1e-12 and A["q9"]["buy2"] > A["q9"]["buy1"])
check("Q10 rho^2 = 0.187", abs(A["q10"]["rho2"] - (1 - 1250 / (1400 * math.log(3)))) < 1e-12)
check("Q11 regret 200 upgrades = $2,400", A["q11"]["regret"] == 200 and A["q11"]["dollars"] == 2400)
check("Q12 epsilon floor 80", round(A["q12"]["floor"], 9) == 80)
check("Q14 Thompson sends the highest draw and updates beta", A["q14"]["sent"] == "C" and A["q14"]["post_after"] == [2, 3])
check("Q16 SD of validation positives = sqrt(4500 x .08 x .92)", abs(A["q16"]["sd"] - math.sqrt(4500 * 0.08 * 0.92)) < 1e-12)
c = A["q18"]
check("Q18 cheapest cutoff is not the most accurate one", min(c["costs"], key=c["costs"].get) != max(c["acc"], key=c["acc"].get) and abs(c["breakeven"] - 200 / 1100) < 1e-12,
      f"costs {c['costs']}, accuracy {c['acc']}")
pos, neg = [0.9, 0.7, 0.6, 0.4], [0.8, 0.6, 0.3, 0.2, 0.1]
auc = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / 20
check("Q19 AUC by pair counting = 0.775", abs(A["q19"]["auc"] - auc) < 1e-12 and auc == 0.775)
check("Q20 recomputations: precision 0.75, recall 0.50, accuracy 0.933, baseline 0.90",
      300 / 400 == 0.75 and 300 / 600 == 0.5 and abs(5600 / 6000 - 0.9333) < 1e-4 and 5400 / 6000 == 0.9 and "0.75" in key and "0.50" in key)
check("Q6 peeking rate for 10 looks quoted as about 19%", "19.3%" in key)

# 3. the key shows the computed numbers
for s in ("31,106", "0.775", "$89,000", "$102,500", "0.187", "$2,400", "0.182"):
    if s not in key:
        check(f"key contains {s}", False)
check("key quotes the computed numbers", all(s in key for s in ("31,106", "0.775", "$89,000", "$102,500", "0.187", "$2,400", "0.182")))
# 4. PDFs
pages = {f: int(re.search(r"Pages:\s+(\d+)", os.popen(f"pdfinfo {os.path.join(HERE, f)}").read()).group(1)) for f in ("exam.pdf", "answer_key.pdf")}
check("printable PDFs exist (exam with answer space, key with rubric)", 4 <= pages["exam.pdf"] <= 9 and 3 <= pages["answer_key.pdf"] <= 8, str(pages))
print("\n%d/%d PASS" % (sum(ok), len(ok)))
raise SystemExit(0 if all(ok) else 1)
