
def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message


client = OpenAI(# 定义API的URL
    api_key="< DEEP_SEEK API KEY >",
    base_url="https://api.deepseek.com",
)

messages = { "default":[] }

def ask(msg:str="你好", messages:list=messages["default"]):
    messages.append({"role": "user", "content": f"{msg}"})
    #print(f"User: {messages[-1]}")
    messages.append(send_messages(messages))
    while messages[-1].tool_calls:
        for tool in messages[-1].tool_calls:
            messages.append({"role": "tool", "tool_call_id": tool.id, "content": getFxResponse(tool.function.name, tool.function.arguments)})
        messages.append(send_messages(messages))
    print(f"Ass: {messages[-1].content}")


if __name__ == "__main__":
    while True:
        msg = input("User:\t")
        if msg == "exit":
            break
        ask(msg)
