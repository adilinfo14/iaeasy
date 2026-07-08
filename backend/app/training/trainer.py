import csv
import threading
import uuid
from pathlib import Path

import numpy as np

_jobs: dict[str, dict] = {}
_modeles_entraines: dict[str, dict] = {}

_DATASET_SENTIMENT = Path(__file__).parent / "datasets" / "toy_sentiment_fr.csv"
_DATASET_SPAM = Path(__file__).parent / "datasets" / "toy_spam_fr.csv"
_BASE_MODEL_SENTIMENT = "cmarkea/distilcamembert-base"

SCENARIOS = {
    "sentiment_camembert": {
        "titre": "Trier des avis clients (positif / négatif)",
        "famille_algo": "Réseau de neurones (deep learning)",
        "modele_base": "CamemBERT distillé — 68 millions de paramètres",
        "cas_usage": (
            "Un service client reçoit des centaines d'avis chaque semaine et veut les trier "
            "automatiquement en positif/négatif pour prioriser les réponses aux clients mécontents."
        ),
    },
    "spam_logreg": {
        "titre": "Filtrer les emails indésirables (spam)",
        "famille_algo": "Algorithme classique (régression logistique)",
        "modele_base": "Régression logistique sur des vecteurs TF-IDF — pas de réseau de neurones",
        "cas_usage": (
            "Une messagerie professionnelle veut détecter automatiquement les emails de "
            "spam/phishing avant qu'ils n'arrivent dans la boîte de réception."
        ),
    },
    "prevision_ca": {
        "titre": "Prévoir le chiffre d'affaires du mois prochain",
        "famille_algo": "Algorithme classique (régression linéaire)",
        "modele_base": "Régression linéaire entraînée par descente de gradient, à la main",
        "cas_usage": (
            "Un artisan veut anticiper sa trésorerie en prévoyant son chiffre d'affaires des "
            "prochains mois à partir de son historique de facturation."
        ),
    },
}


def _lire_csv(path: Path) -> tuple[list[str], list[int]]:
    textes, labels = [], []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            textes.append(row["texte"])
            labels.append(int(row["label"]))
    return textes, labels


def _toy_serie_ca() -> tuple[list[int], list[float]]:
    mois = list(range(1, 19))
    rng = np.random.RandomState(5)
    tendance = 8000 + np.array(mois) * 320
    bruit = rng.normal(0, 400, len(mois))
    return mois, (tendance + bruit).tolist()


EXEMPLES_TEST = {
    "sentiment_camembert": [
        "Le technicien a été très professionnel et à l'écoute.",
        "Toujours aucune réponse après 2 semaines, c'est inadmissible.",
        "Prix correct mais le délai était vraiment long.",
        "Je recommande sans hésiter, service impeccable.",
        "Le rendez-vous a encore été annulé sans prévenir.",
        "Équipe efficace, chantier terminé avant la date prévue.",
        "Facturation confuse, plusieurs erreurs à corriger.",
        "Résultat parfait, exactement ce que je voulais.",
        "Un conseiller désagréable qui ne répond pas aux questions.",
        "Très satisfait du suivi après les travaux.",
    ],
    "spam_logreg": [
        "Cliquez ici pour gagner un iPhone gratuitement maintenant.",
        "Bonjour, voici le compte-rendu de la réunion de ce matin.",
        "Urgent : votre compte sera fermé, confirmez vos données ici.",
        "Merci de valider le devis ci-joint avant vendredi.",
        "Vous avez gagné 10000€, réclamez votre prix immédiatement.",
        "Le rendez-vous chantier est confirmé pour lundi 9h.",
        "Réduction de 90% aujourd'hui seulement, cliquez vite.",
        "Voici la facture corrigée suite à notre échange.",
        "Votre colis est bloqué, payez 1,99€ pour le débloquer ici.",
        "Je vous transmets le planning de la semaine prochaine.",
    ],
    "prevision_ca": [19, 20, 21, 22, 24, 26, 28, 30, 15, 25],
}


def lister_scenarios() -> list[dict]:
    return [{"id": sid, **infos} for sid, infos in SCENARIOS.items()]


