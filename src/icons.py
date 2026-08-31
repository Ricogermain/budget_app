"""
Icônes SVG (traits, style Material/Feather) utilisées à la place des emojis
dans l'ensemble du dashboard. Chaque icône est un template SVG minimal,
coloré dynamiquement via le paramètre `color`.
"""

_ICON_PATHS = {
    # Flèche montante dans un cercle -> Revenus
    "income": '<circle cx="12" cy="12" r="9"/><path d="M8 13l4-4 4 4"/><path d="M12 9v7"/>',
    # Flèche descendante dans un cercle -> Dépenses
    "expense": '<circle cx="12" cy="12" r="9"/><path d="M8 11l4 4 4-4"/><path d="M12 15V8"/>',
    # Balance / solde
    "balance": '<path d="M12 3v18"/><path d="M5 8l-3 6a3 3 0 0 0 6 0l-3-6z"/>'
               '<path d="M19 8l-3 6a3 3 0 0 0 6 0l-3-6z"/><path d="M5 8h14"/>'
               '<path d="M8 21h8"/>',
    # Tirelire -> Taux d'épargne
    "savings": '<path d="M19 9V7a2 2 0 0 0-2-2h-1.5a5.5 5.5 0 0 0-10.9 1H4a1 1 0 0 0-1 1v2'
               'l2 1v2.5a4.5 4.5 0 0 0 3 4.24V19a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-.5h2V19'
               'a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-2.5A5.5 5.5 0 0 0 19 12V9z"/>'
               '<circle cx="15.5" cy="8.5" r=".6" fill="currentColor" stroke="none"/>',
    # Cadenas -> confidentialité
    "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    # Flèche vers le bas dans un cadre -> téléchargement
    "download": '<path d="M12 4v11"/><path d="M8 11l4 4 4-4"/><path d="M5 19h14"/>',
    # Coche dans un cercle -> validation
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/>',
    # Document / fichier -> PDF
    "document": '<path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>'
                '<path d="M14 3v5h5"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    # Filtre -> filtres de dates/catégories
    "filter": '<path d="M4 5h16l-6 8v6l-4-2v-4z"/>',
    # Portefeuille -> en-tête de l'application
    "wallet": '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18"/>'
              '<circle cx="16" cy="14" r="1.4" fill="currentColor" stroke="none"/>',
    # Flèche retour -> message d'invite initial
    "arrow_back": '<path d="M19 12H5"/><path d="M11 6l-6 6 6 6"/>',
}


def render_kpi_card(icon_name: str, label: str, value: str, accent: str = "#2E7D6B") -> str:
    """
    Construit le HTML d'une carte KPI avec une vraie icône SVG (pas d'emoji),
    prête à être injectée via st.markdown(html, unsafe_allow_html=True).
    """
    icon_html = get_icon_svg(icon_name, size=22, color=accent)
    return f"""
    <div style="
        border:1px solid rgba(128,128,128,0.25);
        border-radius:10px;
        padding:14px 16px;
        display:flex;
        align-items:center;
        gap:12px;
    ">
        <div style="
            background:{accent}22;
            border-radius:8px;
            width:38px;height:38px;
            display:flex;align-items:center;justify-content:center;
            flex-shrink:0;
        ">{icon_html}</div>
        <div>
            <div style="font-size:0.8rem;opacity:0.7;margin-bottom:2px;">{label}</div>
            <div style="font-size:1.25rem;font-weight:600;">{value}</div>
        </div>
    </div>
    """


def get_icon_svg(name: str, size: int = 20, color: str = "currentColor") -> str:
    """
    Retourne le markup SVG complet (chaîne HTML) pour l'icône demandée,
    prêt à être injecté via st.markdown(..., unsafe_allow_html=True).
    """
    path = _ICON_PATHS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle;display:inline-block">{path}</svg>'
    )
