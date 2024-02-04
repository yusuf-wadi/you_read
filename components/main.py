#import langchain.chains as chains
from langchain_community.llms.openai import OpenAIChat 
from openai import OpenAI
import streamlit as st
import os
import subprocess
from openai import AuthenticationError
from pydantic.error_wrappers import ValidationError
import tempfile
from decouple import config as cfg
from youtube_transcript_api import YouTubeTranscriptApi as ytta
from PIL import Image
#import deta
from decouple import config as cfg
# random for now
import random
# set OPENAI_API_KEY in env

#db = deta.Deta(cfg('DETA_KEY')).Base('users')

def call_gpt(prompt):
    #st.session_state["OPENAI_API_KEY"] = cfg("OPENAI_API_KEY")
    try:
        chat = OpenAIChat(model_name='gpt-3.5-turbo', client=None, openai_api_key=st.session_state.get("OPENAI_API_KEY"))
        response = chat.generate(prompt)
        return response.generations[0][0].text
    except AuthenticationError:
        st.error("⚠️ Please set the correct key in the sidebar -> see help icon")
        return ""
    except ValidationError:
        st.error("⚠️ Please set the correct key in the sidebar -> see help icon")
        return ""
def call_assistant(text, asst_id=""):
    """
    call assistant api with given text(str) and assistant id(str)
    """
    # create client
    client = OpenAI(api_key=st.session_state.get("OPENAI_API_KEY"))
    # create thread
    thread = client.beta.threads.create()
    # add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    # get assistant
    asst_id = asst_id if asst_id else "asst_UDwtamlqQSBpdqhInYgHHJ9k"
    assistant = client.beta.assistants.retrieve("asst_UDwtamlqQSBpdqhInYgHHJ9k")
    # create run
    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
    )

    # Periodically retrieve the Run to check status and see if it has completed
    # Should print "in_progress" several times before completing
    while run.status != "completed":
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"Run status: {keep_retrieving_run.status}")

        if keep_retrieving_run.status == "completed":
            print("\n")
            break

    # Retrieve messages added by the Assistant to the thread
    all_messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    return all_messages.data[0].content[0].text.value

def main(): 
    content = st.text_input("Enter a YouTube URL:")
    button = st.button("Generate Booklet") 
    # video frames grabbed
    frame_count = 0
    # only generate when user presses submit
    if button and content and "youtube.com" in content:
        # get video ID
        vID = content.split("v=")[1]
        # get transcript
        transcript = None
        try:
            transcript = ytta.get_transcript(vID)
        except:
            st.error("⚠️ Invalid Video")
        
        # get the text from the transcript
        text = ""
        if transcript:
            for line in transcript:
                text += line['text'] + "\n"
            article = call_assistant(text)
            # output the booklet
            write_booklet(article, transcript)
        
        st.markdown("---")
        st.success("🎉 Done!")

def get_frame(vID, line):
    start = line['start']
    end = line['start'] + 1
    # format the time from seconds to HH:MM:SS
    start =  format_seconds(start)
    end = format_seconds(end)
    print(start, end)
    # run batch file capture.bat with arguments
    subprocess.run(["capture.bat", vID, start, end])

def write_booklet(article, transcript):
    
def format_seconds(seconds):
    return f"{int(seconds//3600):02d}:{int((seconds%3600)//60):02d}:{int(seconds%60):02d}"