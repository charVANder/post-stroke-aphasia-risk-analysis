.PHONY: cohort eda tables summary mh_visuals pim_visuals high_risk_visuals \
        readmissions features modeling statistics clinical-impact predictive-pipeline all help

cohort:
	@echo "Creating base cohort..."
	python -B src/create_cohort.py

eda:
	@echo "Running exploratory data analysis..."
	python -B src/eda.py

tables:
	@echo "Creating mental health and PIM tables..."
	python -B src/create_mh_table.py
	python -B src/create_pim_table.py

summary:
	@echo "Generating summary statistics..."
	python -B src/results.py

mh_visuals:
	@echo "Creating mental health visualizations..."
	python -B src/visualize_mh.py

pim_visuals:
	@echo "Creating PIM visualizations..."
	python -B src/visualize_pim.py

high_risk_visuals:
	@echo "Creating high-risk visualizations..."
	python -B src/visualize_risk.py

readmissions:
	@echo "Extracting readmission data from OMOP database..."
	@echo "This may take several minutes..."
	python -B src/extract_readmission_data.py

features:
	@echo "Engineering features for predictive modeling..."
	python -B src/feature_engineering.py

modeling:
	@echo "Training predictive models..."
	@echo "This will take 5-10 minutes (XGBoost + SHAP analysis)..."
	python -B src/predictive_modeling.py

statistics:
	@echo "Running multivariate statistical analyses..."
	python -B src/multivariate_analyses.py

clinical-impact:
	@echo "Running clinical impact analysis..."
	python -B src/clinical_impact/run_analysis.py


# Run complete predictive modeling pipeline
predictive-pipeline: readmissions features modeling statistics
	@echo "PREDICTIVE MODELING PIPELINE COMPLETE"
	@echo "Results saved to: src/output/"

# Run everything (original + predictive modeling + clinical impact modeling )
all: cohort tables summary mh_visuals pim_visuals high_risk_visuals predictive-pipeline clinical-impact
	@echo "COMPLETE ANALYSIS PIPELINE FINISHED"


help:
	@echo "Available targets:"
	@echo ""
	@echo "Original Pipeline:"
	@echo "  cohort            - Create base stroke cohort"
	@echo "  eda               - Exploratory data analysis"
	@echo "  tables            - Create mental health and PIM tables"
	@echo "  summary           - Generate summary statistics"
	@echo "  mh_visuals        - Mental health visualizations"
	@echo "  pim_visuals       - PIM visualizations"
	@echo "  high_risk_visuals - High-risk patient visualizations"
	@echo ""
	@echo "Predictive Modeling Pipeline:"
	@echo "  readmissions      - Extract readmission data from database"
	@echo "  features          - Engineer features for modeling"
	@echo "  modeling          - Train predictive models (Logistic, Lasso, XGBoost)"
	@echo "  statistics        - Run multivariate analyses"
	@echo "  clinical-impact   - Clinical impact analysis (modular version)"
	@echo ""
	@echo "Combined Workflows:"
	@echo "  predictive-pipeline - Run complete predictive modeling pipeline"
	@echo "  all                 - Run everything (original + predictive)"
	@echo ""
	@echo "Utility:"
	@echo "  help                - Show this help message"
	@echo ""

.DEFAULT_GOAL := help
