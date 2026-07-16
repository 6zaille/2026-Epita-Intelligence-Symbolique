"""Explicabilite ML : les valeurs SHAP comme valeur de Shapley.

Sur un vrai jeu de donnees medical (diabetes, scikit-learn), on entraine un
modele qui predit la progression de la maladie a un an, puis on explique la
prediction d'un patient en attribuant a chaque facteur clinique sa valeur de
Shapley (valeur SHAP interventionnelle). On verifie la *local accuracy*
(efficacite) et on compare exact vs Monte Carlo. Le diagramme "waterfall"
montre comment les facteurs construisent la prediction a partir de la moyenne.
"""

import os

import _bootstrap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.ensemble import GradientBoostingRegressor

from applications.shap_ml import explain_instance

# 6 facteurs cliniques interpretables (libelles parlants) parmi les 10 du jeu
FEATURES = ["bmi", "s5", "bp", "s3", "age", "s6"]
LABELS = {
    "bmi": "IMC",
    "s5": "triglycerides",
    "bp": "tension arterielle",
    "s3": "cholesterol HDL",
    "age": "age",
    "s6": "glycemie",
}


def main():
    data = load_diabetes()
    idx = [data.feature_names.index(f) for f in FEATURES]
    X = data.data[:, idx]
    y = data.target
    names = [LABELS[f] for f in FEATURES]

    model = GradientBoostingRegressor(random_state=0).fit(X, y)
    background = X[:150]
    preds = model.predict(X)

    # instance a "histoire claire" : un patient a risque eleve (prediction la
    # plus forte) -> la plupart des facteurs poussent dans le meme sens.
    x_star = X[int(np.argmax(preds))]

    rep = explain_instance(model, x_star, background, names,
                           mc_samples=5000, seed=1)

    print("=" * 64)
    print("EXPLICABILITE ML : VALEURS SHAP = VALEUR DE SHAPLEY")
    print("=" * 64)
    print(f"jeu de donnees        : diabetes (progression a 1 an)")
    print(f"prediction f(x*)      : {rep['prediction']:.1f}")
    print(f"baseline E[f]         : {rep['baseline']:.1f}")
    print(f"ecart a expliquer     : {rep['ecart_a_expliquer']:.1f}")
    print(f"somme des SHAP        : {rep['somme_shap']:.1f}")
    print(f"local accuracy (=efficacite) : {rep['local_accuracy_ok']}")
    if "erreur_mc" in rep:
        print(f"erreur MC vs exact    : {rep['erreur_mc']:.3f}")
    print("\nContributions SHAP (facteurs tries par |contribution|) :")
    order = np.argsort(-np.abs(rep["shap_exact"]))
    for i in order:
        print(f"    {rep['noms'][i]:20s} : {rep['shap_exact'][i]:+7.2f}")

    # ---- Waterfall lisible : construction de la prediction depuis la moyenne
    phi = rep["shap_exact"]
    baseline = rep["baseline"]
    prediction = rep["prediction"]
    order = np.argsort(np.abs(phi))            # petites contributions en bas
    labels = [rep["noms"][i] for i in order]
    vals = phi[order]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    span = prediction - baseline
    cum = baseline
    for k, v in enumerate(vals):
        color = "#2a9d8f" if v >= 0 else "#e76f51"
        ax.barh(k, v, left=cum, color=color, edgecolor="white", height=0.62,
                zorder=3)
        # etiquette toujours a DROITE de la barre -> jamais sur l'axe des noms
        right_edge = max(cum, cum + v)
        ax.text(right_edge + 0.015 * span, k, f"{v:+.1f}", va="center",
                ha="left", fontsize=9, color=color, fontweight="bold")
        cum += v

    ax.axvline(baseline, color="0.45", ls="--", lw=1.2, zorder=2,
               label=f"moyenne du modele  E[f] = {baseline:.0f}")
    ax.axvline(prediction, color="black", ls="-", lw=1.6, zorder=2,
               label=f"prediction  f(x*) = {prediction:.0f}")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlim(baseline - 0.10 * span, prediction + 0.12 * span)
    ax.set_xlabel("progression predite du diabete")
    ax.set_title("Decomposition SHAP : comment les facteurs construisent la prediction",
                 fontsize=12)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    ax.grid(axis="x", alpha=0.25, zorder=0)
    fig.tight_layout()
    out = os.path.join(_bootstrap.FIGDIR, "shap_waterfall.png")
    fig.savefig(out, dpi=140)
    print(f"\nfigure -> {out}")


if __name__ == "__main__":
    main()
