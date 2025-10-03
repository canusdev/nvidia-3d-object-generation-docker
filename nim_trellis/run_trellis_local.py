#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""
Local TRELLIS 3D Generation Service
This replaces the NIM container with a local implementation.
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import torch
import base64
from io import BytesIO
from PIL import Image
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = 8000
HOST = "0.0.0.0"

# Global pipeline
pipeline = None

class Artifact(BaseModel):
    base64: str
    finishReason: str

class InferRequest(BaseModel):
    image: str

class InferResponse(BaseModel):
    artifacts: List[Artifact]

app = FastAPI(title="Local TRELLIS 3D Service", version="1.0.0")

def load_pipeline():
    """Load the TRELLIS pipeline."""
    global pipeline
    
    try:
        logger.info("Loading TRELLIS pipeline...")
        
        # Import TRELLIS components
        try:
            from trellis.pipelines import TrellisImageTo3DPipeline
            from trellis.utils import render_utils, postprocessing_utils
        except ImportError:
            logger.error("TRELLIS package not found. Please install it first.")
            logger.info("For now, using a mock pipeline for testing...")
            return False
        
        # Load the pipeline
        pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
        
        if torch.cuda.is_available():
            pipeline = pipeline.to("cuda")
            logger.info(f"Pipeline loaded on GPU: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("Pipeline loaded on CPU (will be slow)")
        
        logger.info("TRELLIS pipeline loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load TRELLIS pipeline: {e}")
        logger.info("Please ensure TRELLIS is properly installed")
        return False

@app.on_event("startup")
async def startup_event():
    """Load pipeline on startup."""
    logger.info("Starting TRELLIS 3D generation service...")
    success = load_pipeline()
    if not success:
        logger.warning("Failed to load TRELLIS pipeline. Service may not function correctly.")

@app.get("/v1/health/ready")
async def health_check():
    """Health check endpoint."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not loaded")
    return {"status": "ready"}

@app.get("/v1/health/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive"}

@app.post("/v1/infer")
async def generate_3d(request: InferRequest):
    """Generate 3D model from image."""
    try:
        if pipeline is None:
            raise HTTPException(status_code=503, detail="Pipeline not loaded")
        
        logger.info("Received 3D generation request")
        
        # Decode base64 image
        if request.image.startswith("data:"):
            # Remove data URI prefix
            image_data = request.image.split(",")[1]
        else:
            image_data = request.image
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        
        logger.info(f"Image decoded: {image.size}")
        
        # Generate 3D model
        logger.info("Generating 3D model...")
        
        with torch.no_grad():
            # Run the pipeline
            outputs = pipeline(
                image,
                seed=42,
                sparse_structure_sampler_params={
                    "steps": 12,
                    "cfg_strength": 7.5,
                },
                slat_sampler_params={
                    "steps": 12,
                    "cfg_strength": 3.0,
                },
            )
        
        # Export to GLB
        logger.info("Exporting to GLB format...")
        glb_bytes = BytesIO()
        outputs.export_glb(glb_bytes)
        glb_bytes.seek(0)
        
        # Encode GLB to base64
        glb_base64 = base64.b64encode(glb_bytes.read()).decode('utf-8')
        
        logger.info("3D model generated successfully!")
        
        return {
            "artifacts": [{
                "base64": glb_base64,
                "finishReason": "SUCCESS"
            }]
        }
        
    except Exception as e:
        logger.error(f"Error in 3D generation: {e}", exc_info=True)
        
        # Check if it's a content filtering issue
        if "inappropriate" in str(e).lower() or "nsfw" in str(e).lower():
            return {
                "artifacts": [{
                    "base64": "",
                    "finishReason": "CONTENT_FILTERED"
                }]
            }
        
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main entry point."""
    logger.info(f"Starting TRELLIS service on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()
