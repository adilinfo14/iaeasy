import asyncio

import numpy as np


def _toy_dossiers_credit():
    rng = np.random.RandomState(3)
    n = 60
    revenu = rng.normal(2800, 700, n).clip(900, 6000)
    endettement = rng.normal(0.32, 0.12, n).clip(0.05, 0.8)
    incidents = rng.poisson(0.6, n)
    risque = (
        (endettement > 0.4).astype(int) + (incidents >= 2).astype(int) + (revenu < 1800).astype(int) >= 2
    ).astype(int)
    return revenu, endettement, incidents, risque


def _scoring_sync() -> dict:
    from sklearn.linear_model import LogisticRegression

    revenu, endettement, incidents, risque = _toy_dossiers_credit()
    X = np.column_stack([revenu, endettement, incidents])
    modele = LogisticRegression()
    modele.fit(X, risque)

    dossier_teste = {"revenu_mensuel": 1900, "taux_endettement": 0.45, "incidents_paiement": 2}
    nouveau = np.array([[dossier_teste["revenu_mensuel"], dossier_teste["taux_endettement"], dossier_teste["incidents_paiement"]]])
    proba_risque = float(modele.predict_proba(nouveau)[0][1])

    return {
        "type": "scoring_credit",
        "nb_dossiers_entrainement": len(risque),
        "nb_dossiers_a_risque": int(risque.sum()),
        "dossier_teste": dossier_teste,
        "probabilite_risque": round(proba_risque, 3),
        "decision_suggeree": "Refus / étude approfondie" if proba_risque > 0.5 else "Accord",
        "explication": "Modèle (régression logistique) entraîné en direct sur 60 dossiers jouets — "
        "variables utilisées : revenu mensuel, taux d'endettement, incidents de paiement.",
    }


def _toy_notes_films():
    matrice = np.array(
        [
            [5, 4, 0, 1, 0],
            [4, 5, 0, 0, 1],
            [0, 0, 5, 4, 0],
            [1, 0, 4, 5, 0],
            [0, 1, 0, 0, 5],
        ],
        dtype=float,
    )
    films = ["Film A (action)", "Film B (action)", "Film C (drame)", "Film D (drame)", "Film E (comédie)"]
    return matrice, films


def _recommandation_sync() -> dict:
    from sklearn.decomposition import NMF

    matrice, films = _toy_notes_films()
    modele = NMF(n_components=2, init="random", random_state=0, max_iter=500)
    W = modele.fit_transform(matrice)
    H = modele.components_
    matrice_reconstruite = W @ H

    utilisateur_idx = 0
    deja_notes = matrice[utilisateur_idx] > 0
    scores = matrice_reconstruite[utilisateur_idx].copy()
    scores[deja_notes] = -1
    recommande_idx = int(np.argmax(scores))

    return {
        "type": "recommandation",
        "utilisateur": "Utilisateur 1",
        "films_deja_notes": [
            {"film": f, "note": int(n)} for f, n in zip(films, matrice[utilisateur_idx]) if n > 0
        ],
        "film_recommande": films[recommande_idx],
        "score_prevu": round(float(scores[recommande_idx]), 2),
        "explication": "Factorisation de matrice (NMF) entraînée en direct sur les notes de 5 utilisateurs "
        "jouets, pour deviner les goûts non exprimés de l'utilisateur 1.",
    }


def _toy_dossiers_pret():
    rng = np.random.RandomState(9)
    n = 60
    apport = rng.normal(0.15, 0.08, n).clip(0.0, 0.5)
    duree_annees = rng.normal(20, 5, n).clip(7, 30)
    revenu = rng.normal(3200, 900, n).clip(1200, 8000)
    accepte = (
        (apport > 0.1).astype(int) + (revenu > 2200).astype(int) + (duree_annees < 25).astype(int) >= 2
    ).astype(int)
    return apport, duree_annees, revenu, accepte


def _scoring_pret_sync() -> dict:
    from sklearn.tree import DecisionTreeClassifier

    apport, duree, revenu, accepte = _toy_dossiers_pret()
    X = np.column_stack([apport, duree, revenu])
    modele = DecisionTreeClassifier(max_depth=3, random_state=9)
    modele.fit(X, accepte)

    dossier_teste = {"apport_pourcent": 0.08, "duree_annees": 25, "revenu_mensuel": 2400}
    nouveau = np.array([[dossier_teste["apport_pourcent"], dossier_teste["duree_annees"], dossier_teste["revenu_mensuel"]]])
    proba_acceptation = float(modele.predict_proba(nouveau)[0][1])

    return {
        "type": "scoring_pret_immobilier",
        "nb_dossiers_entrainement": len(accepte),
        "nb_dossiers_acceptes": int(accepte.sum()),
        "dossier_teste": dossier_teste,
        "probabilite_acceptation": round(proba_acceptation, 3),
        "decision_suggeree": "Acceptation probable" if proba_acceptation > 0.5 else "Refus probable / étude approfondie",
        "explication": "Modèle (arbre de décision) entraîné en direct sur 60 dossiers de prêt immobilier "
        "jouets — variables utilisées : taux d'apport, durée du prêt, revenu mensuel. Contrairement à la "
        "régression logistique du scoring crédit, un arbre de décision explique sa décision par une suite "
        "de seuils lisibles (ex: 'apport < 10% ET durée > 25 ans → refus').",
    }


