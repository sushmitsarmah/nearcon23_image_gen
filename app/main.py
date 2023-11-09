from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.image_gen.gen_image import ImageGen
from app.image_gen.story_gen import AIStory

from app.config import PromptRequest

app = FastAPI()
img_gen = ImageGen()
ai_story = AIStory()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI comic generator API"}

@app.get("/image")
async def image_gen(prompt: str):
    ipfs = img_gen.gen_image(prompt=prompt, only_img=True)
    return JSONResponse({ "ipfs": ipfs })

@app.post("/gen-stories")
async def image_gen(body: PromptRequest):
    stories = ai_story.get_stories(prompt=body.prompt)
    return JSONResponse({ "stories": stories })

@app.post("/gen-comic")
async def image_gen(body: PromptRequest):
    panels = ai_story.create_comic_panels(story=body.prompt)
    ipfs = img_gen.gen_comic(panels=panels)
    return JSONResponse({ "ipfs": ipfs })