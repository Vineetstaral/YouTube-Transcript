import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
from huggingface_hub import InferenceClient

# Hugging Face Token (replace with your actual token or use Streamlit secrets)
HUGGINGFACE_TOKEN = "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"

# Initialize client
client = InferenceClient(token=HUGGINGFACE_TOKEN)

# Function to extract transcript
def get_transcript(video_url):
    video_id = re.search(
        r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',
        video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    video_id = video_id.group(1)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US'])
    except:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception as e:
            return None

    return " ".join([entry['text'] for entry in transcript])

# Streamlit App
st.title("🎥 YouTube to Blog Generator")
st.write("Paste a YouTube link below to convert the transcript into a professional blog post.")

youtube_url = st.text_input("YouTube Video URL")

if youtube_url:
    with st.spinner("Fetching transcript..."):
        transcript = get_transcript(youtube_url)
    
    if transcript:
        st.success("Transcript fetched successfully!")
        
        prompt = f"""
        Convert this YouTube transcript into a professional blog post:

        {transcript}

        Instructions:
        - Use markdown formatting (headings, bullet points)
        - Keep it engaging and informative
        - Length: 500-800 words
        """

        with st.spinner("Generating blog post..."):
            blog_post = client.text_generation(
                prompt,
                model="mistralai/Mistral-7B-Instruct-v0.1",
                max_new_tokens=1000,
                temperature=0.7
            )

        st.markdown("### 📝 Generated Blog Post")
        st.markdown(blog_post)
    else:
        st.error("Could not fetch a transcript for this video. It might not have English subtitles.")
