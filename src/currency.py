"""
Formatage monétaire pour l'Ariary (MGA) — devise nationale de Madagascar.
L'Ariary ne se subdivise pas en pratique (l'iraimbilanja n'est plus utilisé
couramment), les montants sont donc affichés arrondis, sans décimales,
avec un séparateur de milliers en espace : ex. "2 400 000 Ar".
"""


def format_ariary(amount: float) -> str:
    """Formate un montant en Ariary : '2 400 000 Ar' (arrondi à l'unité)."""
    rounded = round(amount)
    formatted = f"{rounded:,}".replace(",", " ")
    return f"{formatted} Ar"


def format_ariary_signed(amount: float) -> str:
    """Idem que format_ariary mais conserve un signe explicite +/- devant."""
    sign = "+" if amount > 0 else ""
    return f"{sign}{format_ariary(amount)}"
