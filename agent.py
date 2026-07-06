import ollama, json, tools, inspect
from pathlib import Path


# carrega as configurações do user
def load_conf():
    with open('config/conf.json', 'r', encoding='utf-8') as conf:
        return json.load(conf)


config = load_conf()


# carrega todo o contexto da IA
def load_history():
    try:
        with open('storage/historico.json', 'r', encoding='utf-8') as history:
            return json.load(history)
    except FileNotFoundError:
        return []


def save_history(data):
    with open('storage/historico.json', 'w', encoding='utf-8') as history:
        json.dump(data, history, indent=4, ensure_ascii=False)


# lista as funções presentes no arquivo de tools
def load_tools(module):
    tools_map = {}

    for nome, func in inspect.getmembers(module, inspect.isfunction):
        if not nome.startswith("_"):
            tools_map[nome] = func

    return tools_map


# cria schema/descrição para as ferramentas do modelo
def build_tool_schema(ferramentas):
    schema = []

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }

    for name, func in inspect.getmembers(ferramentas, inspect.isfunction):
        if name.startswith("_"):
            continue

        doc = func.__doc__ or "sem descrição"
        sig = inspect.signature(func)

        properties = {}
        required = []
        for param_name, param in sig.parameters.items():
            param_type = type_map.get(param.annotation, "string")
            properties[param_name] = {
                "type": param_type
            }
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        schema.append({
            "type": "function",
            "function": {
                "name": name,
                "description": doc.strip(),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        })

    return schema


# comunicação com a biblioteca do Ollama
class OllamaClient:
    def __init__(self, model: str = None):
        self.model = model or config.get("modelo", "qwen3:8b")

    def chat(self, messages: list, tools: list | None = None):
        response = ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )
        return response



# Agente --intermediário entre o modelo e as ferramentas--
class Agente:
    def __init__(self, llm):
        self.llm = llm
        self.tools_schema = build_tool_schema(tools)
        self.tools_exec = load_tools(tools)
        self.history = load_history()
        self.base_dirs = config["diretórios"]


    def chat(self, message: str):
        self.history.append({
            "role": "user",
            "content": message
        })

        while True:

            response = self.llm.chat(
                messages=self.history[-20:],
                tools=self.tools_schema
            )

            message = response["message"]

            if message.get("tool_calls"):

                for tool_call in message["tool_calls"]:

                    tool_name = tool_call["function"]["name"]
                    args = tool_call["function"]["arguments"]

                    result = self._execute_tool(tool_name, args)

                    self.history.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": str(result)
                    })

                continue

            assistant_message = message["content"]

            self.history.append({
                "role": "assistant",
                "content": assistant_message
            })

            save_history(self.history)
            return assistant_message


    def _convert_local(self, local: str):
        if local not in self.base_dirs:
            return None
        return self.base_dirs[local]


    def _execute_tool(self, tool_name: str, args: dict):
        if tool_name not in self.tools_exec:
            return f"Tool '{tool_name}' não existe"

        if "local" in args:
            local = self._convert_local(args.pop("local"))

            if local is None:
                return "Local inexistente."

            args["local"] = local

        return self.tools_exec[tool_name](**args)


