"""
Predictive Modeling for Hospital Readmission Prediction
OHDSI-Stroke Aphasia Research Project

This module trains and evaluates machine learning models to predict 30-/90-day
hospital readmissions in stroke survivors.

Models:
1. Logistic Regression (interpretable baseline)
2. Lasso Logistic Regression (feature selection)
3. XGBoost (best performance)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import (
    roc_auc_score, average_precision_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report, RocCurveDisplay, PrecisionRecallDisplay
)
from xgboost import XGBClassifier
import shap

# Set random seed for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# READMISSION WINDOW CONFIGURATION
# Options: 'has_30day_readmission', 'has_90day_readmission', 'has_180day_readmission'
READMISSION_OUTCOME = 'has_180day_readmission'  # Change this to switch prediction window
READMISSION_DAYS = 180  # For documentation/reporting

# Plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_data(data_path):
    """
    Load engineered dataset.

    Parameters
    ----------
    data_path : str
        Path to the CSV file with engineered features

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe
    """
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} records with {len(df.columns)} columns\n")
    return df


def prepare_data(df, outcome='has_30day_readmission', test_size=0.2):
    """
    Prepare features and outcome for modeling.

    Parameters
    df : pandas.DataFrame
        Input dataframe
    outcome : str
        Target variable name (default: 'has_30day_readmission')
    test_size : float
        Proportion of data for test set (default: 0.2)

    Returns
        X_train, X_test, y_train, y_test, feature_names (tuple)
    """

    print("=-"*60)
    print("DATA PREP")
    print("=-"*60)

    # Feature list (from feature_engineering.py)
    feature_cols = [
        # Demographics
        'has_aphasia',

        # Mental health conditions (individual)
        'has_depression', 'has_anxiety', 'has_seizure', 'has_bipolar',
        'has_schizophrenia', 'has_ptsd', 'has_psychotic_disorder',

        # Mental health (aggregate)
        'has_any_mental_health_condition', 'mh_burden',

        # PIM medications (individual categories)
        'has_antidepressant', 'has_anxiolytic', 'has_antipsychotic', 'has_hypnotic_sedative',

        # PIM (aggregate)
        'has_any_pim', 'total_pim_count', 'pim_diversity', 'max_concurrent_pims',

        # Polypharmacy (all medications)
        'has_polypharmacy_all_meds', 'total_med_count', 'max_concurrent_meds',

        # Risk scores
        'is_high_risk', 'total_risk_score',

        # Medication-diagnosis discordance
        'antidep_risk', 'anxiolytic_risk', 'hyp_sed_risk', 'antipsych_risk',
        'med_dx_discordance', 'has_any_discordance',

        # Interaction features
        'aphasia_x_mh', 'aphasia_x_highrisk', 'aphasia_x_polypharm',

        # High-risk combinations
        'antidep_anxio_combo', 'multiple_discordances', 'high_med_burden', 'complex_patient'
    ]

    # Check for missing columns
    missing_cols = [col for col in feature_cols if col not in df.columns]
    if missing_cols:
        print(f"WARNING: Missing columns: {missing_cols}")
        feature_cols = [col for col in feature_cols if col in df.columns]

    # Check outcome variable
    if outcome not in df.columns:
        raise ValueError(f"Outcome variable '{outcome}' not found in dataset!")

    # Filter to patients with PIMs only (can't have readmission without PIM date)
    df_filtered = df[df['has_any_pim'] == 1].copy()
    print(f"Filtered to {len(df_filtered):,} patients with PIMs\n")

    # Extract features and outcome
    X = df_filtered[feature_cols].copy()
    y = df_filtered[outcome].copy()

    # Data quality checks
    print("Data Quality Checks:")
    print(f"  Total patients: {len(X):,}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Missing values: {X.isnull().sum().sum()}")

    # Class distribution
    print(f"\nOutcome: {outcome}")
    print(f"  Positive class: {y.sum():,} ({y.mean()*100:.1f}%)")
    print(f"  Negative class: {(~y.astype(bool)).sum():,} ({(1-y.mean())*100:.1f}%)")

    if y.mean() < 0.05:
        print("\n  ?????????? WARNING: Severe class imbalance (<5% positive class)")
        print("  use BalancedRandomForest")

    # Train/test split (stratified)
    print(f"\nSplitting data (test_size={test_size}, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=y,
        random_state=RANDOM_STATE
    )

    print(f"Training set: {len(X_train):,} ({len(X_train)/len(X)*100:.1f}%)")
    print(f" Test set: {len(X_test):,} ({len(X_test)/len(X)*100:.1f}%)")
    print(f" Train positive rate: {y_train.mean()*100:.1f}%")
    print(f" Test positive rate: {y_test.mean()*100:.1f}%")

    print("="*60 + "\n")

    return X_train, X_test, y_train, y_test, feature_cols


def evaluate_model(model, X_test, y_test, model_name, feature_names=None):
    """
    Comprehensive model evaluation.

    Parameters
    ----------
    model : sklearn model
        Trained model
    X_test : pandas.DataFrame
        Test features
    y_test : pandas.Series
        Test outcomes
    model_name : str
        Name of the model for display
    feature_names : list, optional
        List of feature names

    Returns
        Dictionary of evaluation metrics (dict)
    """

    print("=-"*60)
    print(f"EVAL: {model_name}")
    print("=-"*60)

    # Predictions
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    # Find optimal threshold using Youden's J statistic
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]

    y_pred = (y_pred_proba >= optimal_threshold).astype(int)
    y_pred_50 = (y_pred_proba >= 0.5).astype(int)

    # Metrics
    auroc = roc_auc_score(y_test, y_pred_proba)
    auprc = average_precision_score(y_test, y_pred_proba)

    print(f"\nPerformance Metrics:")
    print(f"  AUROC: {auroc:.3f}")
    print(f"  AUPRC: {auprc:.3f}")
    print(f"  Optimal Threshold (Youden's J): {optimal_threshold:.3f}")

    print(f"\nClassification Report (threshold={optimal_threshold:.3f}):")
    print(classification_report(y_test, y_pred, target_names=['No Readmission', 'Readmission']))

    print(f"\nClassification Report (threshold=0.5):")
    print(classification_report(y_test, y_pred_50, target_names=['No Readmission', 'Readmission']))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix (threshold={optimal_threshold:.3f}):")
    print(f"                Predicted")
    print(f"                No    Yes")
    print(f"Actual No    {cm[0,0]:5d} {cm[0,1]:5d}")
    print(f"       Yes   {cm[1,0]:5d} {cm[1,1]:5d}")

    print("="*60 + "\n")

    return {
        'model_name': model_name,
        'auroc': auroc,
        'auprc': auprc,
        'optimal_threshold': optimal_threshold,
        'confusion_matrix': cm,
        'y_pred_proba': y_pred_proba
    }


def train_logistic_regression(X_train, y_train, X_test, y_test, feature_names):
    """
    Train and evaluate Logistic Regression.

    Parameters
    ----------
    X_train, y_train : Training data
    X_test, y_test : Test data
    feature_names : list
        Feature names

    Returns
    -------
    tuple
        (model, evaluation_results, coefficients_df)
    """

    print("="*60)
    print("TRAINING: Logistic Regression")
    print("="*60)

    model = LogisticRegression(
        penalty='l2',
        C=1.0,
        class_weight='balanced',  # Handle imbalanced classes
        max_iter=1000,
        random_state=RANDOM_STATE
    )

    print("\nFitting model...")
    model.fit(X_train, y_train)
    print("Done!\n")

    # Evaluate
    results = evaluate_model(model, X_test, y_test, "Logistic Regression", feature_names)

    # Extract coefficients
    coef_df = pd.DataFrame({
        'feature': feature_names,
        'coefficient': model.coef_[0],
        'odds_ratio': np.exp(model.coef_[0]),
        'abs_coef': np.abs(model.coef_[0])
    }).sort_values('abs_coef', ascending=False)

    print("Top 10 Predictors (by coefficient magnitude):")
    print(coef_df[['feature', 'coefficient', 'odds_ratio']].head(10).to_string(index=False))
    print("\n")

    return model, results, coef_df


def train_lasso_regression(X_train, y_train, X_test, y_test, feature_names):
    """
    Train and evaluate Lasso Logistic Regression.

    Parameters
    ----------
    X_train, y_train : Training data
    X_test, y_test : Test data
    feature_names : list
        Feature names

    Returns
    -------
    tuple
        (model, evaluation_results, coefficients_df)
    """

    print("="*60)
    print("TRAINING: Lasso Logistic Regression (L1 Regularization)")
    print("="*60)

    model = LogisticRegressionCV(
        penalty='l1',
        solver='saga',
        cv=5,
        class_weight='balanced',
        random_state=RANDOM_STATE,
        max_iter=5000,
        n_jobs=-1
    )

    print("\nFitting model with 5-fold cross-validation...")
    print("This may take a few minutes...")
    model.fit(X_train, y_train)
    print(f"Done! Best C: {model.C_[0]:.4f}\n")

    # Evaluate
    results = evaluate_model(model, X_test, y_test, "Lasso Logistic Regression", feature_names)

    # Extract coefficients
    coef_df = pd.DataFrame({
        'feature': feature_names,
        'coefficient': model.coef_[0],
        'odds_ratio': np.exp(model.coef_[0]),
        'abs_coef': np.abs(model.coef_[0])
    }).sort_values('abs_coef', ascending=False)

    # Count non-zero coefficients
    n_selected = (coef_df['coefficient'] != 0).sum()
    print(f"Feature Selection: {n_selected}/{len(feature_names)} features selected")

    print("\nTop 10 Selected Features:")
    print(coef_df[coef_df['coefficient'] != 0][['feature', 'coefficient', 'odds_ratio']].head(10).to_string(index=False))
    print("\n")

    return model, results, coef_df


def train_xgboost(X_train, y_train, X_test, y_test, feature_names):
    """
    Train and evaluate XGBoost.

    Parameters
    ----------
    X_train, y_train : Training data
    X_test, y_test : Test data
    feature_names : list
        Feature names

    Returns
    -------
    tuple
        (model, evaluation_results, feature_importance_df)
    """

    print("=-"*60)
    print("TRAINING: XGBoost")
    print("=-"*60)

    # Calculate scale_pos_weight for class imbalance
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    scale_weight = n_neg / n_pos

    print(f"\nClass imbalance: {n_pos} positive / {n_neg} negative")
    print(f"scale_pos_weight: {scale_weight:.2f}")

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.01,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_weight,
        eval_metric='auc',
        random_state=RANDOM_STATE,
        use_label_encoder=False,
        n_jobs=-1
    )

    print("\nFitting model...")
    model.fit(X_train, y_train)
    print("Done!\n")

    # Evaluate
    results = evaluate_model(model, X_test, y_test, "XGBoost", feature_names)

    # Feature importance
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("Top 10 Important Features:")
    print(importance_df.head(10).to_string(index=False))
    print("\n")

    return model, results, importance_df


def compare_models(results_list):
    """
    Compare multiple models side-by-side.

    Parameters
    results_list : list of dict
        List of evaluation results from evaluate_model()

    -------
    p.DF
        Comparison table
    """

    print("=-"*60)
    print("MODEL COMPARISON")
    print("=-"*60 + "\n")

    comparison_df = pd.DataFrame([
        {
            'Model': r['model_name'],
            'AUROC': f"{r['auroc']:.3f}",
            'AUPRC': f"{r['auprc']:.3f}",
            'Optimal Threshold': f"{r['optimal_threshold']:.3f}"
        }
        for r in results_list
    ])

    print(comparison_df.to_string(index=False))
    print("\n")

    # Determine best model
    auroc_values = [r['auroc'] for r in results_list]
    best_idx = np.argmax(auroc_values)
    best_model = results_list[best_idx]['model_name']
    best_auroc = auroc_values[best_idx]

    print(f"Best Model (by AUROC): {best_model} ({best_auroc:.3f})")
    print("="*60 + "\n")

    return comparison_df


def interpret_xgboost_shap(model, X_test, feature_names, output_dir):
    """
    SHAP analysis for XGBoost interpretability.

    Parameters
    model : XGBClassifier
        Trained XGBoost model
    X_test : pandas.DataFrame
        Test features
    feature_names : list
        Feature names
    output_dir : str
        Directory to save plots
    """

    print("=-"*60)
    print("SHAP ANALYSIS (XGBoost Interpretability)")
    print("-="*60 + "\n")

    print("Computing SHAP values...")
    print("This may take a few minutes...\n")

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # Summary plot (beeswarm)
    print("Creating SHAP summary plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_summary.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {os.path.join(output_dir, 'shap_summary.png')}")

    # Feature importance (bar)
    print("Creating SHAP feature importance plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names, plot_type='bar', show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_importance.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {os.path.join(output_dir, 'shap_importance.png')}")

    print("\nSHAP analysis complete!")
    print("="*60 + "\n")

    return shap_values


def subgroup_performance(model, X_test, y_test, model_name):
    """
    Evaluate model separately for aphasia vs. non-aphasia patients.

    Parameters
    model : sklearn model
        Trained model
    X_test : pandas.DataFrame
        Test features
    y_test : pandas.Series
        Test outcomes
    model_name : str
        Name of the model
    """

    print("=-"*60)
    print(f"SUBGROUP PERFORMANCE: {model_name}")
    print("=-"*60 + "\n")

    # Split by aphasia status
    aphasia_mask = X_test['has_aphasia'] == 1

    X_aphasia = X_test[aphasia_mask]
    y_aphasia = y_test[aphasia_mask]

    X_no_aphasia = X_test[~aphasia_mask]
    y_no_aphasia = y_test[~aphasia_mask]

    print(f"Aphasia group: {len(y_aphasia):,} patients")
    print(f"No Aphasia group: {len(y_no_aphasia):,} patients\n")

    # Evaluate separately
    y_pred_aphasia = model.predict_proba(X_aphasia)[:, 1]
    y_pred_no_aphasia = model.predict_proba(X_no_aphasia)[:, 1]

    auroc_aphasia = roc_auc_score(y_aphasia, y_pred_aphasia)
    auroc_no_aphasia = roc_auc_score(y_no_aphasia, y_pred_no_aphasia)

    auprc_aphasia = average_precision_score(y_aphasia, y_pred_aphasia)
    auprc_no_aphasia = average_precision_score(y_no_aphasia, y_pred_no_aphasia)

    print("Performance by Subgroup:")
    print(f"  Aphasia:")
    print(f"    AUROC: {auroc_aphasia:.3f}")
    print(f"    AUPRC: {auprc_aphasia:.3f}")
    print(f"  No Aphasia:")
    print(f"    AUROC: {auroc_no_aphasia:.3f}")
    print(f"    AUPRC: {auprc_no_aphasia:.3f}")
    print(f"  Difference (Aphasia - No Aphasia):")
    print(f"    AUROC: {auroc_aphasia - auroc_no_aphasia:+.3f}")
    print(f"    AUPRC: {auprc_aphasia - auprc_no_aphasia:+.3f}")

    if abs(auroc_aphasia - auroc_no_aphasia) > 0.05:
        print("\n  ⚠ WARNING: Performance differs by >0.05 between groups")
        print("  Consider training separate models or investigating bias")
    else:
        print("\n  ✓ Performance is similar across subgroups")

    print("="*60 + "\n")


def plot_roc_curves(results_list, output_dir):
    """
    Plot ROC curves for all models on same plot.

    Parameters
    results_list : list of dict
        List of evaluation results
    output_dir :
        Directory to save plot (str
    """

    print("Creating ROC curve comparison plot...")

    plt.figure(figsize=(10, 8))

    for result in results_list:
        fpr, tpr, _ = roc_curve(y_test, result['y_pred_proba'])
        plt.plot(fpr, tpr, label=f"{result['model_name']} (AUC={result['auroc']:.3f})")

    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves: Model Comparison')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_file = os.path.join(output_dir, 'roc_curves_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}\n")


def plot_odds_ratios(coef_df, model_name, output_dir, top_n=15):
    """
    Plot odds ratios from logistic regression.

    Parameters
    coef_df : p.DF
    model_name
        Name of the model
    output_dir
        Directory to save plot
    top_n
        Number of top features to plot
    """

    print(f"Creating odds ratio plot for {model_name}...")

    # Get top features
    top_features = coef_df.head(top_n).copy()

    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['odds_ratio'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Odds Ratio')
    plt.title(f'Top {top_n} Predictors of Hospital Readmission\n{model_name}')
    plt.axvline(x=1, color='red', linestyle='--', label='OR = 1 (no effect)')
    plt.legend()
    plt.grid(axis='x')
    plt.tight_layout()

    output_file = os.path.join(output_dir, f'odds_ratios_{model_name.replace(" ", "_").lower()}.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_file}\n")



if __name__ == '__main__':

    print("\n" + "=-"*60)
    print("HOSPITAL READMISSION PREDICTION")
    print("="*60 + "\n")

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    FIGS_DIR = os.path.join(BASE_DIR, "..", "figs")
    MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

    # Create output directories if they don't exist
    os.makedirs(FIGS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    INPUT_FILE = os.path.join(DATA_DIR, 'high_risk_cohort_engineered_features.csv')

    # Load data
    df = load_data(INPUT_FILE)

    # Prepare data for readmission prediction (window configured above)
    X_train, X_test, y_train, y_test, feature_names = prepare_data(
        df,
        outcome=READMISSION_OUTCOME,
        test_size=0.2
    )

    # Train models
    print("-MODEL TRAINING-")

    # 1. Logistic Regression
    lr_model, lr_results, lr_coef = train_logistic_regression(
        X_train, y_train, X_test, y_test, feature_names
    )

    # 2. Lasso Logistic Regression
    lasso_model, lasso_results, lasso_coef = train_lasso_regression(
        X_train, y_train, X_test, y_test, feature_names
    )

    # 3. XGBoost
    xgb_model, xgb_results, xgb_importance = train_xgboost(
        X_train, y_train, X_test, y_test, feature_names
    )

    # Compare models
    all_results = [lr_results, lasso_results, xgb_results]
    comparison_df = compare_models(all_results)

    # Save comparison table
    comparison_df.to_csv(os.path.join(DATA_DIR, 'model_comparison.csv'), index=False)

    # Visualizations
    print("\n" + "="*60)
    print("CREATING VISUALIZATIONS")
    print("="*60 + "\n")

    # ROC curves
    plot_roc_curves(all_results, FIGS_DIR)

    # Odds ratios
    plot_odds_ratios(lr_coef, "Logistic Regression", FIGS_DIR)
    plot_odds_ratios(lasso_coef, "Lasso Logistic Regression", FIGS_DIR)

    # SHAP analysis for XGBoost
    shap_values = interpret_xgboost_shap(xgb_model, X_test, feature_names, FIGS_DIR)

    # Subgroup analysis
    print("SUBGROUP ANALYSIS (Fairness Check)")

    subgroup_performance(lr_model, X_test, y_test, "Logistic Regression")
    subgroup_performance(lasso_model, X_test, y_test, "Lasso Logistic Regression")
    subgroup_performance(xgb_model, X_test, y_test, "XGBoost")

    # Save models
    print("SAVING MODELS")

    import pickle

    models = {
        'logistic_regression': lr_model,
        'lasso_regression': lasso_model,
        'xgboost': xgb_model
    }

    for name, model in models.items():
        model_file = os.path.join(MODELS_DIR, f'{name}_model.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)
        print(f"Saved: {model_file}")

    # Save coefficients and importance
    lr_coef.to_csv(os.path.join(DATA_DIR, 'logistic_regression_coefficients.csv'), index=False)
    lasso_coef.to_csv(os.path.join(DATA_DIR, 'lasso_regression_coefficients.csv'), index=False)
    xgb_importance.to_csv(os.path.join(DATA_DIR, 'xgboost_feature_importance.csv'), index=False)

    print("ANALYSIS COMPLETE!")
    print(f"\nResults saved to:")
    print(f"  Data files: {DATA_DIR}")
    print(f"  Figures: {FIGS_DIR}")
    print(f"  Models: {MODELS_DIR}")
    print("\nGenerated files:")
    print("  - model_comparison.csv")
    print("  - roc_curves_comparison.png")
    print("  - odds_ratios_*.png")
    print("  - shap_*.png")
    print("  - *_model.pkl")
    print("  - *_coefficients.csv")
