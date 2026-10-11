"""Quick local integration test for DataPilot + Ollama."""
from pathlib import Path
import pandas as pd
from agent import ask_agent

df = pd.read_csv(Path(__file__).parent / "data" / "sample_sales.csv")
question = "Which region has the highest total revenue? Use the data to calculate it."
answer, trace = ask_agent(df, question)

print("\nQUESTION:", question)
print("\nTOOL TRACE:")
for item in trace:
    print(f"- {item['tool']}({item['arguments']})")
print("\nANSWER:", answer)
