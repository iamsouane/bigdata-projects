# -*- coding: utf-8 -*-
"""
Calcul de référence avec pandas, avec EXACTEMENT le même nettoyage que spark.py.
Sert à valider le résultat produit sur EMR.

Usage : python reference_pandas.py transaction.csv reference_revenue_by_country.csv
"""
import sys

import pandas as pd

src, dst = sys.argv[1], sys.argv[2]
df = pd.read_csv(src, dtype=str, keep_default_na=False)
print("Lignes lues :", len(df))

clean = pd.DataFrame({
    "Country": df["country"].str.strip(),                          # trim
    "Quantity": pd.to_numeric(df["quantity"], errors="coerce"),    # cast double
    "UnitPrice": pd.to_numeric(df["unit_price"], errors="coerce"),
})
clean = clean.dropna(subset=["Country", "Quantity", "UnitPrice"])  # dropna
clean = clean[(clean["Country"] != "")                             # filtres
              & (clean["Quantity"] > 0)
              & (clean["UnitPrice"] >= 0)]
print("Lignes après nettoyage :", len(clean))

clean["Revenue"] = clean["Quantity"] * clean["UnitPrice"]
result = (clean.groupby("Country", as_index=False)["Revenue"].sum()
          .rename(columns={"Revenue": "TotalRevenue"}))
result["TotalRevenue"] = result["TotalRevenue"].round(2)
result = result.sort_values(["TotalRevenue", "Country"],
                            ascending=[False, True]).reset_index(drop=True)
print(result.to_string(index=False))
print("Nombre de pays :", len(result))
result.to_csv(dst, index=False, float_format="%.2f")
