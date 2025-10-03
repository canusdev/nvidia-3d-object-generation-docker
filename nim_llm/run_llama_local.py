#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""
Local LLM Service using Transformers
This replaces the NIM container with a local implementation.
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
PORT = 19002
HOST = "0.0.0.0"

# Global model and tokenizer
model = None
tokenizer = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]

app = FastAPI(title="Local LLM Service", version="1.0.0")

def load_model():
    """Load the LLM model and tokenizer."""
    global model, tokenizer
    
    try:
        logger.info(f"Loading model: {MODEL_NAME}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            use_auth_token=os.getenv("HF_TOKEN")
        )
        
        # Load model with appropriate precision
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
            use_auth_token=os.getenv("HF_TOKEN")
        )
        
        if torch.cuda.is_available():
            logger.info(f"Model loaded on GPU: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("Model loaded on CPU")
            
        logger.info("Model loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.info("Falling back to smaller model...")
        
        try:
            # Fallback to a smaller model if main model fails
            fallback_model = "meta-llama/Llama-2-7b-chat-hf"
            logger.info(f"Loading fallback model: {fallback_model}")
            
            tokenizer = AutoTokenizer.from_pretrained(fallback_model, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                fallback_model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            logger.info("Fallback model loaded successfully!")
            return True
            
        except Exception as e2:
            logger.error(f"Failed to load fallback model: {e2}")
            return False

@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    logger.info("Starting LLM service...")
    success = load_model()
    if not success:
        logger.error("Failed to load any model. Service may not function correctly.")

@app.get("/v1/health/ready")
async def health_check():
    """Health check endpoint."""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}

@app.get("/v1/health/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint."""
    try:
        if model is None or tokenizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Format messages for the model
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Apply chat template
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response_text = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        # Format response
        import time
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        }
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/models")
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [{
            "id": MODEL_NAME,
            "object": "model",
            "created": 1234567890,
            "owned_by": "local"
        }]
    }

def main():
    """Main entry point."""
    logger.info(f"Starting LLM service on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()
