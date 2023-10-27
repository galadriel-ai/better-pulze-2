from langsmith import Client
from langchain.smith import RunEvalConfig, run_on_dataset
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

from typing import Optional

from langsmith.evaluation import EvaluationResult, RunEvaluator
from langsmith.schemas import Example, Run


load_dotenv()

client = Client()

DATASET_NAME = "Chat manager test"


class CostEvaluator(RunEvaluator):
    def __init__(self, prediction_key: Optional[str] = None, cost_type: str = "total"):
        self.prediction_key = prediction_key
        self.cost_type = cost_type

    def evaluate_run(
        self, run: Run, example: Optional[Example] = None
    ) -> EvaluationResult:
        if run.outputs is None:
            raise ValueError("Run outputs cannot be None")
        
        llm_output = run.outputs["llm_output"]
        token_usage = llm_output["token_usage"]
        model = llm_output["model_name"]

        tokens_in = token_usage["prompt_tokens"]
        tokens_out = token_usage["completion_tokens"]

        pricing = {
            "gpt-3.5-turbo": {
                "in": 0.0015, # $ per 1000 tokens
                "out": 0.002,
            },
            "gpt-3.5-turbo-16k": {
                "in": 0.003,
                "out": 0.004,
            },
            "gpt-4": {
                "in": 0.03,
                "out": 0.06,
            },
            "gpt-4-32k": {
                "in": 0.06,
                "out": 0.12,
            },
        }

        if model not in pricing:
            raise Exception(f"Don't know how to calculate cost for model {model}")
        
        # Calculate gpt-3.5 equivalent token count
        tokens_in_eq_35: int = round(tokens_in * pricing[model]["in"] / pricing["gpt-3.5-turbo"]["in"])
        tokens_out_eq_35: int = round(tokens_out * pricing[model]["out"] / pricing["gpt-3.5-turbo"]["out"])
        tokens_total_eq_35: int = tokens_in_eq_35 + tokens_out_eq_35

        if self.cost_type == "total":
            return EvaluationResult(key="Token eq total", score=tokens_total_eq_35)
        elif self.cost_type == "in":
            return EvaluationResult(key="Token eq input", score=tokens_in_eq_35)
        elif self.cost_type == "out":
            return EvaluationResult(key="Token eq output", score=tokens_out_eq_35)
        else:
            raise Exception(f"Don't know how to calculate cost type {self.cost_type}")



def make_router():
    return ChatOpenAI(
        openai_api_base="http://127.0.0.1:5000/v1",
        temperature=0.
    )


eval_config = RunEvalConfig(
    input_key="messages",
    reference_key="output",
    evaluators=["qa"],
    custom_evaluators = [CostEvaluator(cost_type="total"),
                         CostEvaluator(cost_type="in"),
                         CostEvaluator(cost_type="out")],
)
run_on_dataset(
    client=client,
    dataset_name=DATASET_NAME,
    llm_or_chain_factory=make_router,
    evaluation=eval_config,
    verbose=True,
)
