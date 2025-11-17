import base64
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

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
    # response.output is a list of output items from the Responses API
    for item in response.output:
        # ImageGenerationCall objects have .result with base64 data
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

    Note: the image_generation tool config does NOT support `n`,
    so we ask for `n` images via the prompt instead.
    """
    # Build prompt with style + requested count
    lines = [body.prompt]
    if body.style:
        lines.append(f"Style: {body.style}")
    if body.n > 1:
        lines.append(f"Generate {body.n} different images.")
    full_prompt = "\n\n".join(lines)

    # Call Responses API + image_generation tool
    response = client.responses.create(
        model="gpt-4.1-mini",   # you can switch to gpt-4.1 / gpt-5.1 if enabled
        input=full_prompt,
        tools=[
            {
                "type": "image_generation",
                # Configuration for the image_generation tool
                "size": body.size,
                "quality": body.quality,
                # IMPORTANT: no "n" here — it's not supported on the tool config
            }
        ],
    )

    images = extract_image_b64_list(response)
    return {"images": images}


@app.post("/api/edit-image", response_model=GenerateResponse)
async def edit_image(
    file: UploadFile = File(...),
    instruction: str = Form(...),
    size: str = Form("1024x1024"),
    quality: str = Form("high"),
):
    """
    Edit an existing image:
    - Upload an image
    - Provide a textual instruction (e.g., "add fireworks", "change background to beach")
    We send both the image and instruction as multimodal input into the Responses API
    and let the image_generation tool produce a modified image.
    """
    # Read file bytes and build a data URL
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = file.content_type or "image/png"
    data_url = f"data:{mime_type};base64,{image_b64}"

    # Structured multimodal input: text + image
    input_blocks = [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": instruction},
                {"type": "input_image", "image_url": data_url},
            ],
        }
    ]

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=input_blocks,
        tools=[
            {
                "type": "image_generation",
                "size": size,
                "quality": quality,
                # For advanced use you can extend here with mask/background etc.
            }
        ],
    )

    images = extract_image_b64_list(response)
    return {"images": images}
