from _decimal import Decimal

from langchain.adapters.openai import convert_dict_to_message
from langchain.schema import ChatResult, ChatGeneration
from langsmith import Client
from langchain.smith import RunEvalConfig, run_on_dataset
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

from typing import Optional, Mapping, Any

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
        price = llm_output.get("price")
        if price:
            return EvaluationResult(
                key="Price e6", score=int(Decimal(price) * Decimal(10**6))
            )
        else:
            raise Exception(f"Don't know how to calculate cost type {self.cost_type}")


class CustomChatOpenAI(ChatOpenAI):
    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        generations = []
        for res in response["choices"]:
            message = convert_dict_to_message(res["message"])
            gen = ChatGeneration(
                message=message,
                generation_info=dict(finish_reason=res.get("finish_reason")),
            )
            generations.append(gen)
        token_usage = response.get("usage", {})
        llm_output = {
            "token_usage": token_usage,
            "model_name": self.model_name,
            "price": response.get("price"),
            "usage_debug": response.get("usage_debug"),
        }
        return ChatResult(generations=generations, llm_output=llm_output)


def make_router():
    return CustomChatOpenAI(openai_api_base="http://127.0.0.1:5000/v1", temperature=0.0)


eval_config = RunEvalConfig(
    input_key="messages",
    reference_key="output",
    evaluators=["qa"],
    custom_evaluators=[
        CostEvaluator(cost_type="total"),
        CostEvaluator(cost_type="in"),
        CostEvaluator(cost_type="out"),
    ],
)
run_on_dataset(
    client=client,
    dataset_name=DATASET_NAME,
    llm_or_chain_factory=make_router,
    evaluation=eval_config,
    verbose=True,
)
