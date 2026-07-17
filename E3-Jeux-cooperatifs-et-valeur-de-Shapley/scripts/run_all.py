"""Lance toutes les demonstrations et regenere toutes les figures."""

import _bootstrap  # noqa: F401

import demo_airport
import demo_convergence
import demo_core
import demo_games
import demo_power
import demo_shap


def main():
    for name, module in [
        ("JEUX CLASSIQUES & AXIOMES", demo_games),
        ("CONVERGENCE MONTE CARLO", demo_convergence),
        ("COEUR & CONVEXITE", demo_core),
        ("PARTAGE DE COUTS (AEROPORT)", demo_airport),
        ("INDICES DE POUVOIR (ONU)", demo_power),
        ("EXPLICABILITE ML (SHAP)", demo_shap),
    ]:
        print("\n\n" + "#" * 70)
        print(f"# {name}")
        print("#" * 70)
        module.main()


if __name__ == "__main__":
    main()
