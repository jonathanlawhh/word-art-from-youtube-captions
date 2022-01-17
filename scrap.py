import time
import pandas as pd
import requests
import re
import json
from xml.etree import ElementTree
import html
from datetime import datetime


def get_video_list(youtube_playlist_url: str) -> list:
    """
    1. Load Gordan Ramsay playlist
    2. Extract the Javascript variable that stores the playlist information
    3. Store it in an object array
    :param youtube_playlist_url: YouTube playlist url. Eg: https://youtube.com/playlist?list=...
    :return: [vidId]
    """
    resp: requests.Response = requests.get(youtube_playlist_url)

    # BROWSER DEBUG: console.log(ytInitialData)
    raw_html: str = resp.text
    result = re.search('var ytInitialData = (.*);<', raw_html)
    result_json = json.loads(result.group(1))

    vid_raw: list = result_json["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]["contents"]

    vid_list: list = [v["playlistVideoRenderer"]["videoId"] for v in vid_raw if "playlistVideoRenderer" in v]

    return vid_list


def get_request_url(vid_id: str) -> dict:
    """
    Retrieves the URL required to download the captions.
    This step is necessary because YouTube has implemented hashed their request in a form of signature.
    We will need the correct signature to download it.
    :param vid_id: Video ID
    :return: { title, description, author, keywords, caption_url }
    """
    youtube_url: str = "https://www.youtube.com/watch?v=" + vid_id
    print("Scrapping", youtube_url)

    resp: requests.Response = requests.get(youtube_url)
    raw_html = resp.text

    # Exclude members only videos
    if '"label":"Members only"' in raw_html or '"label":"Ahli sahaja"' in raw_html:
        return {}

    # Very specifically target this request url
    result = re.search('var ytInitialPlayerResponse = (.*);<', raw_html)

    result_json = json.loads(result.group(1))

    # Ensure language is in English
    if "captions" in result_json:
        caption_tracks: list = result_json["captions"]["playerCaptionsTracklistRenderer"]["captionTracks"]

        tmp_url = ""
        for c in caption_tracks:
            if c["languageCode"] == "en":
                tmp_url = c["baseUrl"].replace("\\u0026", "&")
                break

        # Prevent spam pattern
        time.sleep(1)

        return {
            "title": result_json["videoDetails"]["title"],
            "description": result_json["videoDetails"]["shortDescription"].replace("\n", " "),
            "author": result_json["videoDetails"]["author"],
            "keywords": ",".join(result_json["videoDetails"]["keywords"]),
            "caption_url": tmp_url
        }
    else:
        return {}


def get_video_subtitle(request_url: str) -> str:
    """
    The caption request URL will return an XML format file.
    Parse the XML and return the caption paragraph.
    :param request_url: eg. https://youtube.com/api...?v=....
    :return:
    """
    resp: requests.Response = requests.get(request_url)

    tree = ElementTree.fromstring(resp.content)

    res: list = [html.unescape(t.text.replace("\n", "")) for t in tree if t.text is not None]

    return " ".join(res)


if __name__ == "__main__":

    while True:

        # Get playlist URL from user
        while True:
            print("YouTube playlist URL should look like: https://www.youtube.com/playlist?list=XXX")
            playlist_link: str = input("Playlist URL: ")

            if "https://www.youtube.com/playlist?list=" in playlist_link:
                break

        playlist_video_list: list = get_video_list(playlist_link)
        video_info: list = [get_request_url(v) for v in playlist_video_list if len(v) > 0]

        for vi in video_info:
            if bool(vi):
                print(vi["title"])
                vi["caption"] = get_video_subtitle(vi["caption_url"])

        tmp_now = datetime.now()
        filename: str = video_info[0]["author"] + "-" + tmp_now.strftime("%Y%m%d%H%M%S")

        df = pd.DataFrame(video_info)
        df.drop(columns=["caption_url"], inplace=True)
        df.to_csv(path_or_buf="".join(["./export/dataset-", filename, ".csv"]), index=False)

        raw_caption = df["caption"].str.cat(sep=" ")
        with open("./export/raw-" + filename + ".txt", "w+", encoding="utf-8") as f:
            f.write(raw_caption)

        print("============================")
        print("Scrapping complete")
        print("")
