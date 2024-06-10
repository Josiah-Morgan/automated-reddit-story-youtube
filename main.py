import os
import random
import re
import textwrap
import time


from reddit_image import generate_title
from resources.config import (
    amount_of_comments,
    amount_of_post,
    audio_folder,
    background_video_folder,
    client_id,
    client_secret,
    refresh_token,
    access_token,
    finished_video_folder,
    image_folder,
    password,
    subreddit,
    user_agent,
    username,
    video_folder,
)

import praw
from gtts import gTTS
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)
from moviepy.config import change_settings
from youtube_upload.client import YoutubeUploader


change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"}
)

TTS_LANG = "en-US"
WIDTH = 1000
HEIGHT = 1920

if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)
if not os.path.exists(video_folder):
    os.makedirs(video_folder)
if not os.path.exists(image_folder):
    os.makedirs(image_folder)
if not os.path.exists(finished_video_folder):
    os.makedirs(finished_video_folder)


def clean_up():
    try:
        for folder in [audio_folder, video_folder, image_folder, finished_video_folder]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
        print("Cleaup Done")
    except OSError:
        print("Error occurred while deleting files")


# https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
def remove_emojis(text):
    # Define the regex pattern for emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese characters
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\u3030"
        "\ufe0f"
        "]+",
        flags=re.UNICODE,
    )

    return emoji_pattern.sub(r"", text)


def make_audio(text, file_name):
    audio_path = f"{audio_folder}/{file_name}.mp3"
    tts = gTTS(text, lang=TTS_LANG)
    tts.save(audio_path)

    file = AudioFileClip(audio_path)
    return file


def make_background_video(video_duration):
    amount_of_videos = len(os.listdir(background_video_folder))

    background_duration = 0
    background_videos = []

    while background_duration <= video_duration:
        video_number = random.randint(1, amount_of_videos)
        video = (
            VideoFileClip(f"{background_video_folder}/{video_number}.mp4")
            .resize((WIDTH, HEIGHT))
            .without_audio()
        )

        background_videos.append(video)
        background_duration += video.duration

    final_background = concatenate_videoclips(
        background_videos, method="compose"
    ).subclip(0, video_duration)
    return final_background


def youtube_upload():
    uploader = YoutubeUploader(secrets_file_path="resources/youtube_certs.json")
    uploader.authenticate(refresh_token=refresh_token, access_token=access_token)

    options = {
        "title": f"r/{subreddit} #shorts #reddit",
        "description": "Reddit", # maybe a ai descritpion for the funny
        "tags": [
            "redditdaily",
            "minecraftparkour",
            "reddit",
            "redditstories",
            "redditreadings",
            "askreddit",
            "fyp",
            "crazytales",
            "mindblown",
            "nsfw",
            "storytime",
            "communitystories",
            "tiktokdiscoveries",
            "questioneverything",
        ],
        "categoryId": "22",
        "privacyStatus": "public",
        "kids": False,
    }

    uploader.upload("finished_videos/done.mp4", options)
    print("Uploaded to Youtube")



def make_video(title, comments):
    print("Starting Video")

    # clean up code and workspace

    full_audio = make_audio(
        title + comments + " Remember to like and follow!", "full_audio"
    )
    comments = textwrap.fill(comments, width=15)

    final_clips = []
    audio_clips = []

    # TITLE
    title_audio = make_audio(title, "title_audio")
    title_image = generate_title(title, "title_image")

    title_image_clip = ImageClip(img=title_image, duration=title_audio.duration)

    final_clips.append(title_image_clip)
    print("Finished Title")

    # COMMENTS
    for index, comment in enumerate(comments.split("\n")):
        audio_file = make_audio(comment, f"comment_{index + 1}")
        text_clip = TextClip(
            comment,
            color="LightSkyBlue",
            size=(900, 500),
            font="Impact",
            fontsize=125,
            stroke_color="black",
            stroke_width=2,
        ).set_duration(audio_file.duration - 0.40)

        final_clips.append(text_clip)
        audio_clips.append(audio_file)
    print("Finished Comments")

    video = concatenate_videoclips(final_clips, method="compose")

    background_video = make_background_video(full_audio.duration)
    print("Finished Background")

    final_video = video.set_audio(full_audio)
    final_video = CompositeVideoClip([background_video, final_video.set_position("center")], size=(WIDTH, HEIGHT))
    print("Making Final Video")

    final_video.write_videofile(f"{finished_video_folder}/done.mp4", fps=24)
    print("Finished Video")

    # Upload
    youtube_upload(title)

    # Clean up
    clean_up()


def get_comments(subreddit):
    print("Getting Comments")
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent,
    )

    subreddit = reddit.subreddit(subreddit)
    posts = subreddit.hot(limit=amount_of_post)
    comments_count = 0
    comments_chunks = ""
    for post in posts:
        for index, comment in enumerate(post.comments):
            if comment.author is None:  # no more comments left, so just go ahead and use what you have
                if comments_chunks is None:
                    return  # No vaild comments, so no video
                make_video(post.title, comments_chunks)

            if comment.stickied:
                continue  # Skip pinned comments

            if comment.author.name.lower() in ["bot", "mod", "automoderator"]:
                continue  # Trys to skip bots

            if comments_count == amount_of_comments:
                return make_video(post.title, comments_chunks)
            try:
                comments_count += 1
                comment_text = f"{index + 1}. {comment.body}"
                comments_chunks += remove_emojis(comment_text)
            except Exception as e:
                print(e)



while True:
    try:
        print("Starting Process")
        get_comments(subreddit)
    except Exception as e:
        print(f"An error occurred: {e}")
    print("Starting 3 Hour Timer")
    time.sleep(3 * 60 * 60)


