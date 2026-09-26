import asyncio

import numpy as np

_chronos_pipelines: dict[str, object] = {}


def _toy_serie_economique() -> list[float]:
    mois = np.arange(24)
    tendance = 100 + mois * 2.5
    saison = 8 * np.sin(2 * np.pi * mois / 12)
    bruit = np.random.RandomState(42).normal(0, 3, size=len(mois))
    return (tendance + saison + bruit).tolist()


def _prevoir_sync(model_ref: str) -> dict:
    import torch

    if model_ref not in _chronos_pipelines:
        from chronos import BaseChronosPipeline

        _chronos_pipelines[model_ref] = BaseChronosPipeline.from_pretrained(
            model_ref, device_map="cpu", torch_dtype=torch.float32
        )

    historique = _toy_serie_economique()
    context = torch.tensor(historique)
    horizon = 6
    quantiles, mean = _chronos_pipelines[model_ref].predict_quantiles(
        inputs=context, prediction_length=horizon, quantile_levels=[0.1, 0.5, 0.9]
    )

    return {
        "type": "prevision_serie_temporelle",
        "historique": [round(v, 1) for v in historique],
        "prevision_mediane": [round(v, 1) for v in mean[0].tolist()],
        "intervalle_bas": [round(v, 1) for v in quantiles[0, :, 0].tolist()],
        "intervalle_haut": [round(v, 1) for v in quantiles[0, :, 2].tolist()],
        "explication": "Prévision des 6 prochains mois avec intervalle de confiance (10e-90e centile).",
    }


def _toy_capteur_mecanique() -> list[float]:
    rng = np.random.RandomState(7)
    mesures = rng.normal(loc=0.5, scale=0.05, size=150)
    mesures[60] = 1.4
    mesures[120] = 1.6
    return mesures.tolist()


def _detect_anomalie_sync() -> dict:
    from sklearn.ensemble import IsolationForest

    mesures = _toy_capteur_mecanique()
    X = np.array(mesures).reshape(-1, 1)
    modele = IsolationForest(contamination=0.02, random_state=7)
    modele.fit(X)
    scores = modele.decision_function(X)
    predictions = modele.predict(X)

    anomalies = [
        {"indice": i, "valeur": round(mesures[i], 3), "score": round(float(scores[i]), 3)}
        for i, p in enumerate(predictions)
        if p == -1
    ]

    return {
        "type": "detection_anomalie",
        "nb_mesures": len(mesures),
        "mesures": [round(v, 3) for v in mesures],
        "anomalies_detectees": anomalies,
        "explication": "Modèle entraîné en direct sur ces mesures : les points identifiés comme "
        "anomalie s'écartent statistiquement du comportement vibratoire normal de la machine.",
    }


def _toy_transactions_bancaires() -> list[float]:
    rng = np.random.RandomState(11)
    montants = rng.normal(45, 20, 200).clip(2, 300)
    montants[15] = 2450
    montants[120] = 1875
    return montants.tolist()


def _detect_fraude_sync() -> dict:
    from sklearn.ensemble import IsolationForest

    montants = _toy_transactions_bancaires()
    X = np.array(montants).reshape(-1, 1)
    modele = IsolationForest(contamination=0.015, random_state=11)
    modele.fit(X)
    scores = modele.decision_function(X)
    predictions = modele.predict(X)

    anomalies = [
        {"indice": i, "montant": round(montants[i], 2), "score": round(float(scores[i]), 3)}
        for i, p in enumerate(predictions)
        if p == -1
    ]

    return {
        "type": "detection_anomalie",
        "nb_mesures": len(montants),
        "mesures": [round(v, 2) for v in montants],
        "anomalies_detectees": anomalies,
        "explication": "Modèle entraîné en direct sur l'historique de montants de transactions : les "
        "valeurs identifiées s'écartent statistiquement du comportement d'achat habituel du client.",
    }


def _toy_capteur_four() -> list[float]:
    rng = np.random.RandomState(23)
    mesures = rng.normal(loc=180, scale=4, size=150)
    mesures[45] = 230
    mesures[100] = 95
    return mesures.tolist()


def _detect_anomalie_four_sync() -> dict:
    from sklearn.ensemble import IsolationForest

    mesures = _toy_capteur_four()
    X = np.array(mesures).reshape(-1, 1)
    modele = IsolationForest(contamination=0.02, random_state=23)
    modele.fit(X)
    scores = modele.decision_function(X)
    predictions = modele.predict(X)

    anomalies = [
        {"indice": i, "valeur": round(mesures[i], 1), "score": round(float(scores[i]), 3)}
        for i, p in enumerate(predictions)
        if p == -1
    ]

    return {
        "type": "detection_anomalie",
        "nb_mesures": len(mesures),
        "mesures": [round(v, 1) for v in mesures],
        "anomalies_detectees": anomalies,
        "explication": "Même algorithme (Isolation Forest) que pour la maintenance mécanique ou la "
        "fraude bancaire, appliqué cette fois à la température d'un four industriel — preuve qu'un "
        "même type de modèle sert des secteurs très différents dès lors qu'on lui donne les bonnes données.",
    }


async def run_anomalie_four() -> dict:
    return await asyncio.to_thread(_detect_anomalie_four_sync)


