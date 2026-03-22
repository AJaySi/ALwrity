import os
import configparser
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize session state variables if not already done
if 'progress' not in st.session_state:
    st.session_state.progress = 0


def create_agents(search_keywords):
    """Create agents for content creation."""
    try:
        from crewai import Agent
        from crewai_tools import SerperDevTool
    except ImportError:
        raise ImportError("The 'crewai' and/or 'crewai_tools' package is not installed. Please install them to use AI Agents Crew Writer features.")
    search_tool = SerperDevTool()
    google_api_key = os.getenv("GEMINI_API_KEY")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", verbose=True, temperature=0.6, google_api_key=google_api_key
    )

    try:
        role, goal, backstory = read_config("content_researcher")
        content_researcher = Agent(
            role=role, goal=goal, backstory=backstory, tools=[search_tool], memory=True, 
            verbose=True, max_rpm=None, max_iter=10, allow_delegation=False, llm=llm
        )

        role, goal, backstory = read_config("content_outliner")
        content_outliner = Agent(
            role=role, goal=goal, backstory=backstory, memory=True, 
            verbose=True, tools=[search_tool], max_rpm=10, max_iter=10, allow_delegation=False, llm=llm
        )

        role, goal, backstory = read_config("content_writer")
        content_writer = Agent(
            role=role, goal=goal, backstory=backstory, memory=True, 
            verbose=True, max_rpm=10, max_iter=15, allow_delegation=False, llm=llm
        )

        role, goal, backstory = read_config("content_reviewer")
        content_reviewer = Agent(
            role=role, goal=goal, backstory=backstory, memory=True, 
            verbose=True, max_rpm=10, max_iter=10, allow_delegation=False, llm=llm
        )

    except Exception as err:
        st.error(f"Error creating agents: {err}")
        st.stop()

    return [content_researcher, content_outliner, content_writer, content_reviewer]

def create_tasks(agents, search_keywords):
    """Create tasks for the agents."""
    try:
        from crewai import Task
    except ImportError:
        raise ImportError("The 'crewai' package is not installed. Please install it to use AI Agents Crew Writer features.")
    try:
        task_description, expected_output = read_config("research_task")
        research_task = Task(
            description=f"The main focus keywords are: '{search_keywords}'.\n{task_description}.",
            expected_output=expected_output,
            agent=agents[0]
        )

        task_description, expected_output = read_config("outline_task")
        outline_task = Task(
            description=f"{task_description}.\nThe main focus keywords are {search_keywords}",
            expected_output=expected_output,
            agent=agents[1]
        )

        task_description, expected_output = read_config("writer_task")
        writer_task = Task(
            description=f"{task_description}\nThe main focus keywords are {search_keywords}.",
            expected_output=expected_output,
            agent=agents[2]
        )

        task_description, expected_output = read_config("review_task")
        proofread_task = Task(
            description=f"{task_description}.\nThe main focus keywords are: {search_keywords}.",
            expected_output=expected_output,
            agent=agents[3]
        )

    except Exception as err:
        st.error(f"Error creating tasks: {err}")
        st.stop()

    return [research_task, outline_task, writer_task, proofread_task]

def execute_tasks(agents, tasks, lang):
    """Execute tasks with the agents."""
    try:
        from crewai import Crew
    except ImportError:
        raise ImportError("The 'crewai' package is not installed. Please install it to use AI Agents Crew Writer features.")
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
        language=lang
    )
    try:
        result = crew.kickoff()
    except Exception as err:
        st.error(f"Error executing tasks: {err}")
        st.stop()
    return result

def read_config(which_member):
    """Reads configuration for the specified agent or task."""
    team_dir = os.path.join(os.getcwd(), "lib", "workspace", "my_content_team")
    config_file = None
    
    if 'content_researcher' in which_member or 'research_task' in which_member:
        config_file = os.path.join(team_dir, "content_researcher.txt")
    elif 'content_writer' in which_member or 'writer_task' in which_member:
        config_file = os.path.join(team_dir, "content_writer.txt")
    elif 'content_reviewer' in which_member or 'review_task' in which_member:
        config_file = os.path.join(team_dir, "content_reviewer.txt")
    elif 'content_outliner' in which_member or 'outline_task' in which_member:
        config_file = os.path.join(team_dir, "content_outliner.txt")

    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        role = config.get('main', 'role')
        goal = config.get('main', 'goal')
        backstory = config.get('backstory', 'text')
    except Exception as err:
        st.error(f"Error reading config: {err}")
        st.stop()

    if 'task' not in which_member:
        return role, goal, backstory
    else:
        try:
            task_description = config.get('task', 'task_description')
            expected_output = config.get('task', 'task_expected_output')
        except Exception as err:
            st.error(f"Error reading task config: {err}")
            st.stop()
        return task_description, expected_output


def ai_agents_writers(search_keywords, lang="en"):
    """Main function to kickoff AI Agents content team."""

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    st.session_state.progress = 0
    status_text.text("Setting up environment...")
    status_text.text("Creating Agents team...")
    try:
        agents = create_agents(search_keywords)
        st.session_state.progress += 10
        progress_bar.progress(st.session_state.progress)
    except Exception as err:
        st.error(f"Failed in creating Agents team: {err}")
        st.stop()

    status_text.text("Creating tasks for Agents team...")
    try:
        tasks = create_tasks(agents, search_keywords)
        st.session_state.progress += 25
        progress_bar.progress(st.session_state.progress)
    except Exception as err:
        st.error(f"Failed in creating tasks for Agents team: {err}")
        st.stop()

    status_text.text("AI Agents busy writing your content...")
    try:
        result = execute_tasks(agents, tasks, lang)
        st.session_state.progress += 60
        progress_bar.progress(st.session_state.progress)
        status_text.text("Tasks executed successfully.")
        st.success("Successfully executed tasks.")
        
        # Display result with an option to copy the content
        st.markdown("### Result")
        st.code(result, language='markdown')
        st.download_button('Download Content', data=result, file_name='alwrity_result.md')
    except Exception as err:
        st.error(f"Failed to execute tasks: {err}")

