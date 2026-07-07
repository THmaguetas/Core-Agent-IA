# 🤖 Core Agent IA

---
## 📖 Sobre
Este projeto implementa um agente de IA local que conecta modelos executados pelo `Ollama` a ferramentas desenvolvidas em Python. O agente interpreta pedidos do usuário, que decide quando utilizar ferramentas, executa as funções de forma segura em diretórios autorizados no conf.json e devolve os resultados ao modelo para que ele produza a resposta final.

O arquivo "agent.py" é o orquestador de todo o funcionamento do projeto, logo, ele pode ser adaptado para qualquer tipo de interface sem problemas, sem nenhuma edição no código (incluindo bots do Discord). O arquivo "main.py" foi criado apenas para que o agente seja acessível facilmente.

- O modelo de IA é escolhido pelo usuário, e informado no conf.json

---
## 🚀 Como executar
- Tenha o `Ollama` e um modelo de IA de sua escolha previamente instalado
```bash
git clone https://github.com/THmaguetas/Core-Agent-IA.git
cd Core-Agent-IA
python -m venv .venv
pip install -r requirements.txt
python main.py
```

---
# 📌 Status do projeto
🚧 Finalizado.
