"""
Drug Adverse Event Explorer

Gets the most reported side effects for a drug from the FDA openFDA API
and saves them as a bar chart.
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt

drug = "ibuprofen"  # change this to any drug you like

url = "https://api.fda.gov/drug/event.json"
params = {
    "search": f'patient.drug.medicinalproduct:"{drug}"',
    "count": "patient.reaction.reactionmeddrapt.exact",
    "limit": 15,
}

response = requests.get(url, params=params)
response.raise_for_status()

df = pd.DataFrame(response.json()["results"])
df.columns = ["reaction", "reports"]
print(df)

df.sort_values("reports").plot.barh(x="reaction", y="reports", legend=False)
plt.title(f"Top reported reactions: {drug}")
plt.xlabel("Number of reports")
plt.tight_layout()
plt.savefig("images/top_reactions.png")
plt.show()