def _toy_sinistres_auto() -> list[float]:
    rng = np.random.RandomState(41)
    montants = rng.normal(1400, 500, 180).clip(150, 4000)
    montants[30] = 18500
    montants[95] = 21200
    return montants.tolist()


def _detect_anomalie_sinistres_sync() -> dict:
    from sklearn.ensemble import IsolationForest

    montants = _toy_sinistres_auto()
    X = np.array(montants).reshape(-1, 1)
    modele = IsolationForest(contamination=0.012, random_state=41)
    modele.fit(X)
    scores = modele.decision_function(X)
    predictions = modele.predict(X)

    anomalies = [
        {"indice": i, "montant": round(montants[i], 2), "score": round(float(scores[i]), 3)}
        for i, p in enumerate(predictions)
        if p == -1
    ]

    return {
        "type": "detection_anomalie",
        "nb_mesures": len(montants),
        "mesures": [round(v, 2) for v in montants],
        "anomalies_detectees": anomalies,
        "explication": "Même algorithme (Isolation Forest) que pour la fraude bancaire ou la "
        "maintenance mécanique, appliqué cette fois aux montants de sinistres auto déclarés — les "
        "montants identifiés s'écartent statistiquement de la distribution habituelle des sinistres, "
        "un premier filtre avant expertise humaine, jamais une accusation automatique.",
    }


async def run_anomalie_sinistres_auto() -> dict:
    return await asyncio.to_thread(_detect_anomalie_sinistres_sync)


def _toy_remboursements_sante() -> list[float]:
    rng = np.random.RandomState(43)
    montants = rng.normal(85, 40, 200).clip(10, 400)
    montants[50] = 3200
    montants[150] = 2750
    return montants.tolist()


def _detect_anomalie_remboursements_sync() -> dict:
    from sklearn.ensemble import IsolationForest

    montants = _toy_remboursements_sante()
    X = np.array(montants).reshape(-1, 1)
    modele = IsolationForest(contamination=0.01, random_state=43)
    modele.fit(X)
    scores = modele.decision_function(X)
    predictions = modele.predict(X)

    anomalies = [
        {"indice": i, "montant": round(montants[i], 2), "score": round(float(scores[i]), 3)}
        for i, p in enumerate(predictions)
        if p == -1
    ]

    return {
        "type": "detection_anomalie",
        "nb_mesures": len(montants),
        "mesures": [round(v, 2) for v in montants],
        "anomalies_detectees": anomalies,
        "explication": "Même algorithme (Isolation Forest) que pour la fraude bancaire, appliqué "
        "cette fois aux montants de remboursements de soins — un remboursement anormalement élevé "
        "n'est pas une preuve de fraude, seulement un signal à vérifier en priorité.",
    }


async def run_anomalie_remboursements_sante() -> dict:
    return await asyncio.to_thread(_detect_anomalie_remboursements_sync)


def _toy_serie_sinistres_frequence() -> list[float]:
    mois = np.arange(24)
    tendance = 42 + mois * 0.6
    saison = 10 * np.sin(2 * np.pi * (mois - 3) / 12)  # pic hivernal (verglas, tempêtes)
    bruit = np.random.RandomState(45).normal(0, 3, size=len(mois))
    return (tendance + saison + bruit).clip(min=5).tolist()


def _toy_serie_depenses_sante() -> list[float]:
    mois = np.arange(24)
    tendance = 210 + mois * 1.8
    saison = 15 * np.sin(2 * np.pi * (mois - 1) / 12)  # pic hivernal (épidémies saisonnières)
    bruit = np.random.RandomState(47).normal(0, 6, size=len(mois))
    return (tendance + saison + bruit).clip(min=50).tolist()


def _prevoir_generique_sync(model_ref: str, historique: list[float]) -> dict:
    import torch

    if model_ref not in _chronos_pipelines:
        from chronos import BaseChronosPipeline

        _chronos_pipelines[model_ref] = BaseChronosPipeline.from_pretrained(
            model_ref, device_map="cpu", torch_dtype=torch.float32
        )

    context = torch.tensor(historique)
    horizon = 6
    quantiles, mean = _chronos_pipelines[model_ref].predict_quantiles(
        inputs=context, prediction_length=horizon, quantile_levels=[0.1, 0.5, 0.9]
    )

    return {
        "type": "prevision_serie_temporelle",
        "historique": [round(v, 1) for v in historique],
        "prevision_mediane": [round(v, 1) for v in mean[0].tolist()],
        "intervalle_bas": [round(v, 1) for v in quantiles[0, :, 0].tolist()],
        "intervalle_haut": [round(v, 1) for v in quantiles[0, :, 2].tolist()],
        "explication": "Prévision des 6 prochains mois avec intervalle de confiance (10e-90e centile).",
    }


async def run_prevision_sinistres_frequence(model_ref: str) -> dict:
    return await asyncio.to_thread(_prevoir_generique_sync, model_ref, _toy_serie_sinistres_frequence())


async def run_prevision_depenses_sante(model_ref: str) -> dict:
    return await asyncio.to_thread(_prevoir_generique_sync, model_ref, _toy_serie_depenses_sante())


async def run_prevision(model_ref: str) -> dict:
    return await asyncio.to_thread(_prevoir_sync, model_ref)


async def run_anomalie() -> dict:
    return await asyncio.to_thread(_detect_anomalie_sync)


async def run_fraude() -> dict:
    return await asyncio.to_thread(_detect_fraude_sync)
