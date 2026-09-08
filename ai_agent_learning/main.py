import os
from dotenv import load_dotenv
from openai import OpenAI
import tools
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

available_tools = {
    "get_server_status": tools.get_server_status,
    "get_disk_space": tools.get_disk_space,
    "get_ssh_port_status": tools.get_ssh_port_status
}

tools = [
    {
        "type": "function",
        "name": "get_server_status",
        "description": "Check whether the server is running.",
        "parameters": {
        "type": "object",
        "properties": {
            "server": {
                "type": "string",
                "description": "The IP address or hostname of the server to check."
            }
        },
        "required": ["server"]
        }
    },
    {
        
        "type": "function",
        "name": "get_disk_space",
        "description": "Check how much free disk space the server has.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_ssh_port_status",
        "description": "Check whether SSH port 22 is open on the server.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

conversation = [
    {
        "role": "user",
        "content": input("User Input: ")
    }
]

while True:
    response = client.responses.create(
        model="gpt-5.6-sol",
        input=conversation,
        tools=tools
    )
    
    if response.output_text:
        print("AI:", response.output_text)

        user_input = input("User: ")

        conversation.append({
            "role": "assistant",
            "content": response.output_text
        })

        conversation.append({
            "role": "user",
            "content": user_input
        })

        continue

    for item in response.output:

        if item.type == "function_call":

            tool = available_tools[item.name]
            arguments = json.loads(item.arguments)
            result = tool(**arguments)
            print("Tool result", result)

            tool_result = {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result
            }

            response = client.responses.create(
                model="gpt-5.6-sol",
                previous_response_id=response.id,
                input=[tool_result],
                tools=tools
            )
            print("AI:", response.output_text)
            break