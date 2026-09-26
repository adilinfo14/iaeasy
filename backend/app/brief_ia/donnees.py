"""Mise en situation fictive : une marque d'articles de randonnée prépare ses soldes d'été.

Reprend l'esprit des connecteurs du squelette `ecommerce-brief-agent/connectors/*.py` (PIM,
pricing, calendrier promo, DAM, analytics) mais en dicts Python simples — pas besoin de
connecteurs séparés pour une démo à une seule mise en situation, contrairement au squelette qui
doit rester généralisable à n'importe quelle source réelle.
"""

from __future__ import annotations

CAMPAGNE = {
    "campaign_id": "SOLDES-ETE-2026",
    "nom": "Soldes d'été 2026",
    "date_debut": "2026-07-15",
    "date_fin": "2026-08-05",
    "theme": "Fraîcheur & montagne",
    "categories_ciblees": ["chaussures", "sacs à dos"],
    "type_remise": "percentage",
    "mentions_legales": [
        "Offre valable du 15/07 au 05/08/2026 dans la limite des stocks disponibles",
        "Prix de référence : voir conditions générales de vente",
    ],
}

# PIM : catalogue produit — prix "catalogue", pas forcément à jour sur la remise réelle.
PIM_PRODUITS = [
    {
        "sku": "CHZ-001",
        "nom": "Chaussure de randonnée Alpine Pro",
        "categorie": "chaussures",
        "prix": 129.90,
        "stock": "en_stock",
    },
    {
        "sku": "CHZ-002",
        "nom": "Chaussure de randonnée Alpine Light",
        "categorie": "chaussures",
        "prix": 99.90,
        "stock": "stock_faible",
    },
]

# Moteur de pricing : source de vérité sur la remise réelle appliquée en caisse — volontairement
# DIFFÉRENTE de ce qu'on pourrait supposer depuis le calendrier promo seul, pour illustrer
# pourquoi le mapping doit trancher plutôt que de laisser un LLM deviner.
PRICING_REMISES = {
    "CHZ-001": 30,
    "CHZ-002": 25,  # remise produit-spécifique, différente de la remise générale de la campagne
}

REMISE_GENERALE_CAMPAGNE = 30  # ce que le calendrier promo affiche par défaut

CHARTE_MARQUE_BRUTE = (
    "Ton de marque : dynamique, inclusif, jamais infantilisant. "
    "Palette : #0B3D2E (vert forêt), #F2E8CF (sable), #E07A5F (terracotta). "
    "Mots interdits : 'gratuit', 'miracle', 'meilleur du marché'. "
    "Mention obligatoire sur toute promotion : voir conditions en magasin et sur le site."
)

# Historique de performance — sert d'exemples pédagogiques au node retrieve_examples, à la place
# d'un vrai index Vertex AI Vector Search (non provisionné pour cette démo). Même principe déjà
# établi ailleurs sur iaeasy pour le nœud "base_vectorielle" du Constructeur : un petit corpus de
# démonstration intégré, tant qu'aucune vraie source n'est connectée.
EXEMPLES_BRIEFS_PASSES = [
    {
        "titre": "Soldes d'été 2025 — Alpine Pro",
        "resume": "Format 9:16, mise en situation réelle en montagne (pas de fond studio) : "
        "CTR 4,1%, nettement supérieur aux visuels en studio (2,3%).",
    },
    {
        "titre": "Collection hiver 2025 — sacs à dos",
        "resume": "Message court centré sur un seul bénéfice (légèreté) plutôt que sur toutes "
        "les caractéristiques techniques à la fois : conversion +18% vs. la version précédente.",
    },
]


def construire_contexte_campagne() -> dict:
    """Fusionne PIM + pricing + calendrier promo — la règle d'arbitrage est ici, pas dans le LLM :
    le moteur de pricing fait TOUJOURS autorité sur la remise réelle, jamais le PIM ni le
    calendrier promo (souvent en cache ou moins à jour)."""
    avertissements: list[str] = []
    produits = []
    for p in PIM_PRODUITS:
        remise = PRICING_REMISES.get(p["sku"])
        if remise is None:
            avertissements.append(
                f"Pas de remise trouvée dans le pricing engine pour {p['sku']}, "
                f"repli sur la remise générale de la campagne ({REMISE_GENERALE_CAMPAGNE}%)."
            )
            remise = REMISE_GENERALE_CAMPAGNE
        elif remise != REMISE_GENERALE_CAMPAGNE:
            avertissements.append(
                f"{p['sku']} a une remise spécifique ({remise}%) différente de la remise "
                f"générale affichée sur le calendrier promo ({REMISE_GENERALE_CAMPAGNE}%) — "
                "c'est la remise du pricing engine qui fait foi."
            )
        produits.append({**p, "remise_pct": remise})

    return {
        "campagne": CAMPAGNE,
        "produits": produits,
        "avertissements": avertissements,
    }
