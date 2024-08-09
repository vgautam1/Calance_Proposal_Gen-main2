import logging
from langchain.agents import create_react_agent, Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import PromptTemplate

def refine_search_query(user_input, additional_info, llm):
    prompt = f"""
    Analyze the following content and derive the best search string to best research what is expressed in this statement:
    "Based on: {user_input}; Additional_info: {additional_info}"
    """
    response = llm.invoke(prompt)
    refined_query = response.strip()
    return refined_query

def perform_research(user_input, additional_info, llm):
    try:
        refined_query = refine_search_query(user_input, additional_info, llm)
        search = DuckDuckGoSearchRun()
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events"
            )
        ]
        prompt_template = PromptTemplate(
            input_variables=["user_input", "additional_info", "tools", "tool_names", "agent_scratchpad"],
            template="""
            Based on: {user_input} and additional info: {additional_info}
            
            You have access to the following tools:
            {tool_names}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of {tool_names}
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            {agent_scratchpad}
            """
        )
        agent = create_react_agent(tools, llm, prompt=prompt_template)
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        research_result = agent_executor.run(refined_query)
        return {"status": "success", "data": research_result}
    except Exception as e:
        logging.error(f"Research error: {str(e)}")
        return {"status": "error", "message": f"Unable to complete research due to an error: {str(e)}"}
