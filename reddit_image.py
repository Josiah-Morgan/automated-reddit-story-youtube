import textwrap
from PIL import Image, ImageFont, ImageDraw
from resources.config import image_folder

# add a light mode?
DARK_BACKGROUND_COLOR = "rgb(11,20,22)" # "#0b1416"

USERNAME_FONT = ImageFont.truetype("resources/verdana-bold.ttf", 56) # 56
TITLE_FONT = ImageFont.truetype("resources/impact.ttf", 53)

def generate_title(
    title_text: str,
    file_path: str,
    user_name_text: str = "Wonders of the Planet"
):

    wrapped_text = textwrap.fill(title_text, width=35)
    title_chucks = wrapped_text.split("\n")
    
    height = (60 * len(title_chucks)) + 200 

    image = Image.new("RGB", (900, height), DARK_BACKGROUND_COLOR) # width, height
    draw = ImageDraw.Draw(image)


    # Add Text
    text_y = (1 * len(title_chucks)) + 175 
    draw.multiline_text((30, text_y), wrapped_text, font=TITLE_FONT)


    # Set Avatar
    avatar_image = Image.open("resources/earth_circle.png")
    avatar_size = (160, 160)
    avatar = avatar_image.resize(avatar_size)
    image.paste(avatar, (10, 10), avatar)
    
    
    # Set Username
    draw.text((180, 55), user_name_text, font=USERNAME_FONT)
    
    image_path = f"{image_folder}/{file_path}.png"
    image.save(image_path)
    return image_path
