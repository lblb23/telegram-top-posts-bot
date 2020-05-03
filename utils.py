import instaloader
from instaloader import Profile
import pandas as pd
import re
from tabulate import tabulate

L = instaloader.Instaloader(
    sleep=True,
    download_geotags=False,
    filename_pattern="{shortcode}",
    quiet=False,
    download_video_thumbnails=False,
    download_comments=False,
)


def thousands_sep(x):
    return "{:,}".format(x).replace(",", " ")


def get_top_posts(
    context, chat_id, messages, profile_url, top_n=10, lookback_posts=100
):
    context.bot.send_message(chat_id=chat_id, text=messages["loading"])
    try:
        username = re.findall(
            r"(?:(?:http|https):\/\/)?(?:www.)?(?:instagram.com|instagr.am)\/([A-Za-z0-9-_]+)",
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

        df_videos = (
            pd.DataFrame(posts_videos)
            .sort_values("Views", ascending=False)
            .head(n=top_n)
            .set_index("Post URL")
        )
        df_videos["Views"] = df_videos["Views"].apply(
            lambda x: f"{thousands_sep(x)} views"
        )

        df_photos = (
            pd.DataFrame(posts_photos)
            .sort_values("Likes", ascending=False)
            .head(n=top_n)
            .set_index("Post URL")
        )
        df_photos["Likes"] = df_photos["Likes"].apply(
            lambda x: f"{thousands_sep(x)} likes"
        )

        top_videos = "Top videos by views:\n" + tabulate(df_videos, tablefmt="plain")
        top_photos = "Top posts by likes:\n" + tabulate(df_photos, tablefmt="plain")

        context.bot.send_message(
            chat_id=chat_id, text=top_videos, disable_web_page_preview=True
        )
        context.bot.send_message(
            chat_id=chat_id, text=top_photos, disable_web_page_preview=True
        )

    except IndexError as e:
        context.bot.send_message(chat_id=chat_id, text=messages["error"])
        result = False
        traceback = str(e)

    return result, traceback
