import base64
from typing import List, Optional

import streamlit as st
from openai import OpenAI

# -----------------------------
# OpenAI client (uses OPENAI_API_KEY from env)
# -----------------------------
client = OpenAI()
# -----------------------------
# Helpers
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


def generate_images(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "high",
    n: int = 1,
    style: Optional[str] = None,
) -> List[bytes]:
    """
    Call OpenAI Responses API + image_generation tool and return a list
    of image bytes ready for st.image.
    """
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    lines = [prompt]
    if style:
        lines.append(f"Style: {style}")
    if n > 1:
        lines.append(f"Generate {n} different images.")
    full_prompt = "\n\n".join(lines)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=full_prompt,
        tools=[
            {
                "type": "image_generation",
                "size": size,
                "quality": quality,
            }
        ],
        timeout=60,
    )

    b64_list = extract_image_b64_list(response)
    images: List[bytes] = []
    for b64 in b64_list:
        images.append(base64.b64decode(b64))
    return images


def edit_image(
    image_bytes: bytes,
    instruction: str,
    size: str = "1024x1024",
    quality: str = "high",
) -> List[bytes]:
    """
    Call OpenAI Responses API with multimodal input (text + image)
    and image_generation tool to get edited image bytes.
    """
    if not instruction.strip():
        raise ValueError("Instruction cannot be empty.")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = "image/png"  # reasonable default
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
        timeout=60,
    )

    b64_list = extract_image_b64_list(response)
    images: List[bytes] = []
    for b64 in b64_list:
        images.append(base64.b64decode(b64))
    return images


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Image Studio (Streamlit)", layout="centered")

st.title("Image Studio")
st.write("Generate and edit images using OpenAI Responses API + `image_generation` tool.")

tab_generate, tab_edit = st.tabs(["🎨 Generate Image", "🪄 Edit Existing Image"])

# -------- Generate Tab --------
with tab_generate:
    st.subheader("Generate Image")

    with st.form("generate_form"):
        prompt = st.text_area(
            "Prompt",
            value="A futuristic city at sunset with flying cars...",
            height=100,
        )
        style = st.text_input(
            "Style (optional)",
            placeholder="3D render, anime, watercolor, etc.",
        )
        size = st.selectbox(
            "Size",
            options=[
                "1024x1024",
                "1024x1536",  # tall
                "1536x1024",  # wide
                "auto",
            ],
            index=0,
        )
        quality = st.selectbox(
            "Quality",
            options=["high", "medium", "low", "auto"],
            index=0,
        )
        n = st.selectbox("Number of images", options=[1, 2, 3], index=0)

        submitted = st.form_submit_button("Generate")

    if submitted:
        if not prompt.strip():
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Generating images..."):
                try:
                    images = generate_images(
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        n=n,
                        style=style or None,
                    )
                    st.success(f"Got {len(images)} image(s).")
                    for idx, img_bytes in enumerate(images, start=1):
                        st.image(img_bytes, caption=f"Generated image {idx}")
                except Exception as e:
                    st.error(f"Error while generating image(s): {e}")

# -------- Edit Tab --------
with tab_edit:
    st.subheader("Edit Existing Image")

    with st.form("edit_form"):
        uploaded_file = st.file_uploader(
            "Upload image",
            type=["png", "jpg", "jpeg", "webp"],
        )
        instruction = st.text_area(
            "Instruction (what do you want changed?)",
            placeholder="Add fireworks in the sky, change background to a beach, etc.",
            height=100,
        )
        size_edit = st.selectbox(
            "Size",
            options=[
                "1024x1024",
                "1024x1536",  # tall
                "1536x1024",  # wide
                "auto",
            ],
            index=0,
        )
        quality_edit = st.selectbox(
            "Quality",
            options=["high", "medium", "low", "auto"],
            index=0,
        )

        edit_submitted = st.form_submit_button("Edit Image")

    if edit_submitted:
        if uploaded_file is None:
            st.error("Please upload an image first.")
        elif not instruction.strip():
            st.error("Please provide an instruction.")
        else:
            with st.spinner("Editing image..."):
                try:
                    img_bytes = uploaded_file.getvalue()
                    edited_images = edit_image(
                        image_bytes=img_bytes,
                        instruction=instruction,
                        size=size_edit,
                        quality=quality_edit,
                    )
                    st.success(f"Got {len(edited_images)} edited image(s).")
                    for idx, img_bytes in enumerate(edited_images, start=1):
                        st.image(img_bytes, caption=f"Edited image {idx}")
                except Exception as e:
                    st.error(f"Error while editing image: {e}")
