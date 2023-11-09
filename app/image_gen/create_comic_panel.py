from PIL import Image, ImageDraw, ImageFont

from app.image_gen.utils import wrap_text

def create_comic_panel(images, text_overlays):
    # Load a font
    font_path = "./Next Sunday.ttf"  # Update this to the path of your .ttf font file
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)

    # Define the size of the gap in pixels
    gap_size = 10  # for example, a 10-pixel gap

    # Assuming all images are the same size, get dimensions for the first image
    width, height = images[0].size

    image_positions = [
        (0, 0),
        (width + gap_size, 0),
        (0, height + gap_size),
        (width + gap_size, height + gap_size)
    ]

    # Create a new image with a white background, adding the gap size
    combined_image = Image.new('RGB', 
                            (width * 2 + gap_size, height * 2 + gap_size), 
                            color='white')

    # Paste images into the combined image with the specified gap
    # combined_image.paste(images[0], (0, 0))
    # combined_image.paste(images[1], (width + gap_size, 0))
    # combined_image.paste(images[2], (0, height + gap_size))
    # combined_image.paste(images[3], (width + gap_size, height + gap_size))

    # Initialize ImageDraw object
    draw = ImageDraw.Draw(combined_image)

    # Paste images and add text
    for i, image in enumerate(images):
        pos = image_positions[i]
        combined_image.paste(image, pos)
        # Update text position based on your preference, e.g., to draw text in the middle of each image:
        text_position = (pos[0] + 10, pos[1] + 10)
        # Optionally, calculate text size and adjust text_position here to center the text
        # text_width, text_height = draw.textsize(text_overlays[i], font=font)
        # text_position = (text_position[0] - text_width // 2, text_position[1] - text_height // 2)
        cleaned_and_wrapped_text = wrap_text(text_overlays[i], width=50)
        draw.text(
            text_position,
            cleaned_and_wrapped_text,
            fill="black",
            font=font
        )

    # Save the combined image
    # combined_image.save('combined_image_with_gap.jpg')
    # combined_image.show()
    return combined_image