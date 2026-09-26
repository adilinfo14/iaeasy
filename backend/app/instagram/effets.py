import random
from PIL import Image, ImageDraw

# Dupliqué depuis carrousel.py (mêmes valeurs) plutôt qu'importé — carrousel.py importe ce
# module pour générer son fond, un import inverse créerait un cycle. Trois tuples de couleur,
# le risque de divergence est nul.
NOIR = (10, 10, 10)
OR = (201, 168, 76)
OR_CLAIR = (226, 201, 122)
MUTED = (147, 147, 141)

# Palette Lesensia (produit distinct de TKonsulting) — valeurs exactes du brief de refonte de
# marque validé (lesensia.com) : Acier comme couleur fonctionnelle (continuité avec l'app/admin
# du produit), un point doré constant comme signature "IA" qui ne bascule jamais avec le thème.
# Fond bleu nuit propre à Lesensia (#0b1220, son propre thème sombre) plutôt que le noir
# TKonsulting — pour qu'un post Lesensia se distingue visuellement d'un post TKonsulting classique.
NAVY_LSN = (11, 18, 32)
ACIER_LSN = (77, 143, 239)  # variante claire du bleu Acier, pensée pour un fond sombre
GOLD_LSN = (224, 168, 37)  # point doré constant de la marque, cf. brief section 01

# Chaque effet est un fond (dessiné AVANT le texte, qui est composé par-dessus dans un calque
# séparé par rendre_slide/rendre_story — le texte reste donc toujours parfaitement lisible quel
# que soit l'effet choisi) construit à partir de primitives composables. Reproduit dans la même
# veine que les motifs déjà utilisés sur tkonsulting.fr (halo radial, particules flottantes,
# ligne diagonale, poussière d'or en coin) plutôt que des filtres photo Instagram classiques —
# nos visuels sont des cartes typographiques, pas des photos, donc "sépia/contraste" n'a pas de
# sens ici : ce qui varie, c'est l'ambiance de fond.


def _glow_radial(fond: Image.Image, cx: float, cy: float, rayon: float, couleur: tuple, intensite: float) -> None:
    """Halo doux via cercles concentriques d'opacité décroissante — pas de dégradé natif dans
    PIL, cette approximation par une quarantaine d'anneaux est visuellement indiscernable d'un
    vrai radial-gradient à cette échelle."""
    W, H = fond.size
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    n = 40
    r_max = rayon * min(W, H)
    for i in range(n, 0, -1):
        r = r_max * (i / n)
        alpha = int(intensite * 255 * (1 - i / n) ** 2)
        if alpha <= 0:
            continue
        draw.ellipse(
            [cx * W - r, cy * H - r * 0.75, cx * W + r, cy * H + r * 0.75],
            fill=couleur + (alpha,),
        )
    fond.alpha_composite(calque)


def _vignette(fond: Image.Image, intensite: float) -> None:
    """Assombrit les bords via le dégradé radial natif de PIL (0 au centre, 255 au bord), utilisé
    comme masque alpha d'un calque noir plein — direction inverse du halo, qui lui éclaircit le
    centre. Redimensionner le dégradé carré en WxH l'étire en ellipse, cohérent avec les
    radial-gradient elliptiques déjà utilisés sur tkonsulting.fr."""
    W, H = fond.size
    masque = Image.radial_gradient("L").resize((W, H)).point(lambda v: int(v * intensite))
    noir_plein = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    fond.paste(noir_plein, (0, 0), masque)


def _particules(fond: Image.Image, n: int, zone: tuple, taille: tuple, couleur: tuple, opacite_max: float, rng: random.Random) -> None:
    """Semis de petits points — reprend le motif de particules flottantes du hero de tkonsulting.fr."""
    W, H = fond.size
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    x0, y0, x1, y1 = zone
    for _ in range(n):
        x = rng.uniform(x0, x1) * W
        y = rng.uniform(y0, y1) * H
        r = rng.uniform(*taille) * min(W, H) / 1080
        alpha = int(rng.uniform(0.3, 1.0) * opacite_max * 255)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=couleur + (alpha,))
    fond.alpha_composite(calque)


