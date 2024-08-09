from langchain.prompts import ChatPromptTemplate

def get_prompt_template(client_name, project_type, user_input, additional_info, format_instructions):
    return ChatPromptTemplate.from_template(
        """You are an expert proposal writer for Calance. Based on the following information, generate a comprehensive proposal:

        Client Name: {client_name}
        Project Type: {project_type}
        Project Requirements: {user_input}
        Additional Information: {additional_info}

        {format_instructions}

        Ensure the proposal is professional, well-structured, and tailored to the client's needs. Include all sections as specified in the format instructions, paying special attention to the risks, constraints, and dependencies section."""
    )
