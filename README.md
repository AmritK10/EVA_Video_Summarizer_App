# EVA_Video_Summarizer_App

This app lets you summarize any Youtube video by just providing the link! </br>
Powered by [EvaDB](https://github.com/georgia-tech-db/eva), a Python-based database system for AI applications developed by Georgia Tech's DB Group.

## Setup

Ensure that the local Python version is >= 3.8. Install the required libraries:

```bat
pip install -r requirements.txt
```

<b>Note: If using Macos >= 12 or Apple Silicon Macs then use eva-decord==0.6.1 instead of decord</b>

## Usage

Run script:

```bat
python video_summarizer.py
```

## Example

```bat
🔮 Welcome to EvaDB! This app lets you summarize any YouTube video for a quick review!
You will only need to supply a Youtube URL.


📺 Enter the URL of the YouTube video (press Enter to use a default Youtube video):
New Video, Generating Summary....

Downloading Video...
Video Downloaded Successfully!

The video summary is: WWE DC presentation of Apple didn't mention virtual reality once in 45 minutes. Google I.O. developer conference used a lot of AI-related terms, but they didn't call themselves an AI-first company. Uncle BHD explains why this is the case.
Tech reviewer noticed that Apple avoids comparing their products to other companies or acknowledging other products at all. Apple prefers to name their products and put a name on them rather than compare them to other products. Apple is very conscious of their image and they don't want to attach themselves to a word that they can't control.
Apple's promotion for its new iPhone is more responsive and smooth than any other promotion they've ever had. The new vision pro headset that Apple just unveiled in particular is interesting. It's clear that Apple has future plans with this headset to make it cheaper and smaller and higher tech.

Session ended.
===========================================
```
