from openai import OpenAI
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="",
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",  # or Llama-3.3-70B-Instruct
    messages=[{"role": "user", "content": "Hello!"}],
)

print(response.choices[0].message.content)
