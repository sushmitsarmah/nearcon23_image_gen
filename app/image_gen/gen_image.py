import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from lighthouseweb3 import Lighthouse
from random import randint, randrange
from dotenv import load_dotenv

from app.image_gen.create_comic_panel import create_comic_panel

load_dotenv()

STABILITY_SDK_KEY = os.getenv("STABILITY_SDK_KEY", "")
LIGHTHOUSE_API_TOKEN = os.getenv("LIGHTHOUSE_API_TOKEN", "")

lh = Lighthouse(token=LIGHTHOUSE_API_TOKEN)
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = STABILITY_SDK_KEY

SEED = 4253978046
STEPS = 50
CFG_SCALE = 8.0
WIDTH = 1024
HEIGHT = 1024
SAMPLES = 1
SAMPLER = generation.SAMPLER_K_DPMPP_2M
OUTPUT_IMG = "gen_image.png"

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class ImageGen:

    def __init__(self, engine="stable-diffusion-xl-1024-v1-0"):
        # Set up our connection to the API.
        self.stability_api = client.StabilityInference(
            key=os.environ['STABILITY_KEY'], # API Key reference.
            verbose=True, # Print debug messages.
            engine=engine, # Set the engine to use for generation.
            # Check out the following link for a list of available engines: https://platform.stability.ai/docs/features/api-parameters#engine
        )

    def gen_image(self, prompt, only_img=False, **kwargs):
        seed = random_with_N_digits(9)
        steps = (kwargs and kwargs["steps"]) or STEPS
        cfg_scale = (kwargs and kwargs["cfg_scale"]) or CFG_SCALE
        width = (kwargs and kwargs["width"]) or WIDTH
        height = (kwargs and kwargs["height"]) or HEIGHT
        samples = (kwargs and kwargs["samples"]) or SAMPLES

        print("generating image ...")
        # Set up our initial generation parameters.
        answers = self.stability_api.generate(
            prompt=prompt,
            seed=seed, # If a seed is provided, the resulting generated image will be deterministic.
                            # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
                            # Note: This isn't quite the case for Clip Guided generations, which we'll tackle in a future example notebook.
            steps=steps, # Amount of inference steps performed on image generation. Defaults to 30. 
            cfg_scale=cfg_scale, # Influences how strongly your generation is guided to match your prompt.
                        # Setting this value higher increases the strength in which it tries to match your prompt.
                        # Defaults to 7.0 if not specified.
            width=width, # Generation width, defaults to 512 if not included.
            height=height, # Generation height, defaults to 512 if not included.
            samples=samples, # Number of images to generate, defaults to 1 if not included.
            sampler=SAMPLER # Choose which sampler we want to denoise our generation with.
                                                        # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                        # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        )

        # Set up our warning to print to the console if the adult content classifier is tripped.
        # If adult content classifier is not tripped, save generated images.
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    # img.save(OUTPUT_IMG)
                    print("image generated !")
                    if only_img:
                        print("uploading image to IPFS ...")
                        tag = str(artifact.seed)
                        ipfs = self.uploadImageToIPFS(tag=tag)
                        img_url = "https://gateway.lighthouse.storage/ipfs/" + ipfs["data"]["Hash"]
                        return img_url
                    else:
                        return img

        return None


    def gen_comic(self, panels: [str]):
        print(panels)
        if panels and len(panels) > 0:
            images = []
            print('looping through panels')
            for prompt in panels:
                print(prompt)
                img = self.gen_image(prompt)
                images.append(img)
                print("image appended")

            comic_img = create_comic_panel(images, panels)
            comic_img.save(OUTPUT_IMG)
            tag = str(random_with_N_digits(9))
            ipfs = self.uploadImageToIPFS(tag=tag)
            img_url = "https://gateway.lighthouse.storage/ipfs/" + ipfs["data"]["Hash"]
            return img_url
        else:
            return ""


    def uploadImageToIPFS(self, tag):
        # File upload with tags
        tagged_source_file_path = "./" + OUTPUT_IMG

        if tag:
            uploaded = lh.upload(source=tagged_source_file_path, tag=tag)
        else:
            uploaded = lh.upload(source=tagged_source_file_path)
        print("File Upload with Tag Successful!")
        return uploaded

if __name__ == "main":
    # prompt = "best quality, ultra high res, (photorealistic:1.4), whimsical creature carnival, [dancing pixies:giant fire-breathing salamanders:0.5] and [glittering unicorns:playful griffins:0.6] [amidst a kaleidoscope of stars::0.4] [in a realm of enchantment:in a land of fantastical wonders:0.7], highly detailed, cinematic lighting"
    prompt = "best quality, ultra high res, photorealistic, [big strawberry:skull:20] hanging from a tree"
    img_gen = ImageGen()
    ipfs = img_gen.genImage(prompt=prompt)
    # print("IPFS link = ", ipfs_hash)
    print(ipfs)