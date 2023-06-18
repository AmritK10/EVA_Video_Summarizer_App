from flask import Flask,render_template,redirect,request,jsonify
from Vid_Summarizer import text_summary
import os

# Create app
# __name__ == __main__
app = Flask(__name__)

# Create API End point
@app.route("/summarize",methods=["POST"])
def summarize():
    if request.method == "POST":
        summarized_ans = text_summary(request.get_json()['video_url'])
        return jsonify(summarized_ans)

# App Listening
if __name__ == "__main__":
	app.run()
