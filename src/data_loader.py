"""
Module d'Importation & Normalisation
-------------------------------------
Gère le chargement multi-format (.csv, .tsv, .xlsx, .xls) et la détection
automatique des colonnes (Date, Libellé, Montant / Débit-Crédit).
"""

import io
import pandas as pd

SUPPORTED_EXTENSIONS = (".csv", ".tsv", ".xlsx", ".xls")

# Mots-clés utilisés pour deviner automatiquement le rôle de chaque colonne
DATE_HINTS = ["date", "date operation", "date transaction", "value date"]
LABEL_HINTS = ["libelle", "libellé", "description", "designation", "detail", "operation"]
AMOUNT_HINTS = ["montant", "amount", "solde", "valeur"]
DEBIT_HINTS = ["debit", "débit", "sortie", "depense", "dépense"]
CREDIT_HINTS = ["credit", "crédit", "entree", "entrée", "recette"]


def load_raw_file(uploaded_file) -> pd.DataFrame:
    """
    Charge un fichier CSV/TSV/Excel uploadé (objet Streamlit UploadedFile)
    et retourne un DataFrame brut (sans normalisation).
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return _read_csv_flexible(uploaded_file, sep=None)
    elif filename.endswith(".tsv"):
        return _read_csv_flexible(uploaded_file, sep="\t")
    elif filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError(
            f"Format de fichier non supporté : {filename}. "
            f"Formats acceptés : {', '.join(SUPPORTED_EXTENSIONS)}"
        )


def _read_csv_flexible(uploaded_file, sep):
    """
    Lit un CSV/TSV en tentant de détecter automatiquement le séparateur
    (virgule ou point-virgule sont fréquents dans les exports bancaires FR).
    """
    raw_bytes = uploaded_file.read()
    text = raw_bytes.decode("utf-8-sig", errors="replace")

    if sep is None:
        # Détection simple : le séparateur le plus fréquent sur la première ligne
        first_line = text.splitlines()[0] if text.splitlines() else ""
        sep = ";" if first_line.count(";") >= first_line.count(",") else ","

    return pd.read_csv(io.StringIO(text), sep=sep)


def guess_column_mapping(df: pd.DataFrame) -> dict:
    """
    Tente de deviner automatiquement quelle colonne correspond à
    Date / Libellé / Montant (ou Débit + Crédit séparés).
    Retourne un dict prêt à préremplir les menus déroulants Streamlit.
    """
    columns_lower = {c: str(c).strip().lower() for c in df.columns}

    def find_match(hints):
        for col, low in columns_lower.items():
            if any(hint in low for hint in hints):
                return col
        return None

    mapping = {
        "date_col": find_match(DATE_HINTS),
        "label_col": find_match(LABEL_HINTS),
        "amount_col": find_match(AMOUNT_HINTS),
        "debit_col": find_match(DEBIT_HINTS),
        "credit_col": find_match(CREDIT_HINTS),
    }
    return mapping


def normalize_dataframe(
    df: pd.DataFrame,
    date_col: str,
    label_col: str,
    amount_col: str = None,
    debit_col: str = None,
    credit_col: str = None,
) -> pd.DataFrame:
    """
    Construit un DataFrame normalisé à 3 colonnes : date, libelle, montant.
    - date au format datetime (ISO)
    - montant en float (dépenses négatives, revenus positifs)
    Gère le cas "montant unique" ET le cas "débit/crédit séparés".
    """
    result = pd.DataFrame()

    result["date"] = _parse_dates(df[date_col])
    result["libelle"] = df[label_col].astype(str).str.strip()

    if amount_col:
        result["montant"] = _to_numeric(df[amount_col])
    elif debit_col and credit_col:
        debit = _to_numeric(df[debit_col]).fillna(0).abs()
        credit = _to_numeric(df[credit_col]).fillna(0).abs()
        result["montant"] = credit - debit
    else:
        raise ValueError(
            "Mapping incomplet : fournir soit 'amount_col', "
            "soit 'debit_col' + 'credit_col'."
        )

    total_rows = len(result)
    valid_dates = result["date"].notna().sum()
    valid_montants = result["montant"].notna().sum()

    result = result.dropna(subset=["date", "montant"]).reset_index(drop=True)

    if result.empty:
        # Diagnostic précis pour aider l'utilisateur à corriger le mapping
        if total_rows == 0:
            raise ValueError("Le fichier importé ne contient aucune ligne de données.")
        if valid_dates == 0:
            raise ValueError(
                f"Impossible d'interpréter la colonne Date ('{date_col}'). "
                "Vérifiez qu'elle contient bien des dates (ex: 2026-08-01 ou 01/08/2026)."
            )
        if valid_montants == 0:
            source = amount_col or f"{debit_col} / {credit_col}"
            raise ValueError(
                f"Impossible d'interpréter les montants de la colonne '{source}'. "
                "Vérifiez le format sélectionné (colonne unique +/- ou Débit/Crédit "
                "séparés) et que les valeurs sont bien numériques."
            )
        raise ValueError(
            "Aucune ligne valide après normalisation : la colonne Date et la "
            "colonne Montant ne sont jamais renseignées en même temps sur la "
            "même ligne. Vérifiez le mapping des colonnes."
        )

    return result


def _parse_dates(series: pd.Series) -> pd.Series:
    """
    Parse une colonne de dates en gérant les deux formats les plus courants
    dans les exports bancaires : ISO (YYYY-MM-DD, non ambigu) et
    français (DD/MM/YYYY, jour en premier). On tente d'abord le format ISO
    strict ; les valeurs non reconnues retombent sur un parsing dayfirst.
    """
    text = series.astype(str).str.strip()
    parsed = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(
            text[missing], errors="coerce", dayfirst=True
        )
    return parsed


def _to_numeric(series: pd.Series) -> pd.Series:
    """Nettoie une colonne de montants (espaces, virgules décimales, symboles Ar/€)."""
    cleaned = (
        series.astype(str)
        .str.replace("Ar", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("\u202f", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")
