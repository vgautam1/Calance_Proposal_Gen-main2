import json
import logging
from langchain.prompts import ChatPromptTemplate

def improve_proposal(proposal_content, comments, llm):
    prompt = ChatPromptTemplate.from_template(
        """You are an expert proposal reviewer. Improve the following proposal sections based on the comments provided:

        {proposal_content}
        Comments: {comments}

        Ensure the improvements are professional and address the comments effectively. Return the improved proposal as a JSON object with the same structure as the original proposal. Make sure to include all required sections: date, project_name, description, purpose, scope, approach, engagement_approach, project_estimated_timeline, development_hosting_support_maintenance_estimates, and risks_constraints_dependencies."""
    )
    chain = prompt | llm
    improved_proposal = chain.invoke({"proposal_content": json.dumps(proposal_content), "comments": json.dumps(comments)})
    
    if isinstance(improved_proposal, str):
        try:
            parsed_proposal = json.loads(improved_proposal)
        except json.JSONDecodeError:
            logging.error("Failed to parse the improved proposal")
            parsed_proposal = proposal_content
    elif hasattr(improved_proposal, 'content'):
        try:
            parsed_proposal = json.loads(improved_proposal.content)
        except json.JSONDecodeError:
            logging.error("Failed to parse the improved proposal")
            parsed_proposal = proposal_content
    else:
        logging.error("Unexpected response format")
        parsed_proposal = proposal_content

    # Ensure all required keys are present
    required_keys = ['date', 'project_name', 'description', 'purpose', 'scope', 'approach', 'engagement_approach', 'project_estimated_timeline', 'development_hosting_support_maintenance_estimates', 'risks_constraints_dependencies']
    for key in required_keys:
        if key not in parsed_proposal:
            parsed_proposal[key] = proposal_content.get(key, "Not provided")

    return parsed_proposal
