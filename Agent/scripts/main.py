from groq import Groq
# import the functions from other modules.
from actions import generate_character_name, determine_character_trait, analyze_sentiment, fetch_current_weather, solve_equation
from prompts import system_prompt
from json_helpers import extract_json
from memory import memory
from context import context_manager
from dotenv import load_dotenv
load_dotenv("local.env")
import os
import json

model = os.getenv("model")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def chat(messages, model):
    resp = client.chat.completions.create(model=model, messages=messages)
    msg = resp.choices[0].message
    content = msg.content or ""
    finish_reason = resp.choices[0].finish_reason  # usually "stop", "length", etc.
    return content, finish_reason

available_actions = {
    "generate_character_name": generate_character_name,
    "determine_character_trait": determine_character_trait,
    "analyze_sentiment": analyze_sentiment,
    "fetch_current_weather": fetch_current_weather,
    "solve_equation": solve_equation,
}

user_prompt = str(input("User: "))

# define the role system and user. In sytem we pass the system_prompt
# which we have imported from prompts.py file. this will provide instruction to llm
# what to do how to do.
messages = [
    {"role": "system", "content": (
        system_prompt
    )},
    {"role": "user", "content": user_prompt},
]

max_steps = 6
last_calls = []  # keep last few (name, args) to detect loops

for step in range(1, max_steps + 1):
    print(f"Loop: {step}\n----------------------")

    assistant_text, finish_reason = chat(messages, model)
    print(assistant_text)
    messages.append({"role": "assistant", "content": assistant_text})

    data = extract_json(assistant_text)[0]  # should parse into dict
    if not data:
        # Hard fallback: ask the model to restate in JSON once, then bail.
        messages.append({"role": "user", "content": "Your last output was not valid JSON. Follow the schema exactly."})
        continue  # give it one more shot; max_steps still caps us
    
    action = data.get("type")

    if action == "final":
        answer = data.get("answer", "")
        print(answer)
        break

    if action == "call":
        name = data.get("function_name")
        args = data.get("function_parms", {}) or {}

        if name not in available_actions:
            raise Exception(f"Unknown action: {name} {args}")

        # Spin-guard: if the same tool+args repeats too much, stop.
        signature = (name, json.dumps(args, sort_keys=True))
        last_calls.append(signature)
        if last_calls.count(signature) > 2:
            print("Stopping: detected repeated identical tool calls.")
            break

        print(f" -- running {name} {args}")
        try:
            result = available_actions[name](**args)
        except Exception as e:
            result = {"error": str(e)}

        # Feed the result back clearly delimited
        tool_msg = {
            "role": "user",  # if you prefer, use "tool" if your client supports it
            "content": f"TOOL_RESULT[{name}]: {json.dumps(result)}"
        }
        messages.append(tool_msg)
        print(tool_msg["content"],">>>>>>>>>>>")

        # Update memory/context
        memory.update_memory("last_response", result)
        context_manager.update_context("last_action", name)
        
        print("Memory: ",memory.data)

        # Continue loop to let the model observe the result
        continue

    else:
        # Unknown schema -> ask for correction once
        messages.append({"role": "user", "content": "Invalid schema. Use either action:'call' or action:'final'."})
        continue

else:
    # Only runs if loop exhausted without break
    print("Stopping: reached controller max_steps without a final answer.")