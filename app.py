import datetime
import os
from pathlib import Path
from urllib.request import getproxies

import pytz
from dotenv import load_dotenv
from smolagents import CodeAgent, GradioUI, OpenAIServerModel, tool

from tools.final_answer import FinalAnswerTool

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_custom_tool(arg1:str, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that does nothing yet 
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    return "What magic will you build ?"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


def configure_local_proxy_bypass() -> None:
    """Connect directly to Gradio on localhost while retaining outbound proxies."""
    # On macOS, setting NO_PROXY alone can hide system proxy discovery.
    # Preserve the effective HTTP(S)/ALL proxies before adding local exceptions.
    proxies = getproxies()
    for scheme in ("http", "https", "all"):
        if proxies.get(scheme):
            os.environ.setdefault(f"{scheme}_proxy", proxies[scheme])

    bypass_hosts = ["127.0.0.1", "localhost", "::1"]
    for name in ("NO_PROXY", "no_proxy"):
        bypass_hosts.extend(
            host.strip() for host in os.getenv(name, "").split(",") if host.strip()
        )
    bypass = ",".join(dict.fromkeys(bypass_hosts))
    os.environ["NO_PROXY"] = bypass
    os.environ["no_proxy"] = bypass


def create_agent() -> CodeAgent:
    # Environment variables take precedence over the local .env file.
    load_dotenv(Path(__file__).with_name(".env"))
    configure_local_proxy_bypass()
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "请设置 DEEPSEEK_API_KEY：复制 .env.example 为 .env，"
            "填入你的 DeepSeek API Key，或在运行环境中设置该变量。"
        )

    model = OpenAIServerModel(
        model_id=os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
        api_base="https://api.deepseek.com",
        api_key=api_key,
        flatten_messages_as_text=True,
        temperature=0.1,
        max_tokens=2048,
        # CodeAgent uses generated Python code as actions. Non-thinking mode
        # lets the older adapter exchange ordinary chat messages throughout.
        extra_body={"thinking": {"type": "disabled"}},
        client_kwargs={"timeout": 120.0},
    )

    # Use prompts bundled with smolagents 1.13.0: the course's prompts.yaml
    # predates the final_answer fallback required by this version.
    return CodeAgent(
        model=model,
        tools=[FinalAnswerTool(), get_current_time_in_timezone],
        max_steps=6,
        verbosity_level=1,
    )


if __name__ == "__main__":
    GradioUI(create_agent()).launch(share=False, server_name="127.0.0.1")
