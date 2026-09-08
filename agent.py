import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    ping_host,
    check_ssh_port,
    check_ssh_service,
)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_STEPS = 5


tools = [
    {
        "type": "function",
        "name": "ping_host",
        "description": "Check whether a host responds to ping.",
        "parameters": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Hostname or IP address to ping."
                }
            },
            "required": ["host"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "check_ssh_port",
        "description": "Check whether TCP port 22 is open on a host.",
        "parameters": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Hostname or IP address to check."
                }
            },
            "required": ["host"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "check_ssh_service",
        "description": "Check whether the local SSH service is running.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
]


def execute_tool(name, arguments):

    if name == "ping_host":
        return ping_host(arguments["host"])

    if name == "check_ssh_port":
        return check_ssh_port(arguments["host"])

    if name == "check_ssh_service":
        return check_ssh_service()

    return f"Unknown tool: {name}"


def main():

    problem = input("Describe the IT problem: ")

    conversation = [
        {
            "role": "user",
            "content": f"""
The user has reported this IT problem:

{problem}

Investigate the problem using the available tools.

Your goal is to identify the most likely cause.

If you need information that cannot be obtained using a tool,
ask the user for it.

If you need to ask the user a question, respond with exactly:

ASK_USER: <your question>

When you have enough information to identify the likely cause,
stop investigating and provide a short explanation.
"""
        }
    ]

    for step in range(1, MAX_STEPS + 1):

        print(f"\n--- Agent step {step} ---")

        response = client.responses.create(
            model="gpt-5.6",
            input=conversation,
            tools=tools,
            reasoning={"effort": "low"}
        )

        conversation += response.output

        # Check if the AI wants to ask the user something
        if response.output_text.startswith("ASK_USER:"):

            question = response.output_text.replace(
                "ASK_USER:",
                "",
                1
            ).strip()

            print(f"\nAgent asks:")
            print(question)

            answer = input("\nYour answer: ")

            conversation.append({
                "role": "user",
                "content": f"""
The user answered:

{answer}

Continue investigating the original problem.
"""
            })

            continue

        # Check for tool calls
        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if tool_calls:

            for tool_call in tool_calls:

                print(f"Action: {tool_call.name}")

                arguments = json.loads(tool_call.arguments)

                print(f"Arguments: {arguments}")

                result = execute_tool(
                    tool_call.name,
                    arguments
                )

                print(f"Result: {result}")

                conversation.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result
                })

            continue

        # No tool call and no question = final answer
        print("\nAgent result:")
        print(response.output_text)

        break


if __name__ == "__main__":
    main()