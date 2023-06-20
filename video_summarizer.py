import os
import evadb
from pytube import YouTube, extract
import pandas as pd
import pickle as pkl
import datetime

DEFAULT_VIDEO_LINK = "https://www.youtube.com/watch?v=TvS1lHEQoKk"
MAX_CHUNK = 500


def download_video(link):
    """Downloads a YouTube video from url.

    Args:
        link (str): url of the target YouTube video.
    """
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.filter(progressive=True)
    youtubeObject.first().download(filename="curr_video.mp4")


def setup_udfs(cursor):
    """Initializes the UDFs

    Args:
        cursor (EVADBCursor): evadb api cursor.
    """
    # Drop the Speech Recognizer UDF if needed
    cursor.query("DROP UDF IF EXISTS SpeechRecognizer;").df()

    # Create a Speech Recognizer UDF using Hugging Face
    speech_recognizer_udf_creation = """
        CREATE UDF SpeechRecognizer
        TYPE HuggingFace
        'task' 'automatic-speech-recognition'
        'model' 'openai/whisper-base';
        """
    cursor.query(speech_recognizer_udf_creation).df()

    # Drop the Text Summarization UDF if needed
    cursor.query("DROP UDF IF EXISTS TextSummarizer;").df()

    # Create a Text Summarization UDF using Hugging Face
    text_summarizer_udf_creation = """
        CREATE UDF TextSummarizer
        TYPE HuggingFace
        'task' 'summarization';
        """
    cursor.query(text_summarizer_udf_creation).df()


def transcribe(cursor):
    """Transcribes the video

    Args:
        cursor (EVADBCursor): evadb api cursor.
    """

    # load the video
    cursor.query("DROP TABLE IF EXISTS VIDEOS;").df()
    cursor.query("LOAD VIDEO 'curr_video.mp4' INTO VIDEOS;").df()

    # Drop the table if needed
    cursor.query("DROP TABLE IF EXISTS TEXT_SUMMARY;").df()

    # Create a materialized view of the text summarization output
    text_summarization_query = """
    SELECT SpeechRecognizer(audio) 
    FROM VIDEOS;
    """

    df = cursor.query(text_summarization_query).df()
    return df


def partition_transcription(df):
    """Parititons the transcription according to the acceptable size for summarization

    Args:
        df (Pandas dataframe): dataframe containing the transcription
    """

    text = df["speechrecognizer.text"].values[0].split(" ")
    text_len = len(text)

    y = (text_len // MAX_CHUNK) * MAX_CHUNK
    text_arr = [text[x : x + MAX_CHUNK] for x in range(0, y, MAX_CHUNK)]

    text_arr[-1] += text[y:text_len]

    data = []
    for arr in text_arr:
        data.append(" ".join(arr))

    parted_df = pd.DataFrame(data, columns=["text"])
    parted_df.to_csv("transcript.csv")


def summarize(cursor):
    """Summarizes the video transcript

    Args:
        cursor (EVADBCursor): evadb api cursor.
    """

    cursor.query("""DROP TABLE IF EXISTS Transcript;""").execute()
    cursor.query("""CREATE TABLE IF NOT EXISTS Transcript (text TEXT(50));""").execute()
    cursor.load("transcript.csv", "Transcript", "csv").execute()

    cursor.query("DROP TABLE IF EXISTS TEXT_SUMMARY;").df()

    select_summary_query = """
            SELECT TextSummarizer(text) FROM Transcript;;
            """
    df = cursor.query(select_summary_query).df()

    summary = "\n".join(df["textsummarizer.summary_text"].values)

    return summary


def fetch_existing_summary(video_id):
    """Fetches the video summary if it has been stored previously

    Args:
        video_id (str): id of the youtube video
    """

    file_path = os.path.join("/", "content", "evadb_data", "tmp")

    for summary_file in os.listdir(file_path):
        if summary_file.split("@")[0] == video_id:
            print("Found summary")
            # Unpickle data from the file
            with open(os.path.join(file_path, summary_file), "rb") as file:
                summary_dict = pkl.load(file)

            return summary_dict["summary"]

    return None


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("curr_video.mp4"):
        os.remove("curr_video.mp4")
    if os.path.exists("transcript.csv"):
        os.remove("transcript.csv")


def main():
    print(
        "🔮 Welcome to EvaDB! This app lets you summarize any YouTube video for a quick review! \nYou will only need to supply a Youtube URL.\n\n"
    )

    # Get Youtube video url
    video_link = str(
        input(
            "📺 Enter the URL of the YouTube video (press Enter to use a default Youtube video):"
        )
    )

    if video_link == "":
        video_link = DEFAULT_VIDEO_LINK

    try:
        # establish evadb api cursor
        cursor = evadb.connect().cursor()

        video_id = extract.video_id(video_link)
        summary = fetch_existing_summary(video_id)

        if not summary:
            print("New Video, Generating Summary....\n")
            download_video(video_link)
            setup_udfs(cursor)
            df = transcribe(cursor)
            partition_transcription(df)
            summary = summarize(cursor)

            data = {"summary": summary}

            # Pickle data to a file
            filename = f"{video_id}@{datetime.datetime.now()}.pickle"

            file_path = os.path.join("/", "content", "evadb_data", "tmp", filename)

            with open(file_path, "wb") as file:
                pkl.dump(data, file)

        print(f"The video summary is: {summary}")

        cleanup()
        print("\nSession ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("Session ended with an error.")
        print(e)
        print("===========================================")


if __name__ == "__main__":
    main()
