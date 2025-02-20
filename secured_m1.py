import os
import argparse
import asyncio
import warnings
from typing import Optional
from dotenv import load_dotenv

from autogen_agentchat.ui import Console, UserInputManager
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.ui import RichConsole

from overwrites._secured_m1 import MagenticOne

# Suppress warnings about the requests.Session() not being closed
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
warnings.filterwarnings(action="ignore", message=".*model mismatch.*", category=UserWarning)

load_dotenv()

async def cancellable_input(prompt: str, cancellation_token: Optional[CancellationToken]) -> str:
    task: asyncio.Task[str] = asyncio.create_task(asyncio.to_thread(input, prompt))
    if cancellation_token is not None:
        cancellation_token.link_future(task)
    return await task


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run a complex task using MagenticOne in fully secured mode.\n\n"
            "For more information, refer to the following paper: https://arxiv.org/abs/2411.04468"
        )
    )
    parser.add_argument("task", type=str, nargs=1, help="The task to be executed by MagenticOne.")
    parser.add_argument("--secure", action="store_true", help="Enable all following security features.", default=False)
    parser.add_argument("--enable-human-oversight", action="store_true", help="Enable human oversight for code execution, web browsing, and file handling.", default=False)
    parser.add_argument("--enable-file-security", action="store_true", help="Enable file security mode, where user must approve file handling requests.", default=False)
    parser.add_argument("--enable-terminate", action="store_true", help="Enable terminate mode, when user provides 'TERMINATE' command, the program will terminate.", default=False)
    parser.add_argument("--rich", action="store_true", help="Enable rich console output", default=True)
    args = parser.parse_args()

    async def run_task(task: str, use_rich_console: bool, enable_human_oversight: bool, enable_file_security: bool, enable_terminate: bool) -> None:
        input_manager = UserInputManager(callback=cancellable_input)
        client = AzureOpenAIChatCompletionClient(azure_deployment="gpt-4o", model="gpt-4o")
        async with DockerCommandLineCodeExecutor(work_dir=os.getcwd()) as code_executor:
            m1 = MagenticOne(client=client,
                             input_func=input_manager.get_wrapped_callback(),
                             code_executor=code_executor,
                             enable_human_oversight=enable_human_oversight,
                             enable_file_security=enable_file_security,
                             enable_terminate=enable_terminate
                )

            if use_rich_console:
                await RichConsole(m1.run_stream(task=task), output_stats=False, user_input_manager=input_manager)
            else:
                await Console(m1.run_stream(task=task), output_stats=False, user_input_manager=input_manager)
            
            await code_executor.stop()

    task = args.task[0]
    if args.secure:
        asyncio.run(run_task(task, args.rich, True, True, True))
    asyncio.run(run_task(task, args.rich, args.enable_human_oversight, args.enable_file_security, args.enable_terminate))


if __name__ == "__main__":
    main()
