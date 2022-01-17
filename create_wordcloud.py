from PIL import Image
import numpy as np
import glob
import os

from scipy.ndimage import gaussian_gradient_magnitude
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from datetime import datetime

IMAGE_WIDTH: int = 3840
IMAGE_HEIGHT: int = 2160
MAX_WORDS: int = 500

CUSTOM_FILTER_WORDS = ["okay", "[Music]", "Music", "oh", "uh", "yeah", "left", "right", "let", "want"
                       "going", "gonna", "see", "look", "want", "now", "then", "will", "one"]


def get_latest_raw_caption() -> str:
    """
    Get the latest raw-xxx.txt from export folder
    Read it and parse it into a string
    :return: Content of latest raw caption file
    """
    list_of_files = glob.glob('./export/raw-*.txt')
    selected_file_idx: int = 0

    while True:
        print("\n".join([str(idx) + ". " + x for idx, x in enumerate(list_of_files)]))
        chosen: str = input("Select caption file index: ")

        if int(chosen) < len(list_of_files):
            selected_file_idx = int(chosen)
            break

    text = open(list_of_files[selected_file_idx], encoding="utf-8").read()

    return text


def select_mask() -> str:
    """
    Console input to choose mask from mask folder
    :return: relative path of mask image
    """
    list_of_mask: list = glob.glob('./mask/*')

    while True:
        print("\n".join([str(idx) + ". " + x for idx, x in enumerate(list_of_mask)]))
        chosen: str = input("Select mask index: ")

        if int(chosen) < len(list_of_mask):
            return list_of_mask[int(chosen)]


def create_word_cloud(raw_caption: str, mask_path: str):
    # read the mask image
    input_mask = np.array(Image.open(mask_path))

    # create mask  white is "masked out", else black
    bw_mask = input_mask.copy()
    bw_mask[bw_mask.sum(axis=2) == 0] = 255

    # Downscale image, we do not need
    # mask_color = input_mask[::3, ::3]

    # some finesse: we enforce boundaries between colors so they get less washed out.
    # For that we do some edge detection in the image
    edges = np.mean([gaussian_gradient_magnitude(input_mask[:, :, i] / 255., 2) for i in range(3)], axis=0)
    input_mask[edges > .08] = 255

    stopwords = set(STOPWORDS)

    tmp = [stopwords.add(cfw) for cfw in CUSTOM_FILTER_WORDS]

    wc = WordCloud(background_color="white", max_words=MAX_WORDS, stopwords=stopwords, font_path='./Roboto-Regular.ttf',
                   mask=bw_mask, height=IMAGE_HEIGHT, width=IMAGE_WIDTH, mode="RGB", min_word_length=3)

    # generate word cloud
    wc.generate(raw_caption)

    # store to file
    image_colors = ImageColorGenerator(input_mask)
    wc.recolor(color_func=image_colors)

    tmp_now = datetime.now()
    filename: str = tmp_now.strftime("art-%Y%m%d%H%M%S")
    wc.to_file("./export/" + filename + ".png")

    with open("./export/" + filename + ".svg", "w+") as f:
        f.write(wc.to_svg(embed_font=True))


if __name__ == "__main__":

    raw_caption: str = get_latest_raw_caption()

    mask_path = select_mask()

    create_word_cloud(raw_caption, mask_path)

    print("Completed")