def apercu_donnees(scenario_id: str) -> dict:
    if scenario_id == "sentiment_camembert":
        textes, labels = _lire_csv(_DATASET_SENTIMENT)
        lignes = [{"texte": t, "label": "positif" if lbl == 1 else "négatif"} for t, lbl in zip(textes, labels)]
        return {"colonnes": ["texte", "label"], "lignes": lignes[:10], "total": len(lignes)}

    if scenario_id == "spam_logreg":
        textes, labels = _lire_csv(_DATASET_SPAM)
        lignes = [{"texte": t, "label": "spam" if lbl == 1 else "légitime"} for t, lbl in zip(textes, labels)]
        return {"colonnes": ["texte", "label"], "lignes": lignes[:10], "total": len(lignes)}

    if scenario_id == "prevision_ca":
        mois, ca = _toy_serie_ca()
        lignes = [{"mois": f"Mois {m}", "chiffre_affaires_euros": round(c)} for m, c in zip(mois, ca)]
        return {"colonnes": ["mois", "chiffre_affaires_euros"], "lignes": lignes, "total": len(lignes)}

    raise ValueError(f"Scénario inconnu : {scenario_id}")


def _entrainer_sentiment(job_id: str) -> None:
    from datasets import Dataset
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        Trainer,
        TrainerCallback,
        TrainingArguments,
    )

    class LossCallback(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kwargs):
            if logs and "loss" in logs:
                _jobs[job_id]["history"].append(
                    {
                        "step": state.global_step,
                        "epoch": round(state.epoch or 0, 2),
                        "loss": round(logs["loss"], 4),
                    }
                )

    textes, labels = _lire_csv(_DATASET_SENTIMENT)
    tokenizer = AutoTokenizer.from_pretrained(_BASE_MODEL_SENTIMENT)
    model = AutoModelForSequenceClassification.from_pretrained(_BASE_MODEL_SENTIMENT, num_labels=2)

    encodings = tokenizer(textes, truncation=True, padding=True, max_length=64)
    dataset = Dataset.from_dict({**encodings, "labels": labels})

    args = TrainingArguments(
        output_dir=f"/tmp/iaeasy-training-{job_id}",
        per_device_train_batch_size=8,
        num_train_epochs=4,
        logging_steps=1,
        save_strategy="no",
        report_to=[],
        disable_tqdm=True,
    )

    trainer = Trainer(model=model, args=args, train_dataset=dataset, callbacks=[LossCallback()])
    trainer.train()

    _modeles_entraines[job_id] = {"type": "sentiment", "tokenizer": tokenizer, "modele": model}


def _entrainer_spam(job_id: str) -> None:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier
    from sklearn.metrics import log_loss

    textes, labels = _lire_csv(_DATASET_SPAM)
    y = np.array(labels)

    vectorizer = TfidfVectorizer(max_features=200)
    X = vectorizer.fit_transform(textes).toarray()

    modele = SGDClassifier(loss="log_loss", random_state=0, learning_rate="constant", eta0=0.15)
    classes = np.array([0, 1])

    n_epochs = 25
    for epoch in range(n_epochs):
        modele.partial_fit(X, y, classes=classes)
        probas = modele.predict_proba(X)
        perte = log_loss(y, probas, labels=[0, 1])
        _jobs[job_id]["history"].append(
            {"step": epoch + 1, "epoch": round(epoch + 1, 2), "loss": round(float(perte), 4)}
        )

    _modeles_entraines[job_id] = {"type": "spam", "vectorizer": vectorizer, "modele": modele}


def _entrainer_prevision(job_id: str) -> None:
    mois, ca = _toy_serie_ca()
    x = np.array(mois, dtype=float)
    y = np.array(ca, dtype=float)
    x_mean, x_std = x.mean(), x.std()
    y_mean, y_std = y.mean(), y.std()
    x_norm = (x - x_mean) / x_std
    y_norm = (y - y_mean) / y_std

    a, b = 0.0, 0.0
    lr = 0.15
    n_iter = 60
    for i in range(n_iter):
        y_pred = a * x_norm + b
        erreur = y_pred - y_norm
        perte = float(np.mean(erreur**2))
        grad_a = float(np.mean(2 * erreur * x_norm))
        grad_b = float(np.mean(2 * erreur))
        a -= lr * grad_a
        b -= lr * grad_b
        _jobs[job_id]["history"].append({"step": i + 1, "epoch": round((i + 1) / 6, 2), "loss": round(perte, 5)})

    _modeles_entraines[job_id] = {
        "type": "prevision",
        "a": a,
        "b": b,
        "x_mean": x_mean,
        "x_std": x_std,
        "y_mean": y_mean,
        "y_std": y_std,
    }


_ENTRAINEURS = {
    "sentiment_camembert": _entrainer_sentiment,
    "spam_logreg": _entrainer_spam,
    "prevision_ca": _entrainer_prevision,
}


