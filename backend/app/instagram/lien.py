import json
from datetime import datetime
from pathlib import Path

from ..core.config import settings

# Journal des clics sur les liens "en bio" — un compte pro Instagram peut afficher plusieurs
# liens externes, donc chaque entrée est (jour calendaire, clé du lien) avec un compteur, pas un
# log par clic (pas besoin de granularité plus fine, et ça garde le fichier petit sur le long terme).
# Instagram ne transmet aucune identité dans un clic — seuls l'IP et le user-agent sont visibles
# côté serveur, et l'IP ne permet pas de remonter à une personne. On agrège donc seulement deux
# signaux anonymes (type d'appareil, heure de la journée) plutôt que de tenter un fingerprinting.
_FICHIER = Path(settings.data_dir) / "instagram_lien_bio_historique.json"
_MAX_ENTREES = 800
_MOTS_CLES_MOBILE = ("Mobile", "Android", "iPhone", "iPad")


def _defaut() -> dict:
    return {"clics": [], "appareils": {"mobile": 0, "bureau": 0}, "heures": {str(h): 0 for h in range(24)}}


def _lire_brut() -> dict:
    if not _FICHIER.exists():
        return _defaut()
    try:
        donnees = json.loads(_FICHIER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _defaut()
    defaut = _defaut()
    if isinstance(donnees, list):
        # Ancien format (avant l'ajout des agrégats appareil/heure) : une simple liste de clics.
        defaut["clics"] = donnees
        return defaut
    defaut.update(donnees)
    return defaut


def _classer_appareil(user_agent: str) -> str:
    return "mobile" if any(mot in user_agent for mot in _MOTS_CLES_MOBILE) else "bureau"


def enregistrer_clic(cle: str, user_agent: str = "") -> None:
    donnees = _lire_brut()
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    for entree in donnees["clics"]:
        if entree.get("date") == aujourdhui and entree.get("cle") == cle:
            entree["clics"] = entree.get("clics", 0) + 1
            break
    else:
        donnees["clics"].append({"date": aujourdhui, "cle": cle, "clics": 1})
        donnees["clics"] = donnees["clics"][-_MAX_ENTREES:]
    donnees["appareils"][_classer_appareil(user_agent)] += 1
    donnees["heures"][str(datetime.now().hour)] += 1
    _FICHIER.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")


def lire_stats(limite_jours: int = 30) -> dict:
    donnees = _lire_brut()
    entrees = donnees["clics"]
    total_par_cle: dict[str, int] = {}
    for e in entrees:
        total_par_cle[e["cle"]] = total_par_cle.get(e["cle"], 0) + e.get("clics", 0)
    dates_recentes = sorted({e["date"] for e in entrees})[-limite_jours:]
    return {
        "total_par_lien": total_par_cle,
        "historique": [e for e in entrees if e["date"] in dates_recentes],
        "appareils": donnees["appareils"],
        "heures": donnees["heures"],
    }