def _ligne_diagonale(fond: Image.Image, cx: float, cy: float, longueur: float, angle_deg: float, couleur: tuple, opacite: float, epaisseur: int) -> None:
    W, H = fond.size
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    import math

    l = longueur * min(W, H)
    a = math.radians(angle_deg)
    dx, dy = math.cos(a) * l / 2, math.sin(a) * l / 2
    x, y = cx * W, cy * H
    draw.line([(x - dx, y - dy), (x + dx, y + dy)], fill=couleur + (int(opacite * 255),), width=epaisseur)
    fond.alpha_composite(calque)


def _grille_points(fond: Image.Image, espacement: int, couleur: tuple, opacite: float) -> None:
    W, H = fond.size
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    alpha = int(opacite * 255)
    r = max(1, espacement // 40)
    for x in range(0, W, espacement):
        for y in range(0, H, espacement):
            draw.ellipse([x - r, y - r, x + r, y + r], fill=couleur + (alpha,))
    fond.alpha_composite(calque)


def _grain(fond: Image.Image, n: int, couleur: tuple, opacite: float, rng: random.Random) -> None:
    W, H = fond.size
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        alpha = int(rng.uniform(0.2, 1.0) * opacite * 255)
        draw.point((x, y), fill=couleur + (alpha,))
    fond.alpha_composite(calque)


def _poussiere_coin(fond: Image.Image, coin: str, n: int, couleur: tuple) -> None:
    """Traînée de points dégressive dans un coin — reprend le motif déjà utilisé sur la section
    finale de tkonsulting.fr (près du monogramme)."""
    W, H = fond.size
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(calque)
    signe_x = -1 if "d" in coin else 1  # "d"roite vs "g"auche
    signe_y = -1 if "b" in coin else 1  # "b"as vs "h"aut
    ox = W * (0.92 if signe_x == -1 else 0.08)
    oy = H * (0.92 if signe_y == -1 else 0.08)
    for i in range(n):
        t = i / n
        r = (11 - 9 * t) * min(W, H) / 1080
        alpha = int(255 * (0.28 - 0.24 * t))
        x = ox + signe_x * -1 * t * 0.28 * W
        y = oy + signe_y * -1 * t * 0.28 * H
        draw.ellipse([x - r, y - r, x + r, y + r], fill=couleur + (max(alpha, 0),))
    fond.alpha_composite(calque)


def _fond_base(WS: int, HS: int, couleur: tuple = NOIR) -> Image.Image:
    return Image.new("RGBA", (WS, HS), couleur + (255,))


# Chaque preset est une fonction (WS, HS, rng) -> Image RGBA, construite à partir des primitives
# ci-dessus. 50 identités nommées, organisées en 5 familles pour l'affichage groupé côté IHM.
def _preset_halo(cx, cy, rayon, intensite, couleur=OR, fond_couleur=NOIR):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS, fond_couleur)
        _glow_radial(fond, cx, cy, rayon, couleur, intensite)
        return fond
    return f


def _preset_halo_particules(cx, cy, rayon, intensite, n_particules, couleur=OR, couleur_particules=None, fond_couleur=NOIR):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS, fond_couleur)
        _glow_radial(fond, cx, cy, rayon, couleur, intensite)
        _particules(fond, n_particules, (0.1, 0.05, 0.9, 0.95), (1, 6), couleur_particules or OR_CLAIR, 0.8, rng)
        return fond
    return f


def _preset_vignette_grille(intensite_vignette, espacement, couleur=OR):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS)
        _grille_points(fond, espacement, couleur, 0.05)
        _vignette(fond, intensite_vignette)
        return fond
    return f


def _preset_ligne_halo(angle, cx, cy, rayon, intensite, couleur=OR, fond_couleur=NOIR):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS, fond_couleur)
        _glow_radial(fond, cx, cy, rayon, couleur, intensite * 0.7)
        _ligne_diagonale(fond, 0.5, 0.5, 0.9, angle, couleur, 0.12, max(1, WS // 540))
        return fond
    return f


def _preset_coin_poussiere(coin, n, couleur=OR, fond_couleur=NOIR):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS, fond_couleur)
        _poussiere_coin(fond, coin, n, couleur)
        return fond
    return f


def _preset_grain_vignette(n_grain, intensite_vignette, couleur=MUTED):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS)
        _grain(fond, n_grain, couleur, 0.5, rng)
        _vignette(fond, intensite_vignette)
        return fond
    return f


