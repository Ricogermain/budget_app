"""
Génération des graphiques interactifs (Plotly Express).
"""

import plotly.express as px
import pandas as pd

from src.currency import format_ariary

COLOR_SEQUENCE = px.colors.qualitative.Set2


def donut_depenses_categorie(df_categorie: pd.DataFrame):
    """Donut Chart : répartition des dépenses par poste (% et Ar)."""
    fig = px.pie(
        df_categorie,
        names="categorie",
        values="montant",
        hole=0.55,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_traces(
        textposition="outside",
        texttemplate="%{label}<br>%{percent}",
        customdata=df_categorie["montant"].apply(format_ariary),
        hovertemplate="%{label}<br>%{customdata}<extra></extra>",
    )
    fig.update_layout(
        showlegend=True,
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )
    return fig


def bar_entrees_sorties(df_mensuel: pd.DataFrame):
    """Bar Chart : évolution temporelle Entrées vs Sorties par mois."""
    df_melted = df_mensuel.melt(
        id_vars="mois",
        value_vars=["revenu", "depense"],
        var_name="type",
        value_name="montant",
    )
    df_melted["type"] = df_melted["type"].map(
        {"revenu": "Entrées", "depense": "Sorties"}
    )

    fig = px.bar(
        df_melted,
        x="mois",
        y="montant",
        color="type",
        barmode="group",
        color_discrete_map={"Entrées": "#2E7D6B", "Sorties": "#D9534F"},
        labels={"mois": "Mois", "montant": "Montant (Ar)", "type": ""},
    )
    fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), legend_title_text="")
    return fig


def treemap_repartition(df_hierarchique: pd.DataFrame):
    """Treemap : vue hiérarchique catégorie -> sous-poste (libellé)."""
    fig = px.treemap(
        df_hierarchique,
        path=["categorie", "libelle"],
        values="montant_abs",
        color="categorie",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_traces(
        texttemplate="%{label}<br>%{value:,.0f} Ar",
        hovertemplate="%{label}<br>%{value:,.0f} Ar<extra></extra>",
    )
    fig.update_layout(margin=dict(t=30, b=10, l=10, r=10))
    return fig
