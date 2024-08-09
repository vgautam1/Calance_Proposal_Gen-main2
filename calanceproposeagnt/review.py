import streamlit as st
import uuid

def review_and_comment(proposal_content):
    st.subheader("Review and Comment on the Draft Proposal")
    comments = {}
    for section, content in proposal_content.items():
        st.write(f"**{section.replace('_', ' ').title()}**")
        st.write(content)
        unique_key = f"comment_{section}_{uuid.uuid4()}"  # Use UUID for uniqueness
        comment = st.text_area(f"Comments for {section}:", key=unique_key)
        comments[section] = comment
    return comments
