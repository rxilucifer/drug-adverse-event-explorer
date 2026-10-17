"""
Drug comparison

Compares the most reported side effects of two drugs using FDA openFDA data.
Shows each side effect as a percentage of that drug's own reports,
so a drug with more reports does not look worse just because it is more popular.
"""
import requests
import pandas as pd
import matplotlib.pyplot as plt

drugs = ["ibuprofen", "acetaminophen"]  # change these to compare other drugs
url = "https://api.fda.gov/drug/event.json"


def get_total_reports(drug):
    """How many reports mention this drug in total."""
    params = {"search": f'patient.drug.medicinalproduct:"{drug}"', "limit": 1}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["meta"]["results"]["total"]


def get_top_reactions(drug, limit=30):
    """The most reported side effects for this drug."""
    params = {
        "search": f'patient.drug.medicinalproduct:"{drug}"',
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": limit,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    df = pd.DataFrame(response.json()["results"])
    df.columns = ["reaction", drug]
    return df.set_index("reaction")


frames = []
for drug in drugs:
    total = get_total_reports(drug)
    df = get_top_reactions(drug)
    df[drug] = df[drug] / total * 100  # turn counts into percentages
    frames.append(df)

# keep side effects that appear in both drugs' lists, then take the top 10
combined = frames[0].join(frames[1], how="inner")
combined["total"] = combined.sum(axis=1)
combined = combined.sort_values("total", ascending=False).head(10)
combined = combined.drop(columns="total").sort_values(drugs[0])

print(combined.round(2))

combined.plot.barh(figsize=(9, 6))
plt.title(f"Top reported reactions: {drugs[0]} vs {drugs[1]}")
plt.xlabel("% of each drug's reports")
plt.tight_layout()
plt.savefig("images/drug_comparison.png")
plt.show()