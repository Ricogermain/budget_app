"""
Génération & Exportation de Rapports (FPDF2)
-----------------------------------------------
Compile un rapport PDF A4 récapitulatif : KPI, Top 10 des dépenses,
répartition budgétaire par catégorie.
"""

from datetime import datetime
from fpdf import FPDF


class BudgetReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(46, 125, 107)
        self.cell(0, 12, "Synthese Budget Personnel", ln=True, align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(
            0, 6,
            f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
            ln=True, align="C"
        )
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _clean(text: str) -> str:
    """FPDF2 core fonts (Helvetica) sont en latin-1 : on neutralise les
    caractères non supportés (ex: emoji, symboles rares) sans planter."""
    return str(text).encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf_report(kpis: dict, df_categorie, df_top_depenses) -> bytes:
    """
    kpis : dict issu de analytics.compute_kpis()
    df_categorie : DataFrame [categorie, montant] issu de depenses_par_categorie()
    df_top_depenses : DataFrame [date, libelle, categorie, montant_abs]
    Retourne les octets du PDF, prêts pour st.download_button.
    """
    pdf = BudgetReportPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    # --- Section KPI ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 10, "Indicateurs cles", ln=True)

    pdf.set_font("Helvetica", "", 11)
    kpi_lines = [
        ("Total Revenus", f"{kpis['total_revenus']:.2f} EUR"),
        ("Total Depenses", f"{kpis['total_depenses']:.2f} EUR"),
        ("Solde Net", f"{kpis['solde_net']:.2f} EUR"),
        ("Taux d'Epargne", f"{kpis['taux_epargne']:.1f} %"),
    ]
    for label, value in kpi_lines:
        pdf.cell(70, 8, _clean(label), border=0)
        pdf.cell(0, 8, _clean(value), ln=True)

    pdf.ln(6)

    # --- Section répartition budgétaire ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Repartition budgetaire par categorie", ln=True)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(244, 246, 245)
    pdf.cell(100, 8, "Categorie", border=1, fill=True)
    pdf.cell(60, 8, "Montant (EUR)", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 10)
    for _, row in df_categorie.iterrows():
        pdf.cell(100, 7, _clean(row["categorie"]), border=1)
        pdf.cell(60, 7, f"{row['montant']:.2f}", border=1, ln=True)

    pdf.ln(6)

    # --- Section Top 10 dépenses ---
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Top 10 des plus grosses depenses", ln=True)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(244, 246, 245)
    pdf.cell(30, 8, "Date", border=1, fill=True)
    pdf.cell(80, 8, "Libelle", border=1, fill=True)
    pdf.cell(40, 8, "Categorie", border=1, fill=True)
    pdf.cell(30, 8, "Montant", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 9)
    for _, row in df_top_depenses.iterrows():
        date_str = row["date"].strftime("%d/%m/%Y") if hasattr(row["date"], "strftime") else str(row["date"])
        pdf.cell(30, 7, _clean(date_str), border=1)
        pdf.cell(80, 7, _clean(str(row["libelle"])[:38]), border=1)
        pdf.cell(40, 7, _clean(row["categorie"]), border=1)
        pdf.cell(30, 7, f"{row['montant_abs']:.2f} EUR", border=1, ln=True)

    return bytes(pdf.output())
