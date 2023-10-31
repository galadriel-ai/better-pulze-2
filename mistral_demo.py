import openai

openai.api_base = "http://10.138.0.4:8000/v1"  # use the IP or hostname of your instance
openai.api_key = "none"  # vLLM server is not authenticated

# mistralai/Mistral-7B-v0.1
# mistralai/Mistral-7B-Instruct-v0.1
completion = openai.Completion.create(
    model="mistralai/Mistral-7B-v0.1",
    prompt="The mistral is",
    temperature=0.7,
    max_tokens=200, stop=".")

print(completion.to_dict_recursive())