def _evaluer_avant(scenario_id: str) -> list[dict]:
    exemples = EXEMPLES_TEST[scenario_id]

    if scenario_id == "sentiment_camembert":
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(_BASE_MODEL_SENTIMENT)
        modele = AutoModelForSequenceClassification.from_pretrained(_BASE_MODEL_SENTIMENT, num_labels=2)
        modele.eval()

        resultats = []
        for texte in exemples:
            entrees = tokenizer(texte, return_tensors="pt", truncation=True, max_length=64)
            with torch.no_grad():
                logits = modele(**entrees).logits
            proba = torch.softmax(logits, dim=1)[0]
            etiquette = "positif" if proba[1] > proba[0] else "négatif"
            resultats.append({"entree": texte, "prediction": etiquette, "confiance": round(float(proba.max()), 3)})
        return resultats

    if scenario_id == "spam_logreg":
        return [
            {"entree": texte, "prediction": "indéterminé (poids à zéro, rien n'a encore été appris)", "confiance": 0.5}
            for texte in exemples
        ]

    if scenario_id == "prevision_ca":
        _, ca = _toy_serie_ca()
        y_mean_str = f"{np.mean(ca):,.0f}".replace(",", " ")
        return [
            {
                "entree": f"Mois {m}",
                "prediction": f"{y_mean_str} € (moyenne globale, aucune tendance apprise)",
                "confiance": None,
            }
            for m in exemples
        ]

    raise ValueError(f"Scénario inconnu : {scenario_id}")


def _evaluer_apres(job_id: str, scenario_id: str) -> list[dict]:
    exemples = EXEMPLES_TEST[scenario_id]
    return [tester_modele(job_id, str(e)) for e in exemples]


def _entrainer(job_id: str, scenario_id: str) -> None:
    try:
        _ENTRAINEURS[scenario_id](job_id)
        _jobs[job_id]["apres"] = _evaluer_apres(job_id, scenario_id)
        _jobs[job_id]["status"] = "termine"
    except Exception as exc:  # noqa: BLE001 — l'erreur doit remonter côté IHM, pas planter le thread
        _jobs[job_id]["status"] = "erreur"
        _jobs[job_id]["erreur"] = str(exc)


def demarrer_entrainement(scenario_id: str) -> str:
    if scenario_id not in SCENARIOS:
        raise ValueError(f"Scénario inconnu : {scenario_id}")
    job_id = uuid.uuid4().hex[:8]
    avant = _evaluer_avant(scenario_id)
    _jobs[job_id] = {
        "status": "en_cours",
        "history": [],
        "erreur": None,
        "scenario_id": scenario_id,
        "avant": avant,
        "apres": None,
    }
    threading.Thread(target=_entrainer, args=(job_id, scenario_id), daemon=True).start()
    return job_id


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def tester_modele(job_id: str, entree: str | None) -> dict:
    infos = _modeles_entraines.get(job_id)
    if infos is None:
        raise ValueError("Le modèle n'est pas encore prêt (entraînement non terminé).")

    if infos["type"] == "sentiment":
        import torch

        tokenizer, model = infos["tokenizer"], infos["modele"]
        entrees = tokenizer(entree or "", return_tensors="pt", truncation=True, max_length=64)
        with torch.no_grad():
            logits = model(**entrees).logits
        proba = torch.softmax(logits, dim=1)[0]
        etiquette = "positif" if proba[1] > proba[0] else "négatif"
        return {
            "type": "test_modele",
            "entree": entree,
            "prediction": etiquette,
            "confiance": round(float(proba.max()), 3),
        }

    if infos["type"] == "spam":
        X = infos["vectorizer"].transform([entree or ""]).toarray()
        proba = infos["modele"].predict_proba(X)[0]
        etiquette = "spam" if proba[1] > 0.5 else "légitime"
        return {
            "type": "test_modele",
            "entree": entree,
            "prediction": etiquette,
            "confiance": round(float(proba.max()), 3),
        }

    if infos["type"] == "prevision":
        try:
            mois_cible = float(entree) if entree else 19.0
        except ValueError:
            mois_cible = 19.0
        x_norm = (mois_cible - infos["x_mean"]) / infos["x_std"]
        y_norm = infos["a"] * x_norm + infos["b"]
        y_pred = y_norm * infos["y_std"] + infos["y_mean"]
        return {
            "type": "test_modele",
            "entree": f"Mois {mois_cible:g}",
            "prediction": f"{y_pred:,.0f} € prévus".replace(",", " "),
            "confiance": None,
        }

    raise ValueError(f"Type de modèle inconnu : {infos['type']}")
