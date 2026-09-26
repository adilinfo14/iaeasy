"""Schémas Pydantic — sortie forcée des appels Gemini (structured output) et forme des
événements SSE envoyés au frontend. Sous-ensemble du squelette `ecommerce-brief-agent`, réduit à
ce que l'IHM affiche réellement.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CharteMarque(BaseModel):
    ton: str = Field(description="Ton de la marque, en une phrase")
    palette: list[str] = Field(description="Couleurs de la charte, en hexadécimal")
    mots_interdits: list[str] = Field(default_factory=list)
    mention_obligatoire: str = Field(description="Mention légale obligatoire sur toute promotion")


class BriefCreatif(BaseModel):
    titre: str
    objectif: str
    message_cle: str
    produits_vedettes: list[str] = Field(description="SKUs mis en avant — doivent exister dans le contexte")
    ton: str
    mentions_obligatoires: list[str]
    formats: list[str] = Field(description='ex: ["9:16", "1:1", "16:9"]')
    duree_secondes: int
    appel_action: str
    deadline: str = Field(description="Date limite, format AAAA-MM-JJ, avant le début de la promotion")


class AvisRelecteur(BaseModel):
    score: int = Field(ge=1, le=5)
    valide: bool
    remarques: list[str] = Field(default_factory=list)
