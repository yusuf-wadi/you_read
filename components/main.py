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
        client = OpenAI(api_key=st.session_state.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(model = "gpt-3.5-turbo-16k-0613", messages = [{"role" : "user", "content" : prompt}])
        return response.choices[0].message.content
    except AuthenticationError:
        st.error("⚠️ Please set the correct key in the sidebar -> see help icon")
        return ""
    except ValidationError:
        st.error("⚠️ Please set the correct key in the sidebar -> see help icon")
        return ""
    
def stream_gpt(prompt):
    #st.session_state["OPENAI_API_KEY"] = cfg("OPENAI_API_KEY")
    try:
        client = OpenAI(api_key=st.session_state.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(model = "gpt-3.5-turbo-16k-0613", messages = [{"role" : "user", "content" : prompt}], stream = True)
        # return stream object
        return response
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
    # chunk number
    chunk_num = 0
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
            #article = call_assistant(text)
            # moving away from assistant api
            # form prompt
            prompt = f"Given a text, write the text keeping details. IMPORTANT: add [IMAGE_HERE] to denote where an image would be in the article:\n-----\ntext: {text}\n-----\nbooklet:"
            # article = call_gpt(prompt)
            # # write article to debug log
            # with open("debug.log", "w") as f:
            #     f.write(article)
            # # output the booklet
            # write_booklet(article, transcript, vID)
            stream = stream_gpt(prompt)
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    chunk_num += 1
                    # write to debug
                    with open("debug.log", "a") as f:
                        f.write(chunk.choices[0].delta.content)
                    # output the booklet
                    write_booklet(chunk.choices[0].delta.content, transcript, vID, chunk_num)
        
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
    subprocess.run([fr"src\capture.bat", vID, start, end])
    # get most recent image in the output folder *.jpg
    image_name = ""
    with open(fr"output\output_{vID}.txt") as f:
        frames = f.readlines()
        image_name =  frames[-1].strip()
    # open the image
    return Image.open(fr"output\{image_name}.jpg")
        
def write_booklet(article, transcript, vID, chunk_num):
    """
    args: article(str), transcript(list), vID(str)
    
    compares between the response from the assistant and the transcript
    approximates which frames to grab when prompted with [IMAGE_HERE] based on the transcript
    """
    
    # split the texts into words
    article_words = article.split(" ")
    # we need to know what time the word is said in the video
    # we can use the length of the article to approximate the time
    article_length = len(article_words)
    # get the length of the transcript
    transcript_length = len(transcript)
    # get the ratio of the article to the transcript
    ratio = article_length/transcript_length
    
    sentence = ""
    image_amount = 0
    
    for i in range(article_length):
        # add the word to the sentence
        
        # if the word ends with a punctuation, write the sentence to the booklet

        # if the word is [IMAGE_HERE]
        if "[IMAGE_HERE]" in article_words[i] or "[Image]" in article_words[i]:
            # get the line from the transcript
            line = transcript[int(i/ratio)]
            # get the frame from the video
            # limit the images, but cant just be first 5
            if image_amount < 5:
                image = get_frame(vID, line)
                image_amount += 1
                st.image(image, caption=f"Frame {i+1}", use_column_width=True)
        else:
            sentence += article_words[i] + " "
            if "." in article_words[i]:
                st.write(sentence)
                sentence = ""   
            
            
    
    
    
def format_seconds(seconds):
    return f"{int(seconds//3600):02d}:{int((seconds%3600)//60):02d}:{int(seconds%60):02d}"