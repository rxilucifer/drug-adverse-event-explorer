"""
PRR (Proportional Reporting Ratio) signal check

For one drug, checks whether each of its most reported side effects is
reported more often than for all other drugs in the FDA openFDA database.
A possible signal is flagged when: reports >= 3, PRR >= 2, chi-square >= 4.
This does NOT prove the drug causes the side effect.
"""
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

drug = "ibuprofen"  # change this to any drug
top_n = 30          # how many of the drug's side effects to check
url = "https://api.fda.gov/drug/event.json"


def get_total(search=None):
    """Number of reports matching a search (or all reports if no search)."""
    params = {"limit": 1}
    if search:
        params["search"] = search
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["meta"]["results"]["total"]


drug_search = f'patient.drug.medicinalproduct:"{drug}"'
N = get_total()                   # all reports in the database
n_drug = get_total(drug_search)   # reports that mention this drug

params = {
    "search": drug_search,
    "count": "patient.reaction.reactionmeddrapt.exact",
    "limit": top_n,
}
response = requests.get(url, params=params)
response.raise_for_status()
reactions = response.json()["results"]

rows = []
for item in reactions:
    reaction = item["term"]
    a = item["count"]  # reports with this drug AND this side effect
    reaction_total = get_total(f'patient.reaction.reactionmeddrapt:"{reaction}"')

    b = n_drug - a                 # this drug, other side effects
    c = reaction_total - a         # other drugs, this side effect
    d = (N - n_drug) - c           # other drugs, other side effects
    if c <= 0:
        continue

    prr = (a / (a + b)) / (c / (c + d))
    chi2 = N * (a * d - b * c) ** 2 / ((a + b) * (c + d) * (a + c) * (b + d))
    signal = a >= 3 and prr >= 2 and chi2 >= 4

    rows.append({"reaction": reaction, "reports": a, "PRR": prr,
                 "chi2": chi2, "possible_signal": signal})
    time.sleep(0.3)  # be gentle with the FDA server

df = pd.DataFrame(rows).sort_values("PRR", ascending=False)
print(df.round(2).to_string(index=False))

plot_df = df.sort_values("PRR")
plot_df.plot.barh(x="reaction", y="PRR", legend=False, figsize=(9, 8))
plt.axvline(2, color="red", linestyle="--")
plt.title(f"PRR for top reported reactions: {drug}")
plt.xlabel("PRR (red line = 2, the usual 'look closer' level)")
plt.tight_layout()
plt.savefig("images/prr_signals.png")
plt.show()