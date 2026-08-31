"""
Dashboard Web d'Analyse Financière & Budget Personnel
--------------------------------------------------------
Point d'entrée principal Streamlit.
Traitement 100% local en mémoire vive, sans persistance des données.
"""

import streamlit as st
import pandas as pd

from src.data_loader import load_raw_file, guess_column_mapping, normalize_dataframe
from src.categorizer import load_rules, categorize_dataframe, get_all_categories
from src.analytics import (
    compute_kpis,
    depenses_par_categorie,
    evolution_mensuelle,
    top_depenses,
    repartition_hierarchique,
)
from src.charts import donut_depenses_categorie, bar_entrees_sorties, treemap_repartition
from src.pdf_exporter import generate_pdf_report

st.set_page_config(
    page_title="Budget Dashboard",
    page_icon="💶",
    layout="wide",
)

RULES = load_rules("data/rules.json")

# ----------------------------------------------------------------------
# État de session
# ----------------------------------------------------------------------
if "df_categorized" not in st.session_state:
    st.session_state.df_categorized = None


def reset_session():
    st.session_state.df_categorized = None


# ----------------------------------------------------------------------
# SIDEBAR : Import, mapping, filtres
# ----------------------------------------------------------------------
with st.sidebar:
    st.title("💶 Budget Dashboard")
    st.caption("Analyse locale et confidentielle de vos finances")

    st.divider()
    st.subheader("1. Importer un fichier")

    uploaded_file = st.file_uploader(
        "Export bancaire (.csv, .tsv, .xlsx, .xls)",
        type=["csv", "tsv", "xlsx", "xls"],
        on_change=reset_session,
    )

    use_sample = st.checkbox("Utiliser le fichier de démonstration", value=False)

    raw_df = None
    if use_sample:
        raw_df = pd.read_csv("data/sample_bank_export.csv", sep=";")
    elif uploaded_file is not None:
        try:
            raw_df = load_raw_file(uploaded_file)
        except Exception as e:
            st.error(f"Erreur de lecture du fichier : {e}")

    mapping_ready = False
    if raw_df is not None:
        st.divider()
        st.subheader("2. Mapping des colonnes")

        guess = guess_column_mapping(raw_df)
        columns = list(raw_df.columns)

        def idx_or_zero(col_name):
            return columns.index(col_name) if col_name in columns else 0

        date_col = st.selectbox("Colonne Date", columns, index=idx_or_zero(guess["date_col"]))
        label_col = st.selectbox("Colonne Libellé", columns, index=idx_or_zero(guess["label_col"]))

        mode_montant = st.radio(
            "Format des montants",
            ["Colonne unique (+/-)", "Colonnes séparées Débit / Crédit"],
        )

        amount_col = debit_col = credit_col = None
        if mode_montant == "Colonne unique (+/-)":
            amount_col = st.selectbox(
                "Colonne Montant", columns, index=idx_or_zero(guess["amount_col"])
            )
        else:
            debit_col = st.selectbox(
                "Colonne Débit", columns, index=idx_or_zero(guess["debit_col"])
            )
            credit_col = st.selectbox(
                "Colonne Crédit", columns, index=idx_or_zero(guess["credit_col"])
            )

        mapping_ready = True

        if st.button("✅ Valider et analyser", type="primary", use_container_width=True):
            try:
                normalized = normalize_dataframe(
                    raw_df,
                    date_col=date_col,
                    label_col=label_col,
                    amount_col=amount_col,
                    debit_col=debit_col,
                    credit_col=credit_col,
                )
                st.session_state.df_categorized = categorize_dataframe(normalized, RULES)
                st.success(f"{len(normalized)} transactions importées.")
            except Exception as e:
                st.error(f"Erreur lors de la normalisation : {e}")

    st.divider()
    st.caption("🔒 Aucune donnée n'est envoyée à un serveur externe.")


# ----------------------------------------------------------------------
# CORPS PRINCIPAL DU DASHBOARD
# ----------------------------------------------------------------------
st.title("Tableau de bord financier")

