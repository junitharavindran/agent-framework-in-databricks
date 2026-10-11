# Ref: https://mlflow.org/docs/latest/ml/getting-started/running-notebooks/

# PREREQUISITE: Run:
# 
# 1_establish_connection_dev_env_to_mlflow.py

import mlflow

# Print connection information
print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
print(f"Active Experiment: {mlflow.get_experiment_by_name('xyz')}")

# Test logging
with mlflow.start_run():
    mlflow.log_param("test_param", "test_value")
    print("Successfully connected to MLflow!")