"""
Demo 5: the wiki agent wrapped as an MLflow model, so it can be registered in Unity Catalog.

This uses MLflow's "models from code" style: MLflow logs THIS FILE, and loads the model by running it. The last line tells MLflow which object is the model.

The agent itself is unchanged: `predict` just calls `answer_question` from agent_traced.py.
"""

import mlflow
from mlflow.pyfunc import PythonModel


def _question(model_input) -> str:
    """Accept a plain string, a dict, a list, or a one-row DataFrame."""
    if isinstance(model_input, str):
        return model_input
    if isinstance(model_input, dict):
        return model_input["question"]
    if hasattr(model_input, "iloc"):  # pandas DataFrame
        return str(model_input["question"].iloc[0])
    return str(model_input[0])


class WikiAgent(PythonModel):
    def predict(self, model_input, params=None):
        # Imported here (not at the top) so merely logging the model creates no LLM client.
        from common.agent_traced import answer_question

        return answer_question(_question(model_input))


mlflow.models.set_model(WikiAgent())
