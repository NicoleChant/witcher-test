import streamlit as st
import base64
from google.cloud import storage
import os
import json
import random

## define a storage Client if it doesn't already exist
if "client" not in st.session_state:
    st.session_state["client"] = storage.Client()

@st.experimental_memo
def get_img_as_base64(file):
    with open(file , "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_img = get_img_as_base64("images/geralt.jpg")
side_img = get_img_as_base64("images/symbol.jpg")

page_bg_img = f"""
    <style>
    .body {{
        font-size:200px;
    }}
    [data-testid="stHeader"]{{
        background-color: rgba(0,0,0,0);
    }}

    [data-testid="stSidebar"]{{
        background-image: url("data:image/jpg;base64,{side_img}");
        background-position: center;
        background-repeat: no-repeat;
    }}
    [data-testid="stMarkdownContainer"]{{
            font-size:large;
            font:20px;
            font-family:Comic Sans MS;
            color:white;
            margin-top:-80px;
            background-position: center;
            text-align: center;

        }}
    [data-testid="stAppViewContainer"]
    {{
        background-image: url("data:image/jpg;base64,{bg_img}");
        background-position: center;
        background-repeat: no-repeat;
        }}

    .title {{
        font-size:60px;
    }}

    .quote {{
        font-size:30px;
        font-family:Comic Sans MS;
        background-color:black;
        opacity:0.8;
        margin-top:100px;
    }}

    [data-testid="stForm"]{{
        background-color:black;
        opacity:0.8;
    }}
    </style>"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.markdown("<div class='title'> Witcher 3: Quotes </div>" , unsafe_allow_html=True)
#st.title("Witcher 3: Quotes")


def get_quote_from_cloud(choice: str) -> dict[str, str]:
    #bucket = st.session_state["client"].bucket(os.getenv("BUCKET_NAME"))
    client = storage.Client()
    bucket = client.bucket(os.getenv("BUCKET_NAME"))
    blob = bucket.blob(os.getenv("BLOB_NAME"))
    data = json.loads(blob.download_as_string())
    return random.choice(
        list(filter(lambda quote: quote.get("author").startswith(choice),
                    data)))

def main():
    with st.sidebar:
        st.radio("Pages", ("Home","Quotes"))

    submitted = None
    _ , _ , col3 = st.columns(3)
    with col3:
        with st.form("Search"):
            choice = st.selectbox("Choose Character", [
                "Geralt", "Yennefer", "Ciri", "Cahir", "Triss", "Mousesack",
                "Tissaia", "Queen Calanthe", "Renfri"
            ])
            submitted = st.form_submit_button("Submit")

    if submitted:
        quote_data = get_quote_from_cloud(choice)
        author, quote = quote_data.get("author"), quote_data.get("quote")
        st.markdown(
            f"<div class='quote'> {quote} </div><br> ~ <span style='font-size:20px'> {author} </span>",
            unsafe_allow_html=True)

if __name__ == "__main__":
    main()
