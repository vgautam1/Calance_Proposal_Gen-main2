import streamlit as st
from config import configure_llm
from extractors import extract_text_from_file
from research import perform_research
from review import review_and_comment
from improve import improve_proposal
from docx_generator import generate_docx
from templates import get_prompt_template
from utils import CustomOutputParser
from langchain.output_parsers import ResponseSchema  # Add this import
from langchain.schema.runnable import RunnablePassthrough  # Add this import
from collections import defaultdict  # Add this import
import io
import logging
import json
import uuid

def main():
    st.set_page_config(page_title="AI-Powered Proposal Generator", layout="wide")
    st.title('AI-Powered Proposal Generator')

    # Sidebar for API and Model Configuration
    st.sidebar.title('API and Model Configuration')
    api = st.sidebar.selectbox('Choose an API', ['Ollama', 'OpenRouter', 'OpenAI'])
    api_key = st.sidebar.text_input('Enter API Key (not needed for Ollama)', type='password')
    temp = st.sidebar.slider("Model Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    # LLM Configuration
    llm = configure_llm(api, api_key, temp)

    # User Input
    client_name = st.text_input('Enter client name:')
    project_type = st.selectbox('Select project type:', [
        'Software Development', 
        'Consulting', 
        'Integration', 
        'Other', 
        'Generative AI', 
        'Cloud Native Development', 
        'Cloud Infrastructure', 
        'MS SharePoint'
    ])
    user_input = st.text_area('Enter your project requirements:')
    uploaded_docs = st.file_uploader('Upload relevant documents', accept_multiple_files=True)
    additional_info = st.text_area('Enter any additional information or feedback:')

    # Process uploaded documents
    if uploaded_docs:
        for doc in uploaded_docs:
            doc_text = extract_text_from_file(doc)
            user_input += f"\n\nContent from {doc.name}:\n{doc_text}"

    if st.button('Generate Proposal'):
        if user_input and client_name and llm:
            with st.spinner('Generating proposal... This may take a few minutes.'):
                try:
                    research_result = perform_research(user_input, additional_info, llm)
                    if research_result["status"] == "success":
                        user_input += f"\n\nResearch Result:\n{research_result['data']}"
                    else:
                        st.warning(research_result["message"])
                        user_input += f"\n\nResearch Result:\n{research_result['message']}"
                except Exception as e:
                    st.warning(f"An error occurred during research: {str(e)}")
                    research_result = "Research could not be completed due to an error."
                    user_input += f"\n\nResearch Result:\n{research_result}"

                # Define the output structure based on project type
                response_schemas = [
                    ResponseSchema(name="date", description="The date of the proposal"),
                    ResponseSchema(name="project_name", description="The name of the project"),
                    ResponseSchema(name="description", description="Brief description of the project and agreement"),
                    ResponseSchema(name="purpose", description="The purpose of the project"),
                    ResponseSchema(name="scope", description="Detailed scope of the project, including functional and non-functional requirements"),
                    ResponseSchema(name="approach", description="The approach to be used for the project, including technological framework and delivery framework"),
                    ResponseSchema(name="engagement_approach", description="Details on the engagement approach, such as Time & Materials"),
                    ResponseSchema(name="project_estimated_timeline", description="Estimated timeline for the project"),
                    ResponseSchema(name="development_hosting_support_maintenance_estimates", description="Estimates for development, hosting, support, and maintenance"),
                    ResponseSchema(name="risks_constraints_dependencies", description="Identified risks, constraints, and dependencies for the project")
                ]

                output_parser = CustomOutputParser.from_response_schemas(response_schemas)

                # Create the prompt template
                prompt = get_prompt_template(client_name, project_type, user_input, additional_info, output_parser.get_format_instructions())

                # Create the chain
                chain = (
                    {"client_name": RunnablePassthrough(), 
                     "project_type": RunnablePassthrough(),
                     "user_input": RunnablePassthrough(),
                     "additional_info": RunnablePassthrough(),
                     "format_instructions": lambda _: output_parser.get_format_instructions()}
                    | prompt
                    | llm
                    | output_parser
                )

                try:
                    # Generate the proposal
                    result = chain.invoke({
                        "client_name": client_name,
                        "project_type": project_type,
                        "user_input": user_input,
                        "additional_info": additional_info
                    })

                    # Ensure all required keys are present in the result
                    required_keys = ['date', 'project_name', 'description', 'purpose', 'scope', 'approach', 'engagement_approach', 'project_estimated_timeline', 'development_hosting_support_maintenance_estimates', 'risks_constraints_dependencies']
                    for key in required_keys:
                        if key not in result:
                            result[key] = "Not provided"

                    # Store the result in session state
                    st.session_state.result = result

                    # Display the generated proposal
                    st.subheader("Generated Proposal:")
                    for section, content in result.items():
                        st.write(f"**{section.replace('_', ' ').title()}**")
                        st.write(content)
                        st.write("---")

                    # Review and comment on the draft proposal
                    comments = review_and_comment(result)

                    # Store the comments in session state
                    st.session_state.comments = comments

                    # Improve the proposal based on comments
                    final_proposal = improve_proposal(result, comments, llm)
                    
                    # Ensure all required keys are present in the final proposal
                    for key in required_keys:
                        if key not in final_proposal:
                            final_proposal[key] = "Not provided"

                    # Store the final proposal in session state
                    st.session_state.final_proposal = final_proposal
                    logging.info(f"Final proposal structure: {json.dumps(final_proposal, indent=2)}")

                    # Display the final proposal
                    st.subheader("Final Proposal:")
                    for section, content in final_proposal.items():
                        st.write(f"**{section.replace('_', ' ').title()}**")
                        st.write(content)
                        st.write("---")

                    # Generate DOCX
                    logging.info("Generating DOCX file...")
                    doc = generate_docx(final_proposal, client_name)
                    logging.info("DOCX file generated successfully")

                    # Save DOCX to BytesIO object
                    docx_bytes = io.BytesIO()
                    doc.save(docx_bytes)
                    docx_bytes.seek(0)

                    # Read the page count from the saved document
                    doc = Document(docx_bytes)
                    page_count = len(doc.element.xpath('//w:p'))  # Approximate page count based on paragraphs

                    # Update the footer with the page count
                    section = doc.sections[0]
                    footer = section.footer
                    footer.paragraphs[0].text = f"Page 1 of {page_count}"

                    # Save the updated document to a new BytesIO object
                    updated_docx_bytes = io.BytesIO()
                    doc.save(updated_docx_bytes)
                    updated_docx_bytes.seek(0)

                    # Provide download button with a unique key
                    st.download_button(
                        label="Download Proposal as DOCX",
                        data=updated_docx_bytes,
                        file_name=f"Proposal_{client_name}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="unique_download_button_key"  # Add a unique key here
                    )

                    st.success("Proposal generated successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        elif not llm:
            st.error("Please configure and apply an LLM before generating the proposal.")
    else:
        st.warning('Please enter the client name and project requirements.')

    # Check if there are stored results in session state
    if hasattr(st.session_state, 'result'):
        st.subheader("Generated Proposal:")
        for section, content in st.session_state.result.items():
            st.write(f"**{section.replace('_', ' ').title()}**")
            st.write(content)
            st.write("---")

        # Review and comment on the draft proposal
        comments = review_and_comment(st.session_state.result)

        # Store the comments in session state
        st.session_state.comments = comments

        # Improve the proposal based on comments
        final_proposal = improve_proposal(st.session_state.result, st.session_state.comments, llm)

        # Ensure all required keys are present in the final proposal
        for key in required_keys:
            if key not in final_proposal:
                final_proposal[key] = "Not provided"

        # Store the final proposal in session state
        st.session_state.final_proposal = final_proposal

        # Display the final proposal
        st.subheader("Final Proposal:")
        for section, content in final_proposal.items():
            st.write(f"**{section.replace('_', ' ').title()}**")
            st.write(content)
            st.write("---")

        # Generate DOCX
        doc = generate_docx(final_proposal, client_name)
        
        # Save DOCX to BytesIO object
        docx_bytes = io.BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)

        # Read the page count from the saved document
        doc = Document(docx_bytes)
        page_count = len(doc.element.xpath('//w:p'))  # Approximate page count based on paragraphs

        # Update the footer with the page count
        section = doc.sections[0]
        footer = section.footer
        footer.paragraphs[0].text = f"Page 1 of {page_count}"

        # Save the updated document to a new BytesIO object
        updated_docx_bytes = io.BytesIO()
        doc.save(updated_docx_bytes)
        updated_docx_bytes.seek(0)

        # Provide download button with a unique key
        st.download_button(
            label="Download Proposal as DOCX",
            data=updated_docx_bytes,
            file_name=f"Proposal_{client_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="unique_download_button_key_2"  # Add a unique key here
        )

        st.success("Proposal generated successfully!")

if __name__ == "__main__":
    main()
