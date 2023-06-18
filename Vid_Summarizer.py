import evadb
from pytube import YouTube
import os

def Download(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.filter(progressive=True)
    # file_path = None
    try:
        file_path = youtubeObject.first().download()
        print(file_path)
    except Exception as e:
        print(f"An error has occurred: {e}")
    print("Download is completed successfully")

    new_file_name = 'curr_video.mp4'
    new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
    os.rename(file_path, new_file_path)

# Generate text summary of given video
def text_summary(video_url):
  
  cursor = evadb.connect().cursor()
  
  Download(video_url)

  #load the video
  cursor.query("DROP TABLE IF EXISTS VIDEOS;").df()
  cursor.query("LOAD VIDEO 'curr_video.mp4' INTO VIDEOS;").df()

  # Drop the Speech Recognizer UDF if needed
  cursor.query("DROP UDF IF EXISTS SpeechRecognizer;").df()

  # Create a Speech Recognizer UDF using Hugging Face
  text_summarizer_udf_creation = """
          CREATE UDF SpeechRecognizer 
          TYPE HuggingFace 
          'task' 'automatic-speech-recognition' 
          'model' 'openai/whisper-base';
          """
  cursor.query(text_summarizer_udf_creation).df()

  # Drop the Text Summarization UDF if needed
  cursor.query("DROP UDF IF EXISTS TextSummarizer;").df()

  # Create a Text Summarization UDF using Hugging Face
  text_summarizer_udf_creation = """
          CREATE UDF TextSummarizer 
          TYPE HuggingFace 
          'task' 'summarization';
          """
  cursor.query(text_summarizer_udf_creation).df()

  # Drop the table if needed
  cursor.query("DROP TABLE IF EXISTS TEXT_SUMMARY;").df()


  # Create a materialized view of the text summarization output
  text_summarization_query = """
      CREATE MATERIALIZED VIEW 
      TEXT_SUMMARY(summary_text) AS 
      SELECT TextSummarizer(SpeechRecognizer(audio)) FROM VIDEOS; 
      """
  cursor.query(text_summarization_query).df()

  chatgpt_udf = """
      SELECT summary_text 
      FROM TEXT_SUMMARY;
      """
  df = cursor.query(chatgpt_udf).df()

  return str(df.values[0][0])
