"""
Calculs des KPI et agrégations pour le dashboard.
"""

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Calcule : Total Revenus, Total Dépenses, Solde Net, Taux d'Épargne.
    df attend les colonnes : montant.
    """
    revenus = df.loc[df["montant"] > 0, "montant"].sum()
    depenses = df.loc[df["montant"] < 0, "montant"].sum()  # négatif
    depenses_abs = abs(depenses)
    solde_net = revenus - depenses_abs
    taux_epargne = (solde_net / revenus * 100) if revenus > 0 else 0.0

    return {
        "total_revenus": round(revenus, 2),
        "total_depenses": round(depenses_abs, 2),
        "solde_net": round(solde_net, 2),
        "taux_epargne": round(taux_epargne, 2),
    }


def depenses_par_categorie(df: pd.DataFrame) -> pd.DataFrame:
    """Somme des dépenses (valeurs absolues) groupées par catégorie."""
    depenses = df[df["montant"] < 0].copy()
    depenses["montant_abs"] = depenses["montant"].abs()
    grouped = (
        depenses.groupby("categorie")["montant_abs"]
        .sum()
        .reset_index()
        .sort_values("montant_abs", ascending=False)
    )
    grouped.columns = ["categorie", "montant"]
    return grouped


def evolution_mensuelle(df: pd.DataFrame) -> pd.DataFrame:
    """Entrées vs Sorties agrégées par mois (pour le bar chart temporel)."""
    tmp = df.copy()
    tmp["mois"] = tmp["date"].dt.to_period("M").astype(str)
    tmp["revenu"] = tmp["montant"].apply(lambda m: m if m > 0 else 0)
    tmp["depense"] = tmp["montant"].apply(lambda m: abs(m) if m < 0 else 0)

    grouped = tmp.groupby("mois")[["revenu", "depense"]].sum().reset_index()
    return grouped.sort_values("mois")


def top_depenses(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N des plus grosses dépenses (pour la synthèse PDF)."""
    depenses = df[df["montant"] < 0].copy()
    depenses["montant_abs"] = depenses["montant"].abs()
    return depenses.sort_values("montant_abs", ascending=False).head(n)[
        ["date", "libelle", "categorie", "montant_abs"]
    ]


def repartition_hierarchique(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour le Treemap : niveau 1 = catégorie,
    niveau 2 = libellé de la transaction (sous-poste).
    """
    depenses = df[df["montant"] < 0].copy()
    depenses["montant_abs"] = depenses["montant"].abs()
    return depenses[["categorie", "libelle", "montant_abs"]]
