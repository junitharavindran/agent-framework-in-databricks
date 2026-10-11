# Ref: https://mlflow.org/docs/latest/ml/getting-started/running-notebooks/

import mlflow

#================================================
# Configure tracking

# MLflow supports different backends for tracking your experiment data:
# 1. Local database
# 2. Remote server
# 3. Local file storage

TRACKING_OPTION = 1

# Tracking option 1: Set the tracking URI to a local database URI (e.g. sqlite:///mlflow.db).
# NOTE: This is recommended option for quickstart and local development.
if TRACKING_OPTION == 1:
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
# Tracking option 2: Remote tracking server - start a remote MLflow tracking server, then configure your client to use the remote server.
elif TRACKING_OPTION == 2:
    mlflow.set_tracking_uri("http://localhost:5000")
# Tracking option 3: MLflow will automatically use local file storage if no tracking URI is specified.
elif TRACKING_OPTION == 3:
    pass # do nothing; mlflow.set_experiment is sufficient

# NOTE: Alternatively, you can configure the tracking URI and experiment using environment variables MLFLOW_TRACKING_URI and MLFLOW_EXPERIMENT_NAME.

#================================================

mlflow.set_experiment("xyz")


# Start tracking!
# Open http://localhost:5000 in your browser to view the UI.
