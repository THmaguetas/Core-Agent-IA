import ollama, json, storage.tools, inspect
from pathlib import Path
tools = storage.tools


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


# carrega as funções reais das ferramentas para o modelo usar
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



# Agente <intermediário entre o modelo e as ferramentas>
class Agente:
    def __init__(self, llm):
        self.llm = llm
        self.tools_schema = build_tool_schema(tools)
        self.tools_exec = load_tools(tools)
        self.history = load_history()
        self.locals = config["locais"]
        self.current_local = None


    def chat(self, message: str):
        self.history.append({
            "role": "user",
            "content": message
        })

        while True:
            response = self.llm.chat(
                messages=[
                    {
                        "role": "system",
                        "content": self._default_prompt()
                    },
                    *self.history[-100:]    # Limita o contexto em 100 requests
                ],
                tools=self.tools_schema
            )

            message_obj = response["message"].model_dump(exclude_none=True)

            if message_obj.get("tool_calls"):
                self.history.append(message_obj)

                for tool_call in message_obj["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    raw_args = tool_call["function"]["arguments"]
                    exec_args = raw_args.copy()

                    result = self._execute_tool(tool_name, exec_args)

                    self.history.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(
                            {
                                "tool": tool_name,
                                "arguments": raw_args,
                                "result": result
                            },
                            ensure_ascii=False
                        )
                    })
                continue

            assistant_message = message_obj.get("content") or ""

            if not assistant_message.strip():
                prompt_provocacao = "A ferramenta foi executada com sucesso. Por favor, apresente o resultado final formatado ao usuário."

                if self.history and self.history[-1].get("content") == prompt_provocacao:
                    assistant_message = "Tarefa concluída com sucesso!"
                else:
                    self.history.append({
                        "role": "user",
                        "content": prompt_provocacao
                    })
                    continue

            self.history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            save_history(self.history)
            return assistant_message


    def _default_prompt(self):
        guide = Path("storage/guide.md")
        return guide.read_text(encoding="utf-8")


    def _convert_local(self, local: str):
        if local not in self.locals:
            return None
        return self.locals[local]


    def _execute_tool(self, tool_name: str, args: dict):
        if tool_name not in self.tools_exec:
            return f"Tool '{tool_name}' não existe"

        if "local" in args:
            local_simbolico = args["local"]

            if local_simbolico in self.locals:
                caminho_absoluto = self._convert_local(local_simbolico)
                self.current_local = local_simbolico
                args["local"] = caminho_absoluto
            
            elif not self.current_local:
                return f"Local '{local_simbolico}' inexistente ou não configurado."
            
            else:
                args["local"] = self._convert_local(self.current_local)
                
        return self.tools_exec[tool_name](**args)