async def run_scoring_pret() -> dict:
    return await asyncio.to_thread(_scoring_pret_sync)


async def run_scoring_credit() -> dict:
    return await asyncio.to_thread(_scoring_sync)


async def run_recommandation() -> dict:
    return await asyncio.to_thread(_recommandation_sync)


def _toy_notes_materiaux():
    matrice = np.array(
        [
            [5, 4, 0, 1, 0],
            [4, 5, 0, 0, 1],
            [0, 0, 5, 4, 0],
            [1, 0, 4, 5, 0],
            [0, 1, 0, 0, 5],
        ],
        dtype=float,
    )
    materiaux = [
        "Carrelage grès cérame",
        "Carrelage grès cérame (autre gamme)",
        "Parquet chêne massif",
        "Parquet chêne massif (autre finition)",
        "Sol vinyle",
    ]
    return matrice, materiaux


def _recommandation_materiaux_sync() -> dict:
    from sklearn.decomposition import NMF

    matrice, materiaux = _toy_notes_materiaux()
    modele = NMF(n_components=2, init="random", random_state=1, max_iter=500)
    W = modele.fit_transform(matrice)
    H = modele.components_
    matrice_reconstruite = W @ H

    artisan_idx = 0
    deja_notes = matrice[artisan_idx] > 0
    scores = matrice_reconstruite[artisan_idx].copy()
    scores[deja_notes] = -1
    recommande_idx = int(np.argmax(scores))

    return {
        "type": "recommandation",
        "utilisateur": "Artisan 1",
        "films_deja_notes": [
            {"film": m, "note": int(n)} for m, n in zip(materiaux, matrice[artisan_idx]) if n > 0
        ],
        "film_recommande": materiaux[recommande_idx],
        "score_prevu": round(float(scores[recommande_idx]), 2),
        "explication": "Même principe (factorisation de matrice NMF) que la recommandation de films, "
        "appliqué cette fois aux préférences de matériaux d'un artisan à partir de ses chantiers passés "
        "— la recommandation ne se limite pas au e-commerce grand public.",
    }


async def run_recommandation_materiaux() -> dict:
    return await asyncio.to_thread(_recommandation_materiaux_sync)


def _toy_clients_artisan():
    rng = np.random.RandomState(15)
    # 3 groupes de clients volontairement distincts, mais SANS étiquette de groupe fournie
    # au modèle — c'est justement le principe du clustering : les découvrir tout seul.
    occasionnels = rng.normal([300, 1], [80, 0.5], (20, 2))
    reguliers = rng.normal([900, 4], [150, 1], (20, 2))
    gros_comptes = rng.normal([3500, 8], [400, 2], (15, 2))
    montants_frequences = np.vstack([occasionnels, reguliers, gros_comptes])
    # Bornes réalistes appliquées séparément par colonne (le montant et la fréquence n'ont
    # évidemment pas la même échelle) pour éviter une valeur aberrante négative ou nulle.
    montants_frequences[:, 0] = montants_frequences[:, 0].clip(min=50)
    montants_frequences[:, 1] = montants_frequences[:, 1].clip(min=0.5)
    return montants_frequences


def _clustering_sync() -> dict:
    from sklearn.cluster import KMeans

    donnees = _toy_clients_artisan()
    modele = KMeans(n_clusters=3, n_init=10, random_state=15)
    labels = modele.fit_predict(donnees)

    groupes = []
    for cluster_id in sorted(set(labels)):
        membres = donnees[labels == cluster_id]
        groupes.append(
            {
                "groupe": int(cluster_id) + 1,
                "nb_clients": int(len(membres)),
                "montant_moyen_facture": round(float(membres[:, 0].mean()), 0),
                "frequence_moyenne_par_an": round(float(membres[:, 1].mean()), 1),
            }
        )
    groupes.sort(key=lambda g: g["montant_moyen_facture"])

    return {
        "type": "clustering",
        "nb_clients_total": len(donnees),
        "nb_groupes": 3,
        "groupes_decouverts": groupes,
        "explication": "Le modèle (KMeans) n'a reçu QUE deux chiffres par client (montant moyen de "
        "facture, fréquence annuelle) — sans jamais qu'on lui dise combien de groupes chercher ni ce "
        "qu'ils représentent. Il a découvert seul 3 profils de clients à partir de leurs seules "
        "habitudes, une différence fondamentale avec le scoring crédit qui, lui, apprend à partir "
        "d'exemples déjà étiquetés 'à risque' ou 'sain'.",
    }


