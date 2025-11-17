import base64
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import logging

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("imagestudio")

# -----------------------------
# OpenAI client (uses OPENAI_API_KEY from env)
# -----------------------------
client = OpenAI()

# -----------------------------
# FastAPI app setup
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # for dev; you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic models
# -----------------------------
class GenerateRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"     # "1024x1024", "1024x1536", "1536x1024", or "auto"
    quality: str = "high"       # "low", "medium", "high", "auto"
    n: int = 1                  # number of images user wants
    style: Optional[str] = None # e.g. "3D render", "anime", etc.


class GenerateResponse(BaseModel):
    images: List[str]           # base64-encoded PNG images


# -----------------------------
# Utility helpers
# -----------------------------
def extract_image_b64_list(response) -> List[str]:
    """
    Extract base64 image strings from Responses API output.
    Image-generation tool calls appear as items with `result` (base64).
    """
    results: List[str] = []
    for item in response.output:
        result = getattr(item, "result", None)
        if result:
            results.append(result)
    return results


# -----------------------------
# Routes
# -----------------------------

@app.get("/")
async def root():
    return {"status": "ok", "message": "ImageStudio backend is running"}


@app.post("/api/generate-image", response_model=GenerateResponse)
async def generate_image(body: GenerateRequest):
    """
    Generate image(s) from a text prompt using the built-in image_generation tool.
    """
    logger.info(f"/api/generate-image called with body={body}")

    # Build prompt with style + requested count
    lines = [body.prompt]
    if body.style:
        lines.append(f"Style: {body.style}")
    if body.n > 1:
        lines.append(f"Generate {body.n} different images.")
    full_prompt = "\n\n".join(lines)

    try:
        logger.info("Calling OpenAI responses.create() ...")
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=full_prompt,
            tools=[
                {
                    "type": "image_generation",
                    "size": body.size,
                    "quality": body.quality,
                    # no "n" here; we ask for multiple images in the prompt text
                }
            ],
            timeout=30,  # avoid hanging forever
        )
        logger.info("OpenAI responses.create() finished successfully")
    except Exception as e:
        logger.exception("Error while calling OpenAI responses.create()")
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    images = extract_image_b64_list(response)
    logger.info(f"/api/generate-image returning {len(images)} images")
    return {"images": images}


@app.post("/api/edit-image", response_model=GenerateResponse)
async def edit_image(
    file: UploadFile = File(...),
    instruction: str = Form(...),
    size: str = Form("1024x1024"),
    quality: str = Form("high"),
):
    """
    Edit an existing image using text + uploaded image as multimodal input.
    """
    logger.info(f"/api/edit-image called with instruction={instruction!r}, size={size}, quality={quality}")

    # Read file bytes and build a data URL
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = file.content_type or "image/png"
    data_url = f"data:{mime_type};base64,{image_b64}"

    input_blocks = [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": instruction},
                {"type": "input_image", "image_url": data_url},
            ],
        }
    ]

    try:
        logger.info("Calling OpenAI responses.create() for edit ...")
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=input_blocks,
            tools=[
                {
                    "type": "image_generation",
                    "size": size,
                    "quality": quality,
                }
            ],
            timeout=30,
        )
        logger.info("OpenAI responses.create() for edit finished successfully")
    except Exception as e:
        logger.exception("Error while calling OpenAI responses.create() for edit")
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    images = extract_image_b64_list(response)
    logger.info(f"/api/edit-image returning {len(images)} images")
    return {"images": images}