if st.session_state.df_categorized is None:
    st.info(
        "👈 Importez un export bancaire (ou cochez « fichier de démonstration ») "
        "puis configurez le mapping des colonnes dans le panneau latéral."
    )
    st.stop()

df = st.session_state.df_categorized.copy()

# --- Filtres temporels et catégoriels ---
col_f1, col_f2 = st.columns([2, 3])
with col_f1:
    date_min, date_max = df["date"].min().date(), df["date"].max().date()
    date_range = st.date_input(
        "Plage de dates", value=(date_min, date_max), min_value=date_min, max_value=date_max
    )
with col_f2:
    categories_disponibles = sorted(df["categorie"].unique())
    categories_selection = st.multiselect(
        "Filtrer par catégories", categories_disponibles, default=categories_disponibles
    )

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    df = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]
df = df[df["categorie"].isin(categories_selection)]

if df.empty:
    st.warning("Aucune transaction ne correspond aux filtres sélectionnés.")
    st.stop()

st.divider()

# --- KPI Cards ---
kpis = compute_kpis(df)
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Revenus", f"{kpis['total_revenus']:.2f} €")
k2.metric("💸 Total Dépenses", f"{kpis['total_depenses']:.2f} €")
k3.metric(
    "📊 Solde Net",
    f"{kpis['solde_net']:.2f} €",
    delta=f"{kpis['solde_net']:.2f} €",
)
k4.metric("🏦 Taux d'Épargne", f"{kpis['taux_epargne']:.1f} %")

st.divider()

# --- Graphiques ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Répartition des dépenses")
    df_cat = depenses_par_categorie(df)
    if not df_cat.empty:
        st.plotly_chart(donut_depenses_categorie(df_cat), use_container_width=True)
    else:
        st.info("Aucune dépense sur la période sélectionnée.")

with col_g2:
    st.subheader("Entrées vs Sorties par mois")
    df_mensuel = evolution_mensuelle(df)
    st.plotly_chart(bar_entrees_sorties(df_mensuel), use_container_width=True)

st.subheader("Vue hiérarchique des dépenses")
df_hier = repartition_hierarchique(df)
if not df_hier.empty:
    st.plotly_chart(treemap_repartition(df_hier), use_container_width=True)
else:
    st.info("Aucune dépense à afficher en treemap.")

st.divider()

# --- Tableau éditable ---
st.subheader("Transactions (édition manuelle des catégories)")
categories_options = get_all_categories(RULES)

edited_df = st.data_editor(
    df[["date", "libelle", "montant", "categorie"]].sort_values("date", ascending=False),
    column_config={
        "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "libelle": st.column_config.TextColumn("Libellé", disabled=True),
        "montant": st.column_config.NumberColumn("Montant (€)", format="%.2f €", disabled=True),
        "categorie": st.column_config.SelectboxColumn("Catégorie", options=categories_options),
    },
    hide_index=True,
    use_container_width=True,
    key="editor_transactions",
)

# Répercuter les modifications de catégorie sur le DataFrame en session
if not edited_df.equals(df[["date", "libelle", "montant", "categorie"]].sort_values("date", ascending=False)):
    merge_cols = ["date", "libelle", "montant"]
    updated = st.session_state.df_categorized.merge(
        edited_df[merge_cols + ["categorie"]],
        on=merge_cols,
        how="left",
        suffixes=("", "_new"),
    )
    updated["categorie"] = updated["categorie_new"].combine_first(updated["categorie"])
    updated.drop(columns=["categorie_new"], inplace=True)
    st.session_state.df_categorized = updated

st.divider()

# --- Exports ---
st.subheader("Exporter les résultats")
col_e1, col_e2 = st.columns(2)

with col_e1:
    csv_bytes = df.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        "⬇️ Export CSV enrichi",
        data=csv_bytes,
        file_name="transactions_categorisees.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_e2:
    df_top = top_depenses(df, n=10)
    df_cat_pdf = depenses_par_categorie(df)
    pdf_bytes = generate_pdf_report(kpis, df_cat_pdf, df_top)
    st.download_button(
        "⬇️ Synthèse PDF professionnelle",
        data=pdf_bytes,
        file_name="synthese_budget.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
