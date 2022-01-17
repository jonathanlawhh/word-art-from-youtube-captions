<h1 align="center">▶️Word Cloud from YouTube captions</h1>
<p align="center">
    <a href="https://jonathanlawhh.com/works/nft/" target="_blank">https://jonathanlawhh.com/works/nft/</a>
</p>

<p align="center">
    Generating a word cloud based on captions from YouTubers video playlist. <br>
    Using <a href="https://amueller.github.io/word_cloud/" target="_blank">WordCloud for Python by Andreas Muller</a>! <br>
    This project may not work in the future if YouTube updated their website code.
</p>

<p align="center">
    <img src="https://jonathanlawhh.com/gallery/nft/ramsay-in-ten-1.svg" />
</p>

## 🖥️ Setup
Install Python >3.8
```bash
$ git clone https://github.com/jonathanlawhh/word-art-from-youtube-captions.git
$ cd word-art-from-youtube-captions
$ pip3 install -r requirements.txt
```

## 📁 Directory
**scrap.py** <br>
Running `python scrap.py` in console will start the program. 
Input the playlist URL accordingly and the script will run through every video in that playlist, 
attempt to extract the English caption, and save it in the export folder.<br>
YouTube playlist URL should look like: https://www.youtube.com/playlist?list=XXX

**create_wordcloud.py** <br>
Running `python create_wordcloud.py` will give you the option in order to:
1. Select the extracted captions from scrap.py output in exports folder
2. Select a mask for your word art. White will be the excluded area. Please refer to mask folder for sample.
3. Generate the word art in SVG and PNG in the export folder with the dataset name.

**export folder** <br>
All dataset of captions and generated word art will be kept here.

**mask folder** <br>
The mask to use when generating the word art can be kept here and selected later.

**Roboto-Regular.ttf** <br>
Font used in word art. Feel free to change.
