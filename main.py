from agent import Agente, OllamaClient
import os

user = os.getlogin()

llm = OllamaClient()
agent = Agente(llm)

while True:
    msg = str(input(f"{user}@agent❯ "))
    if msg in ["exit", "quit"]:
        break

    print("Assistente❯ " + agent.chat(msg))
