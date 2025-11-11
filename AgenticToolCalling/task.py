import time

from openai import OpenAI, models

client = OpenAI()

response = client.responses.create(
    input="Hello World!",
    model="o3",
    background=True,
)

print(response)
print("Job Created:", response.id)

# Poll for completion
while True:
    job = client.responses.retrieve(response.id)
    print("Status:", job.status)

    if job.status in ["completed", "failed"]:
        break

    time.sleep(1)
print("FINAL OUTPUT:")
print(job.output_text)

