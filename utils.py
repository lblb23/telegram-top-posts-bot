import instaloader
from instaloader import Profile
import pandas as pd
import re
from tabulate import tabulate
from telegram.ext import CallbackContext

L = instaloader.Instaloader(
    sleep=True,
    download_geotags=False,
    filename_pattern="{shortcode}",
    quiet=False,
    download_video_thumbnails=False,
    download_comments=False,
)


def thousands_sep(x: str) -> str:
    """
    Return number with thousand separators
    :param x: number
    :return: number with thousand separators
    """
    return "{:,}".format(x).replace(",", " ")


def get_top_posts(
    context: CallbackContext,
    chat_id: int,
    messages: dict,
    profile_url: str,
    top_n=10,
    lookback_posts=100,
) -> tuple:
    """
    1. Get from message instagram username
    2. Get last 100 posts
    3. Get top 10 videos by views and top 10 photos by likes
    4. Send to user
    :param context: callback context
    :param chat_id: chat id with user
    :param messages: dict with templates of messages
    :param profile_url: messsage from user
    :param top_n:
    :param lookback_posts:
    :return: success status and reason if failed
    """
    context.bot.send_message(chat_id=chat_id, text=messages["loading"])
    try:
        username = re.findall(
            r"(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am)\/([A-Za-z0-9-_.]+)",
            profile_url,
        )[0]
        profile = Profile.from_username(L.context, username)

        n = 0
        posts_photos = []
        posts_videos = []

        for post in profile.get_posts():
            if n > lookback_posts:
                break

            link = f"https://www.instagram.com/p/{post.shortcode}"

            if post.is_video:
                posts_videos.append(
                    {"Post URL": link, "Views": post.video_view_count,}
                )
            else:
                posts_photos.append(
                    {"Post URL": link, "Likes": post.likes,}
                )
            n = n + 1

        if len(posts_photos) > 0:
            df_photos = (
                pd.DataFrame(posts_photos)
                .sort_values("Likes", ascending=False)
                .head(n=top_n)
                .set_index("Post URL")
            )
            df_photos["Likes"] = df_photos["Likes"].apply(
                lambda x: f"{thousands_sep(x)} likes"
            )

            top_photos = "Top posts by likes:\n" + tabulate(df_photos, tablefmt="plain")

            context.bot.send_message(
                chat_id=chat_id, text=top_photos, disable_web_page_preview=True
            )

        if len(posts_videos) > 0:
            df_videos = (
                pd.DataFrame(posts_videos)
                .sort_values("Views", ascending=False)
                .head(n=top_n)
                .set_index("Post URL")
            )
            df_videos["Views"] = df_videos["Views"].apply(
                lambda x: f"{thousands_sep(x)} views"
            )

            top_videos = "Top videos by views:\n" + tabulate(df_videos,
                                                             tablefmt="plain")
            context.bot.send_message(
                chat_id=chat_id, text=top_videos, disable_web_page_preview=True
            )

        result = True
        traceback = "Success"

    except IndexError as e:
        context.bot.send_message(chat_id=chat_id, text=messages["error"])
        result = False
        traceback = str(e)

    return result, traceback
