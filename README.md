# Budget Dashboard — Analyse Financière Personnelle

Dashboard web interactif pour analyser vos exports bancaires (CSV/Excel)
en quelques secondes. Traitement **100% local**, aucune donnée envoyée
à un serveur externe.

## Installation

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur
(par défaut sur http://localhost:8501).

## Utilisation

1. Dans la barre latérale, importez votre export bancaire
   (`.csv`, `.tsv`, `.xlsx`, `.xls`) — ou cochez **« Utiliser le fichier
   de démonstration »** pour tester avec des données factices.
2. Vérifiez/ajustez le **mapping des colonnes** (Date, Libellé, Montant
   ou Débit/Crédit séparés), puis cliquez sur **« Valider et analyser »**.
3. Consultez les **KPI**, les **graphiques interactifs** (donut,
   évolution mensuelle, treemap) et filtrez par date ou catégorie.
4. Corrigez manuellement une catégorie directement dans le **tableau
   éditable** si besoin.
5. Exportez vos résultats en **CSV enrichi** ou en **synthèse PDF**.

## Structure du projet

```
budget_app/
├── .streamlit/config.toml     # Thème visuel Streamlit
├── data/
│   ├── rules.json             # Règles de catégorisation par mots-clés
│   └── sample_bank_export.csv # Fichier de démonstration
├── src/
│   ├── data_loader.py         # Import & mapping dynamique des colonnes
│   ├── categorizer.py         # Moteur de catégorisation par règles
│   ├── analytics.py           # Calculs des KPI et agrégations
│   ├── charts.py              # Graphiques Plotly Express
│   └── pdf_exporter.py        # Génération du rapport PDF (FPDF2)
├── app.py                     # Point d'entrée Streamlit
└── requirements.txt
```

## Personnaliser les catégories

Modifiez `data/rules.json` pour ajouter vos propres mots-clés :

```json
{
  "Ma Categorie": ["mot-cle-1", "mot-cle-2"]
}
```

Chaque transaction est classée dans la **première catégorie** dont un
mot-clé apparaît (insensible à la casse) dans son libellé.
