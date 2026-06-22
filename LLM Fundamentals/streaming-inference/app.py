# server.py
import asyncio
from fastapi import FastAPI, WebSocket
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
import threading

app = FastAPI()

MODEL_NAME = "gpt2"  # replace with any causal LM you have access to

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()

def run_generation(prompt: str, streamer: TextIteratorStreamer):
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            streamer=streamer,
        )

@app.websocket("/llm-stream")
async def llm_stream(ws: WebSocket):
    await ws.accept()

    prompt = await ws.receive_text()

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True,
    )

    # Run generation in a background thread
    thread = threading.Thread(
        target=run_generation,
        args=(prompt, streamer),
        daemon=True,
    )
    thread.start()

    # Stream tokens to client
    for token in streamer:
        await ws.send_text(token)

    await ws.send_text("[END]")
    await ws.close()
