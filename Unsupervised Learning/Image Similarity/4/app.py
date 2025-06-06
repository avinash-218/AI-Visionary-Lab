from qdrant_client import QdrantClient
from io import BytesIO
import streamlit as st
import base64

QDRANT_DB_URL='https://0cef25e0-9d34-416f-a362-f8ed3c6e61a9.us-west-1-0.aws.cloud.qdrant.io'
QDRANT_API_KEY='dHT9IqabKhBnzWOtQCa5jFfOWQj5H1Y3TG8c68ov8wW5sLL5f33lMw'

collection_name = 'animal_images'

if 'selected_record' not in st.session_state:
    st.session_state.selected_record = None

def set_selected_record(new_record):
    st.session_state.selected_record = new_record

@st.cache_resource
def get_client():
    return QdrantClient(url=QDRANT_DB_URL, api_key=QDRANT_API_KEY)

def get_initial_records():
    client = get_client()

    records, _ = client.scroll(
        collection_name=collection_name,
        with_vectors=False,
        limit=5
    )
    return records

def get_similar_records():
    client = get_client()

    if st.session_state.selected_record is not None:
        return client.query_points(
            collection_name=collection_name,
            positive=[st.session_state.selected_record.id],
            limit=5
        )
    
    return None

def get_bytes_from_base64(base64_string):
    return BytesIO(base64.b64decode(base64_string))

records = get_similar_records() if st.session_state.selected_record is not None else get_initial_records()

if st.session_state.selected_record:
    image_bytes = get_bytes_from_base64(
        st.session_state.selected_record.payload['base64'])
    st.header('Similarty Search')
    st.image(image=image_bytes)
    st.divider()

column = st.columns(3)

for idx, record in enumerate(records):
    col_idx = idx % 3
    image_bytes = get_bytes_from_base64(record.payload['base64'])

    with column[col_idx]:
        st.image(image=image_bytes)
        st.button(
            label='Find similar',
            key=record.id,
            on_click=set_selected_record,
            args=[record]
        )