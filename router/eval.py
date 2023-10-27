from langsmith import Client
from langchain.smith import RunEvalConfig, run_on_dataset
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

client = Client()

DATASET_NAME = "Chat manager test"


def make_router():
    # TODO replace this with something that actually routes and
    # implements ChatOpenAI compatible interface
    return ChatOpenAI(temperature=0.)

eval_config = RunEvalConfig(
    input_key="messages",
    reference_key="output",
    evaluators=["qa"]
)
run_on_dataset(
    client=client,
    dataset_name=DATASET_NAME,
    llm_or_chain_factory=make_router,
    evaluation=eval_config,
    verbose=True,
)

