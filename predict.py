import numpy as np
import pandas as pd
import joblib
from scipy.sparse import hstack, csr_matrix

MODEL_DIR = "models"

MISSING_FLAG_COLS = [
    "salary_range", "required_experience", "employment_type",
    "company_profile", "required_education", "industry",
]

TEXT_COLS = ["title", "company_profile", "description", "requirements", "benefits"]

CAT_COLS = [
    "employment_type", "required_experience", "required_education",
    "industry", "function", "department",
]


class FraudDetector:
    def __init__(self, model_dir: str = MODEL_DIR):
        self.model = joblib.load(f"{model_dir}/logistic_regression_model.pkl")
        self.tfidf = joblib.load(f"{model_dir}/tfidf_vectorizer.pkl")
        self.feature_cols = joblib.load(f"{model_dir}/tabular_feature_columns.pkl")

    def _build_row(self, posting: dict) -> pd.DataFrame:
        
        row = {col: posting.get(col, np.nan) for col in TEXT_COLS + CAT_COLS + ["salary_range"]}
        df = pd.DataFrame([row])

        # Missingness flags — computed BEFORE filling NaNs, same as training
        for col in MISSING_FLAG_COLS:
            df[f"{col}_missing"] = df[col].isnull().astype(int)

        # Fill text NaNs with '' and build the combined text field
        for col in TEXT_COLS:
            df[col] = df[col].fillna("")
        df["text_combined"] = (
            df["title"] + " " + df["company_profile"] + " " + df["description"]
            + " " + df["requirements"] + " " + df["benefits"]
        )

        for col in CAT_COLS:
            df[col] = df[col].fillna("Unknown")

        df_encoded = pd.get_dummies(df, columns=CAT_COLS, drop_first=True)

        tab_row = df_encoded.reindex(columns=self.feature_cols, fill_value=0)
        tab_row = tab_row.astype(np.float32)

        return df_encoded["text_combined"], tab_row

    def predict(self, posting: dict) -> dict:
        
        text_row, tab_row = self._build_row(posting)

        text_tfidf = self.tfidf.transform(text_row)
        fused = hstack([text_tfidf, csr_matrix(tab_row.values)])

        proba = self.model.predict_proba(fused)[0, 1]
        label = "Fraud" if proba >= 0.5 else "Not Fraud"

        reasons = self._explain(fused)

        return {"fraud_probability": float(proba), "label": label, "reasons": reasons}

    def _explain(self, fused, top_n: int = 5) -> list:
        
        feature_names = np.concatenate([
            self.tfidf.get_feature_names_out(),
            np.array(self.feature_cols),
        ])
        coefs = self.model.coef_[0]

        row = fused.toarray()[0]
        contributions = row * coefs  # elementwise: value * weight per feature

        nonzero_idx = np.nonzero(row)[0]
        if len(nonzero_idx) == 0:
            return []

        # Sort nonzero-feature contributions by absolute impact, take top_n
        sorted_idx = nonzero_idx[np.argsort(-np.abs(contributions[nonzero_idx]))]
        top_idx = sorted_idx[:top_n]

        reasons = []
        for i in top_idx:
            direction = "toward Fraud" if contributions[i] > 0 else "toward Not Fraud"
            reasons.append({
                "feature": feature_names[i],
                "direction": direction,
                "weight": float(contributions[i]),
            })
        return reasons


if __name__ == "__main__":
    detector = FraudDetector()

    scam_example = {
        "title": "Work From Home - Earn $5000/week!",
        "description": "Send us your bank details to get started immediately.",
        "employment_type": "Full-time",
    }
    scam_result = detector.predict(scam_example)
    print("Scam-style:", scam_result["label"], scam_result["fraud_probability"])
    for r in scam_result["reasons"]:
        print(f"  - {r['feature']} ({r['direction']}, weight={r['weight']:.3f})")

    legit_example = {
        "title": "Senior Software Engineer",
        "company_profile": "We are an established fintech company based in Bangalore, founded in 2015, with over 200 employees.",
        "description": "We are looking for a senior backend engineer to join our growing team, working on distributed systems and microservices architecture.",
        "requirements": "5+ years of experience with Python, Go, or Java. Strong understanding of distributed systems.",
        "benefits": "Health insurance, flexible working hours, annual performance bonus, remote work options.",
        "employment_type": "Full-time",
        "required_experience": "Mid-Senior level",
        "required_education": "Bachelor's Degree",
        "industry": "Information Technology and Services",
    }
    legit_result = detector.predict(legit_example)
    print("\nLegit-style:", legit_result["label"], legit_result["fraud_probability"])
    for r in legit_result["reasons"]:
        print(f"  - {r['feature']} ({r['direction']}, weight={r['weight']:.3f})")