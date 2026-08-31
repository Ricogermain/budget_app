"""
Moteur de Traitement & Catégorisation (Pandas)
------------------------------------------------
Applique un dictionnaire de règles par mots-clés (regex) pour classer
automatiquement chaque transaction dans une catégorie.
"""

import json
import re
import pandas as pd

DEFAULT_CATEGORY = "Non catégorisé"


def load_rules(rules_path: str = "data/rules.json") -> dict:
    """Charge le dictionnaire {categorie: [mots-clés]} depuis un fichier JSON."""
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_pattern(keywords: list) -> re.Pattern:
    escaped = [re.escape(k) for k in keywords if k]
    if not escaped:
        return None
    return re.compile("|".join(escaped), flags=re.IGNORECASE)


def categorize_transaction(libelle: str, rules: dict) -> str:
    """Retourne la première catégorie dont un mot-clé matche le libellé."""
    text = str(libelle).lower()
    for category, keywords in rules.items():
        pattern = _build_pattern(keywords)
        if pattern and pattern.search(text):
            return category
    return DEFAULT_CATEGORY


def categorize_dataframe(df: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """
    Ajoute une colonne 'categorie' au DataFrame normalisé (colonnes
    attendues : date, libelle, montant), sauf si déjà présente (édition
    manuelle conservée).
    """
    result = df.copy()
    if "categorie" not in result.columns:
        result["categorie"] = result["libelle"].apply(
            lambda lib: categorize_transaction(lib, rules)
        )
    # Type (revenu / dépense) déduit du signe du montant
    result["type"] = result["montant"].apply(lambda m: "Revenu" if m > 0 else "Depense")
    return result


def get_all_categories(rules: dict) -> list:
    """Liste triée de toutes les catégories connues + 'Non catégorisé'."""
    categories = sorted(rules.keys())
    if DEFAULT_CATEGORY not in categories:
        categories.append(DEFAULT_CATEGORY)
    return categories
