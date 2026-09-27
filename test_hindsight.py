from hindsight.memory import client, BANK_ID

print("Connecting to Hindsight...")

result = client.recall(
    bank_id=BANK_ID,
    query="payment failure troubleshooting",
)

print("Hindsight connection successful!")
print(f"Memory bank: {BANK_ID}")
print(f"Memories found: {len(result.results)}")