"""
train_delay_model.py — SmartRoute AI ML Delay Prediction Trainer
===================================================================
Inspects maritime shipment data, builds a scikit-learn ColumnTransformer
+ RandomForestRegressor pipeline, evaluates model performance against baseline,
computes feature importances, and saves the trained pipeline to delay_model.pkl.

Workflow:
    CSV -> Data Inspection -> Feature Selection -> Pipeline -> Train/Test Split
        -> RandomForest Training -> Evaluation -> Feature Importance -> Save .pkl
"""

import os
import sys
import warnings
import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure src directory is importable
_ML_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_ML_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


def inspect_data(df: pd.DataFrame) -> None:
    """Step 1: Inspect the dataset structure and quality."""
    print("=" * 80)
    print("STEP 1: DATA INSPECTION SUMMARY")
    print("=" * 80)
    print(f"Total Rows:     {len(df)}")
    print(f"Total Columns:  {len(df.columns)}")
    print("\nColumn Names and Data Types:")
    for col, dtype in zip(df.columns, df.dtypes):
        print(f"  - {col:<32} {str(dtype):<10} Missing: {df[col].isnull().sum()}")

    print(f"\nDuplicate Rows: {df.duplicated().sum()}")
    
    if "actual_delay_days" not in df.columns:
        raise ValueError("Target column 'actual_delay_days' is missing from the dataset!")

    print("\nTarget Variable ('actual_delay_days') Summary Statistics:")
    target_stats = df["actual_delay_days"].describe()
    print(target_stats.to_string())
    print("-" * 80)


def build_and_train_model(csv_path: str):
    """Main training workflow."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset CSV not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # 1. Data Inspection
    inspect_data(df)

    # 2. Feature Selection
    print("\n" + "=" * 80)
    print("STEP 2: FEATURE SELECTION")
    print("=" * 80)

    target_col = "actual_delay_days"
    ignore_cols = ["shipment_id", target_col]

    feature_cols = [col for col in df.columns if col not in ignore_cols]

    categorical_cols = df[feature_cols].select_dtypes(include=["object", "category", "string"]).columns.tolist()
    numerical_cols = df[feature_cols].select_dtypes(include=["number"]).columns.tolist()

    print(f"Predictor Features ({len(feature_cols)} total):")
    print(f"  - Categorical ({len(categorical_cols)}): {categorical_cols}")
    print(f"  - Numerical   ({len(numerical_cols)}): {numerical_cols}")
    print(f"Excluded Columns: {ignore_cols} (avoiding target leakage and ID bias)")

    X = df[feature_cols]
    y = df[target_col]

    # 3. Preprocessing Pipeline Architecture
    print("\n" + "=" * 80)
    print("STEP 3: PREPROCESSING & PIPELINE ARCHITECTURE")
    print("=" * 80)

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numerical_cols),
            ("cat", cat_pipeline, categorical_cols),
        ]
    )

    model_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        ))
    ])

    print("Pipeline constructed successfully:")
    print("  ColumnTransformer -> (Numerical: Median Imputer + StandardScaler, Categorical: MostFrequent Imputer + OneHotEncoder)")
    print("  Regressor         -> RandomForestRegressor(n_estimators=200, random_state=42)")

    # 4. Train / Test Split
    print("\n" + "=" * 80)
    print("STEP 4: TRAIN / TEST SPLIT (80% / 20%, random_state=42)")
    print("=" * 80)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"Training Samples: {X_train.shape[0]}")
    print(f"Testing Samples:  {X_test.shape[0]}")

    # 5. Fit Model & Baseline
    print("\nTraining Random Forest Regressor...")
    model_pipeline.fit(X_train, y_train)

    # Train Baseline Model (Mean Predictor)
    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)

    # 6. Evaluation
    print("\n" + "=" * 80)
    print("STEP 6: MODEL EVALUATION & BASELINE COMPARISON")
    print("=" * 80)

    y_pred = model_pipeline.predict(X_test)
    y_base_pred = baseline.predict(X_test)

    rf_mae = mean_absolute_error(y_test, y_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    rf_r2 = r2_score(y_test, y_pred)

    base_mae = mean_absolute_error(y_test, y_base_pred)
    base_rmse = np.sqrt(mean_squared_error(y_test, y_base_pred))
    base_r2 = r2_score(y_test, y_base_pred)

    print(f"{'Metric':<15} {'Mean Baseline':<20} {'Random Forest Regressor':<25}")
    print("-" * 60)
    print(f"{'MAE (days)':<15} {base_mae:<20.4f} {rf_mae:<25.4f}")
    print(f"{'RMSE (days)':<15} {base_rmse:<20.4f} {rf_rmse:<25.4f}")
    print(f"{'R² Score':<15} {base_r2:<20.4f} {rf_r2:<25.4f}")

    print("\nMetric Definitions:")
    print("  - MAE  (Mean Absolute Error): Average absolute difference in predicted vs actual delay days.")
    print("  - RMSE (Root Mean Squared Error): Square root of mean squared errors, penalizing larger deviations.")
    print("  - R²   (Coefficient of Determination): Proportion of variance in actual_delay_days explained by model.")

    # 7. Feature Importance Mapping
    print("\n" + "=" * 80)
    print("STEP 10: FEATURE IMPORTANCE")
    print("=" * 80)

    rf_model = model_pipeline.named_steps["regressor"]
    prep = model_pipeline.named_steps["preprocessor"]

    num_feature_names = numerical_cols
    cat_feature_names = prep.named_transformers_["cat"].named_steps["encoder"].get_feature_names_out(categorical_cols).tolist()
    all_feature_names = num_feature_names + cat_feature_names

    importances = rf_model.feature_importances_

    # Map OneHotEncoded features back to original feature groups for clean reporting
    feature_importance_df = pd.DataFrame({
        "Feature": all_feature_names,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False)

    print("\nTop 15 Most Important Features:")
    print(f"{'Feature':<45} {'Importance':<15}")
    print("-" * 60)
    for _, row in feature_importance_df.head(15).iterrows():
        print(f"{row['Feature']:<45} {row['Importance']:<15.4f}")

    # 8. Model Saving
    print("\n" + "=" * 80)
    print("STEP 7: SAVING MODEL PIPELINE")
    print("=" * 80)

    model_dir = os.path.join(_ML_DIR, "model")
    os.makedirs(model_dir, exist_ok=True)
    model_save_path = os.path.join(model_dir, "delay_model.pkl")

    joblib.dump(model_pipeline, model_save_path)
    print(f"Successfully saved trained model pipeline to:\n  {model_save_path}")

    return {
        "mae": rf_mae,
        "rmse": rf_rmse,
        "r2": rf_r2,
        "model_path": model_save_path,
        "top_features": feature_importance_df.head(10).to_dict(orient="records"),
    }


if __name__ == "__main__":
    csv_file = os.path.join(_SRC_DIR, "data", "smartroute_maritime_historical_shipments_10000.csv")
    build_and_train_model(csv_file)
