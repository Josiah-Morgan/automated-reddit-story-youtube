import textwrap
from PIL import Image, ImageFont, ImageDraw
from moviepy.editor import ImageClip
from resources.config import image_folder

# This is made just for this project
# I have plans to make this more customizable and public (will I ever do it? not likely)


# add a light mode?
DARK_BACKGROUND_COLOR = "rgb(11,20,22)" # "#0b1416"

USERNAME_FONT = ImageFont.truetype("resources/verdana-bold.ttf", 56) # 56
TEXT_FONT = ImageFont.truetype("resources/verdana.ttf", 14) # 14
TITLE_FONT = ImageFont.truetype("resources/impact.ttf", 53)

def generate_comment(
    comment_text: str,
    file_path: str
):
    # Formats text in chunks and determines height of image
    # textwrap.fill trys to keep sentences intact, so the width parameter is just the max a line could be
    # it won't do something like this: 
    # > I went t
    # > o pet the dog    
    wrapped_text = textwrap.fill(comment_text, width=25)
    title_chucks = wrapped_text.split("\n")

    height = (22 * len(title_chucks)) # 22
    width = int(max(TEXT_FONT.getlength(line) for line in title_chucks)) + 80 # padding 20
    
    image = Image.new("RGB", (900, 480), (DARK_BACKGROUND_COLOR)) # width, height
    draw = ImageDraw.Draw(image)

    # Add Text
    text_y = (2 * len(title_chucks)) # 2
    draw.multiline_text((20, text_y), wrapped_text, font=TEXT_FONT)


    image.save(f"{image_folder}/{file_path}.png")
    
    return f"{image_folder}/{file_path}.png"



# find out how to use earth pfp for avata
def generate_title(
    title_text: str,
    file_path: str,
    user_name_text: str = "Wonders of the World"
):

    wrapped_text = textwrap.fill(title_text, width=35)
    title_chucks = wrapped_text.split("\n")
    
    height = (60 * len(title_chucks)) + 200 # 22
    # width = int(max(TEXT_FONT.getlength(line) for line in title_chucks)) - 5 # padding 20

    image = Image.new("RGB", (900, height), DARK_BACKGROUND_COLOR) # width, height
    draw = ImageDraw.Draw(image)


    # Add Text
    text_y = (1 * len(title_chucks)) + 175 # 2
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

#generate_title("The USA has dropped to 59th in life expectancy. Lower than places like Brazil, Sri Lanka and Algeria to name a few. What is going on here?", "zzyz")

#generate_comment("My girlfriend slept with my dog's cousin. What do I do?", 'balls')