async def run_clustering() -> dict:
    return await asyncio.to_thread(_clustering_sync)


def _toy_dossiers_auto():
    # n=200 (au lieu de 60) et seuils moins stricts : avec seulement 60 dossiers et des seuils
    # sévères, la classe "à risque" ne comptait que 4 exemples — trop peu pour que la régression
    # apprenne une frontière fiable (coefficients quasi nuls ou mal orientés, constaté en test
    # réel). Ce jeu élargi donne une séparation nette et des coefficients correctement orientés.
    rng = np.random.RandomState(31)
    n = 200
    age_conducteur = rng.normal(38, 14, n).clip(18, 75)
    anciennete_permis = (age_conducteur - 18 - rng.uniform(0, 3, n)).clip(0, 55)
    nb_sinistres_3ans = rng.poisson(0.6, n)
    risque = (
        (age_conducteur < 28).astype(int) + (nb_sinistres_3ans >= 1).astype(int) + (anciennete_permis < 6).astype(int)
        >= 2
    ).astype(int)
    return age_conducteur, anciennete_permis, nb_sinistres_3ans, risque


def _scoring_auto_sync() -> dict:
    from sklearn.linear_model import LogisticRegression

    age, anciennete, sinistres, risque = _toy_dossiers_auto()
    X = np.column_stack([age, anciennete, sinistres])
    modele = LogisticRegression()
    modele.fit(X, risque)

    profil_teste = {"age_conducteur": 21, "anciennete_permis_annees": 2, "nb_sinistres_3ans": 1}
    nouveau = np.array(
        [[profil_teste["age_conducteur"], profil_teste["anciennete_permis_annees"], profil_teste["nb_sinistres_3ans"]]]
    )
    proba_risque = float(modele.predict_proba(nouveau)[0][1])

    return {
        "type": "scoring_assurance_auto",
        "nb_profils_entrainement": len(risque),
        "nb_profils_a_risque": int(risque.sum()),
        "profil_teste": profil_teste,
        "probabilite_risque": round(proba_risque, 3),
        "decision_suggeree": "Surprime / étude approfondie" if proba_risque > 0.5 else "Tarif standard",
        "explication": "Modèle (régression logistique) entraîné en direct sur 60 profils jouets — "
        "variables utilisées : âge du conducteur, ancienneté du permis, nombre de sinistres "
        "responsables sur 3 ans. Même technique que le scoring crédit, appliquée à la tarification "
        "auto plutôt qu'au risque bancaire.",
    }


async def run_scoring_auto() -> dict:
    return await asyncio.to_thread(_scoring_auto_sync)


def _toy_dossiers_sante():
    # Mêmes ajustements que le scoring auto (n=200, seuils moins stricts) : la version initiale
    # ne comptait que 2 dossiers "à risque" sur 60, insuffisant pour un apprentissage fiable.
    rng = np.random.RandomState(37)
    n = 200
    age = rng.normal(45, 17, n).clip(18, 85)
    nb_consultations_an = rng.poisson(3, n)
    hospitalisation_recente = rng.binomial(1, 0.15, n)
    surrisque = (
        (age > 55).astype(int) + (nb_consultations_an >= 5).astype(int) + hospitalisation_recente >= 2
    ).astype(int)
    return age, nb_consultations_an, hospitalisation_recente, surrisque


def _scoring_sante_sync() -> dict:
    from sklearn.linear_model import LogisticRegression

    age, consultations, hospit, surrisque = _toy_dossiers_sante()
    X = np.column_stack([age, consultations, hospit])
    modele = LogisticRegression()
    modele.fit(X, surrisque)

    profil_teste = {"age": 67, "nb_consultations_an": 7, "hospitalisation_recente": 1}
    nouveau = np.array(
        [[profil_teste["age"], profil_teste["nb_consultations_an"], profil_teste["hospitalisation_recente"]]]
    )
    proba_surrisque = float(modele.predict_proba(nouveau)[0][1])

    return {
        "type": "scoring_assurance_sante",
        "nb_profils_entrainement": len(surrisque),
        "nb_profils_a_risque": int(surrisque.sum()),
        "profil_teste": profil_teste,
        "probabilite_risque": round(proba_surrisque, 3),
        "decision_suggeree": "Surprime / questionnaire médical complémentaire" if proba_surrisque > 0.5 else "Tarif standard",
        "explication": "Modèle (régression logistique) entraîné en direct sur 60 profils jouets — "
        "variables utilisées : âge, nombre de consultations dans l'année, hospitalisation récente. "
        "Un vrai contrat de complémentaire santé mobiliserait bien plus de variables et un encadrement "
        "réglementaire strict (non-discrimination) ; ceci reste une démonstration pédagogique du "
        "mécanisme, pas un outil de tarification réel.",
    }


async def run_scoring_sante() -> dict:
    return await asyncio.to_thread(_scoring_sante_sync)