def _preset_complet(cx, cy, rayon, intensite, angle, coin, n_poussiere, couleur=OR, fond_couleur=NOIR):
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS, fond_couleur)
        _glow_radial(fond, cx, cy, rayon, couleur, intensite)
        _ligne_diagonale(fond, 0.5, 0.5, 0.85, angle, couleur, 0.1, max(1, WS // 600))
        _poussiere_coin(fond, coin, n_poussiere, couleur)
        return fond
    return f


def _preset_lesensia_signature(cx, cy, rayon, intensite, n_points_or, coin_or):
    """Motif propre à Lesensia : halo Acier (couleur fonctionnelle de la marque) + poussière
    dorée dans un coin, écho du 'point doré constant' du wordmark — jamais teinté en Acier, le
    doré reste la signature IA fixe de la marque quel que soit le thème (cf. brief section 01)."""
    def f(WS, HS, rng):
        fond = _fond_base(WS, HS, NAVY_LSN)
        _glow_radial(fond, cx, cy, rayon, ACIER_LSN, intensite)
        _poussiere_coin(fond, coin_or, n_points_or, GOLD_LSN)
        return fond
    return f


PRESETS = {
    # Halos — un seul foyer de lumière, sobre
    "aube": {"categorie": "Halos", "label": "Aube", "fn": _preset_halo(0.5, 0.35, 0.55, 0.55)},
    "crepuscule": {"categorie": "Halos", "label": "Crépuscule", "fn": _preset_halo(0.5, 0.7, 0.5, 0.5)},
    "zenith": {"categorie": "Halos", "label": "Zénith", "fn": _preset_halo(0.5, 0.15, 0.6, 0.45)},
    "eclipse": {"categorie": "Halos", "label": "Éclipse", "fn": _preset_halo(0.5, 0.5, 0.35, 0.7)},
    "horizon-gauche": {"categorie": "Halos", "label": "Horizon gauche", "fn": _preset_halo(0.15, 0.5, 0.5, 0.5)},
    "horizon-droit": {"categorie": "Halos", "label": "Horizon droit", "fn": _preset_halo(0.85, 0.5, 0.5, 0.5)},
    "lueur-douce": {"categorie": "Halos", "label": "Lueur douce", "fn": _preset_halo(0.5, 0.5, 0.75, 0.3)},
    "coeur-ardent": {"categorie": "Halos", "label": "Cœur ardent", "fn": _preset_halo(0.5, 0.5, 0.3, 0.85)},
    "phare": {"categorie": "Halos", "label": "Phare", "fn": _preset_halo(0.5, 0.05, 0.7, 0.5)},
    "profondeur": {"categorie": "Halos", "label": "Profondeur", "fn": _preset_halo(0.5, 0.95, 0.7, 0.45)},

    # Halo + particules — atmosphère vivante
    "constellation": {"categorie": "Atmosphère", "label": "Constellation", "fn": _preset_halo_particules(0.6, 0.3, 0.55, 0.5, 14)},
    "poussiere-or": {"categorie": "Atmosphère", "label": "Poussière d'or", "fn": _preset_halo_particules(0.5, 0.5, 0.5, 0.4, 20)},
    "nebuleuse": {"categorie": "Atmosphère", "label": "Nébuleuse", "fn": _preset_halo_particules(0.4, 0.6, 0.6, 0.5, 10)},
    "essaim": {"categorie": "Atmosphère", "label": "Essaim doré", "fn": _preset_halo_particules(0.5, 0.4, 0.45, 0.45, 26)},
    "brume-doree": {"categorie": "Atmosphère", "label": "Brume dorée", "fn": _preset_halo_particules(0.5, 0.5, 0.65, 0.35, 8)},
    "voie-lactee": {"categorie": "Atmosphère", "label": "Voie lactée", "fn": _preset_halo_particules(0.5, 0.2, 0.5, 0.4, 32)},
    "etincelles": {"categorie": "Atmosphère", "label": "Étincelles", "fn": _preset_halo_particules(0.7, 0.7, 0.4, 0.5, 18)},
    "reverie": {"categorie": "Atmosphère", "label": "Rêverie", "fn": _preset_halo_particules(0.3, 0.4, 0.55, 0.4, 12)},
    "vent-de-sable": {"categorie": "Atmosphère", "label": "Vent de sable doré", "fn": _preset_halo_particules(0.5, 0.6, 0.6, 0.35, 24)},
    "aurore": {"categorie": "Atmosphère", "label": "Aurore", "fn": _preset_halo_particules(0.5, 0.25, 0.6, 0.55, 16)},

    # Structure — grille, vignette, motifs géométriques sobres
    "minuit": {"categorie": "Structure", "label": "Minuit", "fn": _preset_vignette_grille(0.55, 60)},
    "quadrillage-fin": {"categorie": "Structure", "label": "Quadrillage fin", "fn": _preset_vignette_grille(0.3, 40)},
    "quadrillage-large": {"categorie": "Structure", "label": "Quadrillage large", "fn": _preset_vignette_grille(0.4, 90)},
    "cadre-sombre": {"categorie": "Structure", "label": "Cadre sombre", "fn": _preset_vignette_grille(0.7, 70)},
    "trame-legere": {"categorie": "Structure", "label": "Trame légère", "fn": _preset_vignette_grille(0.2, 50)},
    "architecture": {"categorie": "Structure", "label": "Architecture", "fn": _preset_vignette_grille(0.45, 55)},
    "geometrie-sobre": {"categorie": "Structure", "label": "Géométrie sobre", "fn": _preset_vignette_grille(0.35, 45)},
    "reseau": {"categorie": "Structure", "label": "Réseau", "fn": _preset_vignette_grille(0.5, 65)},
    "confidentiel": {"categorie": "Structure", "label": "Confidentiel", "fn": _preset_vignette_grille(0.65, 75)},
    "epure": {"categorie": "Structure", "label": "Épuré", "fn": _preset_vignette_grille(0.15, 80)},

    # Ligne + halo — mouvement diagonal, dynamique
    "trajectoire": {"categorie": "Dynamique", "label": "Trajectoire", "fn": _preset_ligne_halo(-35, 0.5, 0.5, 0.5, 0.5)},
    "envol": {"categorie": "Dynamique", "label": "Envol", "fn": _preset_ligne_halo(-55, 0.4, 0.4, 0.5, 0.45)},
    "elan": {"categorie": "Dynamique", "label": "Élan", "fn": _preset_ligne_halo(20, 0.6, 0.4, 0.5, 0.5)},
    "chute-doree": {"categorie": "Dynamique", "label": "Chute dorée", "fn": _preset_ligne_halo(70, 0.5, 0.3, 0.45, 0.5)},
    "traverse": {"categorie": "Dynamique", "label": "Traversée", "fn": _preset_ligne_halo(0, 0.5, 0.5, 0.5, 0.4)},
    "ascension": {"categorie": "Dynamique", "label": "Ascension", "fn": _preset_ligne_halo(-90, 0.5, 0.6, 0.5, 0.45)},
    "diagonale-nette": {"categorie": "Dynamique", "label": "Diagonale nette", "fn": _preset_ligne_halo(-30, 0.5, 0.5, 0.4, 0.6)},
    "sillage": {"categorie": "Dynamique", "label": "Sillage", "fn": _preset_ligne_halo(-40, 0.35, 0.65, 0.55, 0.4)},
    "flux": {"categorie": "Dynamique", "label": "Flux", "fn": _preset_ligne_halo(15, 0.65, 0.35, 0.5, 0.45)},
    "cap": {"categorie": "Dynamique", "label": "Cap", "fn": _preset_ligne_halo(-45, 0.55, 0.45, 0.6, 0.4)},

    # Coins — poussière d'or dans un angle, discret
    "signature-bd": {"categorie": "Signature", "label": "Signature bas-droite", "fn": _preset_coin_poussiere("bd", 9)},
    "signature-bg": {"categorie": "Signature", "label": "Signature bas-gauche", "fn": _preset_coin_poussiere("bg", 9)},
    "signature-hd": {"categorie": "Signature", "label": "Signature haut-droite", "fn": _preset_coin_poussiere("hd", 9)},
    "signature-hg": {"categorie": "Signature", "label": "Signature haut-gauche", "fn": _preset_coin_poussiere("hg", 9)},
    "sceau": {"categorie": "Signature", "label": "Sceau discret", "fn": _preset_coin_poussiere("bd", 6)},
    "empreinte": {"categorie": "Signature", "label": "Empreinte", "fn": _preset_coin_poussiere("hg", 12)},
    "grain-doux": {"categorie": "Signature", "label": "Grain doux", "fn": _preset_grain_vignette(1400, 0.25)},
    "grain-marque": {"categorie": "Signature", "label": "Grain marqué", "fn": _preset_grain_vignette(2600, 0.4)},
    "pellicule": {"categorie": "Signature", "label": "Pellicule", "fn": _preset_grain_vignette(2000, 0.5)},
    "sobre": {"categorie": "Signature", "label": "Sobre (sans effet)", "fn": lambda WS, HS, rng: _fond_base(WS, HS)},

    # Complets — combinaison des trois primitives, plus caractériels
    "premiere-classe": {"categorie": "Signature complète", "label": "Première classe", "fn": _preset_complet(0.5, 0.35, 0.55, 0.5, -35, "bd", 9)},
    "conclave": {"categorie": "Signature complète", "label": "Conclave", "fn": _preset_complet(0.5, 0.5, 0.4, 0.6, 0, "hg", 7)},
    "manifeste": {"categorie": "Signature complète", "label": "Manifeste", "fn": _preset_complet(0.4, 0.3, 0.5, 0.45, -50, "bg", 10)},
    "reference": {"categorie": "Signature complète", "label": "Référence", "fn": _preset_complet(0.6, 0.4, 0.45, 0.55, 25, "hd", 8)},
    "distinction": {"categorie": "Signature complète", "label": "Distinction", "fn": _preset_complet(0.5, 0.6, 0.6, 0.4, -20, "bd", 11)},

    # Lesensia — palette propre au produit (Acier + point doré), pas TKonsulting : à utiliser
    # quand le post parle spécifiquement de Lesensia, pour que le visuel se distingue de la
    # charte noir & or habituelle. Couleurs exactes du brief de refonte de marque lesensia.com.
    "lsn-acier-central": {"categorie": "Lesensia", "label": "Acier central", "fn": _preset_lesensia_signature(0.5, 0.4, 0.55, 0.55, 9, "bd")},
    "lsn-acier-haut": {"categorie": "Lesensia", "label": "Acier en hauteur", "fn": _preset_lesensia_signature(0.5, 0.15, 0.6, 0.5, 7, "hg")},
    "lsn-signature-doree": {"categorie": "Lesensia", "label": "Signature dorée", "fn": _preset_lesensia_signature(0.5, 0.5, 0.4, 0.45, 12, "bg")},
    "lsn-horizon": {"categorie": "Lesensia", "label": "Horizon Acier", "fn": _preset_halo(0.5, 0.65, 0.6, 0.5, ACIER_LSN, NAVY_LSN)},
    "lsn-precision": {"categorie": "Lesensia", "label": "Précision", "fn": _preset_ligne_halo(-35, 0.5, 0.45, 0.5, 0.5, ACIER_LSN, NAVY_LSN)},
    "lsn-constellation": {"categorie": "Lesensia", "label": "Données terrain", "fn": _preset_halo_particules(0.5, 0.35, 0.5, 0.45, 16, ACIER_LSN, GOLD_LSN, NAVY_LSN)},
    "lsn-sceau": {"categorie": "Lesensia", "label": "Sceau Acier", "fn": _preset_coin_poussiere("bd", 8, ACIER_LSN, NAVY_LSN)},
    "lsn-fondations": {"categorie": "Lesensia", "label": "Fondations", "fn": _preset_halo(0.5, 0.85, 0.7, 0.4, ACIER_LSN, NAVY_LSN)},
}

DEFAUT = "aube"


def choisir_aleatoire(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    return rng.choice(list(PRESETS.keys()))


def generer_fond(WS: int, HS: int, cle: str, graine: int | None = None) -> Image.Image:
    preset = PRESETS.get(cle, PRESETS[DEFAUT])
    rng = random.Random(graine)
    return preset["fn"](WS, HS, rng)
