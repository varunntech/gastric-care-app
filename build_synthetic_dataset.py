import numpy as np
import pandas as pd

"""
Builds a synthetic gastric cancer RISK dataset that matches the fields
your web form uses, and creates a rule-based label so that
high-risk answers clearly map to higher cancer probability.

Columns:
- age (int)
- gender (str: Male/Female)
- ethnicity (str: e.g. East Asian / South Asian / European / African-Caribbean / Latin American / Middle Eastern)
- geographical_location (str: e.g. East Asia / South Asia / Europe / Africa / North America / South America)
- family_history (0/1)
- smoking_habits (0/1)
- alcohol_consumption (0/1)
- helicobacter_pylori_infection (0/1)
- dietary_habits (Low_Salt/High_Salt)
- existing_conditions (None/Chronic Gastritis/Diabetes)
- label (0 = low or moderate risk, 1 = higher cancer risk)
"""


def generate_row(rng: np.random.Generator) -> dict:
    age = rng.integers(18, 90)
    gender = rng.choice(["Male", "Female"])
    ethnicity = rng.choice(
        [
            "East Asian",
            "South Asian",
            "European",
            "African / Caribbean",
            "Latin American",
            "Middle Eastern",
        ]
    )
    geographical_location = rng.choice(
        ["East Asia", "South Asia", "Europe", "Africa", "North America", "South America"]
    )

    # Lifestyle / history
    family_history = rng.binomial(1, 0.25)  # 25% have family history
    smoking_habits = rng.binomial(1, 0.35)  # 35% smoke or used to
    alcohol_consumption = rng.binomial(1, 0.4)
    helicobacter_pylori_infection = rng.binomial(1, 0.3)

    dietary_habits = rng.choice(["Low_Salt", "High_Salt"], p=[0.6, 0.4])
    existing_conditions = rng.choice(
        ["None", "Chronic Gastritis", "Diabetes"], p=[0.55, 0.3, 0.15]
    )

    # Simple risk score: higher = more likely label = 1
    # Balanced so that no single factor dominates.
    risk_score = 0.0

    # Age (moderate contribution)
    if age >= 70:
        risk_score += 2.0
    elif age >= 55:
        risk_score += 1.4
    elif age >= 40:
        risk_score += 0.8

    # Clinical / family factors (balanced)
    risk_score += family_history * 1.3
    risk_score += helicobacter_pylori_infection * 1.6

    # Lifestyle
    risk_score += smoking_habits * 1.2
    risk_score += alcohol_consumption * 0.8
    if dietary_habits == "High_Salt":
        risk_score += 1.0

    # Existing conditions
    if existing_conditions == "Chronic Gastritis":
        risk_score += 1.4
    elif existing_conditions == "Diabetes":
        risk_score += 0.6

    # Small randomness so points near threshold are not all identical
    risk_score += rng.normal(0, 0.8)

    # Count major risk factors – we only allow "high" risk if there are
    # multiple strong factors together (not just family history alone).
    major_flags = [
        family_history,
        helicobacter_pylori_infection,
        1 if dietary_habits == "High_Salt" else 0,
        1 if existing_conditions == "Chronic Gastritis" else 0,
        smoking_habits,
    ]
    n_major = sum(major_flags)

    # Map score -> base probability of label=1
    #   score < 3.0  -> mostly label 0
    #   score > 5.0  -> mostly label 1 (but only if multiple major factors)
    #   in-between   -> mixed, to let ML learn probabilities
    if risk_score < 3.0:
        prob_label1 = 0.1
    elif risk_score < 5.0:
        prob_label1 = 0.45
    else:
        prob_label1 = 0.8

    # Safety: if there is 0 or 1 major risk factor only,
    # cap probability so it cannot be "high" purely from a single factor.
    if n_major <= 1 and prob_label1 > 0.45:
        prob_label1 = 0.45

    label = int(rng.random() < prob_label1)

    return {
        "age": int(age),
        "gender": gender,
        "ethnicity": ethnicity,
        "geographical_location": geographical_location,
        "family_history": int(family_history),
        "smoking_habits": int(smoking_habits),
        "alcohol_consumption": int(alcohol_consumption),
        "helicobacter_pylori_infection": int(helicobacter_pylori_infection),
        "dietary_habits": dietary_habits,
        "existing_conditions": existing_conditions,
        "label": label,
    }


def main(n_samples: int = 3000, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    rows = [generate_row(rng) for _ in range(n_samples)]
    df = pd.DataFrame(rows)
    out_path = "synthetic_gastric_risk_dataset.csv"
    df.to_csv(out_path, index=False)
    print(f"✅ Synthetic dataset saved to: {out_path} (rows={len(df)})")
    print(df.head())


if __name__ == "__main__":
    main()


