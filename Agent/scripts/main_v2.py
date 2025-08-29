from groq import Groq
# import the functions from other modules.
from actions import generate_character_name, determine_character_trait, analyze_sentiment, fetch_current_weather, solve_equation
from prompts_v2 import system_prompt
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

user_query = str(input("User: "))

# define the role system and user. In sytem we pass the system_prompt
# which we have imported from prompts.py file. this will provide instruction to llm
# what to do how to do.
messages = [
    {"role": "system", "content": (
        system_prompt
    )},
    {"role": "user", "content": user_query},
]

last_calls = []  # keep last few (name, args) to detect loops

# while True:
#     # get model output
#     response, _ = chat(messages, model)  
        
#     try:
#         obj = json.loads(response)
#     except json.JSONDecodeError:
#         raise ValueError("Model did not return valid JSON")

#     if obj["type"] == "thought":
#         print(f"[THOUGHT] {obj['content']}")
        
#     elif obj["type"] == "call":
#         fn = obj["function_name"]
#         parms = obj["function_parms"]
#         print(f"[CALL] {fn}({parms})")

#         # execute your tool
#         result = available_actions[fn](**parms)

#         # add observation to conversation
#         obs = {"type": "observation", "content": result}
#         messages.append({"role": "assistant", "content": json.dumps(obj)})
#         messages.append({"role": "user", "content": json.dumps(obs)})

#     elif obj["type"] == "final":
#         print(f"[FINAL ANSWER] {obj['answer']}")
#         break
#     else:
#         raise ValueError(f"Unknown type {obj['type']}")
        
thought_counter = 0
for step in range(10):
    response, _ = chat(messages, model)
    
    try:
        obj = json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("Model did not return valid JSON")
    
    if obj["type"] == "thought":
        print(f"[THOUGHT] {obj['content']}\n")
        thought_counter += 1
        if thought_counter > 2:  # guardrail
            messages.append({"role": "system", "content": "You have reasoned enough. Now you MUST either call a tool or provide a final answer."})
            continue
    else:
        thought_counter = 0  # reset

    messages.append({"role":"user", "content":json.dumps(obj)})

    # Tool call handling
    if obj["type"] == "call":
        fn = obj["function_name"]
        parms = obj["function_parms"]
        print(f"[CALL] {fn}({parms})\n")

        # execute your tool
        result = available_actions[fn](**parms)

        # add observation to conversation
        obs = {"type": "observation", "content": result}
        print(f"[OBSERVATION]{obs}\n")
        messages.append({"role": "assistant", "content": json.dumps(obj)})
        messages.append({"role": "user", "content": json.dumps(obs)})
        
    # End loop
    if obj["type"] == "final":
        print(f"[FINAL ANSWER] {obj['answer']}\n")
        break
