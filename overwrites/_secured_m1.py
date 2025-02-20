import warnings
import sys
from typing import Awaitable, Callable, List, Optional, Union

from autogen_agentchat.agents import CodeExecutorAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.base import ChatAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient

from autogen_ext.agents.file_surfer import FileSurfer
from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.openai._openai_client import BaseOpenAIChatCompletionClient
from autogen_agentchat.teams._group_chat._magentic_one._magentic_one_orchestrator import MagenticOneOrchestrator

SyncInputFunc = Callable[[str], str]
AsyncInputFunc = Callable[[str, Optional[CancellationToken]], Awaitable[str]]
InputFuncType = Union[SyncInputFunc, AsyncInputFunc]

from ._secured_file_surfer import SecuredFileSurfer
from ._secured_m1_orchestrator import SecuredMagenticOneOrchestrator


class MagenticOne(MagenticOneGroupChat):
    def __init__(
        self,
        client: ChatCompletionClient,
        input_func: InputFuncType | None = None,
        code_executor: CodeExecutorAgent = DockerCommandLineCodeExecutor(),
        enable_human_oversight: bool = False,
        enable_file_security: bool = False,
        enable_terminate: bool = False,
    ):
        self._enable_human_oversight = enable_human_oversight
        self.client = client
        self._validate_client_capabilities(client)
        
        coder = MagenticOneCoderAgent("Coder", model_client=client)
        ws = MultimodalWebSurfer("WebSurfer", model_client=client)
        executor = CodeExecutorAgent("Executor", code_executor=code_executor)

        if not enable_file_security:
            fs = FileSurfer("FileSurfer", model_client=client)
        else:
            fs = SecuredFileSurfer("FileSurfer", model_client=client)
        
        agents: List[ChatAgent] = [fs, ws, coder, executor]
        
        if enable_human_oversight:
            user_proxy_code_approver = UserProxyAgent("UserCodeApprover", input_func=input_func, description="A human code approver, who is asked to review and approve code before it is run")
            user_proxy_file_browser = UserProxyAgent("UserFileApprover", input_func=input_func, description="A human file approver, who will approve local file handling requests, before FileSurfer")
            user_proxy_web_browser = UserProxyAgent("UserWebApprover", input_func=input_func, description="A human web request approver, who will approve web browsing requests, before WebSurfer")
            user_proxy = UserProxyAgent("UserGeneral", input_func=input_func, description="A human user, who will assist with the task where there are doubts or the task is completed")
            agents.append(user_proxy_code_approver)
            agents.append(user_proxy_file_browser)
            agents.append(user_proxy_web_browser)
            agents.append(user_proxy)

        if enable_terminate:
            termination_condition = TextMentionTermination(text="TERMINATE")
        else:
            termination_condition = None

        super().__init__(agents, model_client=client, termination_condition=termination_condition)
        
        if enable_human_oversight:
            self._base_group_chat_manager_class = SecuredMagenticOneOrchestrator
            self._max_turns = 30

    def _validate_client_capabilities(self, client: ChatCompletionClient) -> None:
        capabilities = client.model_info
        required_capabilities = ["vision", "function_calling", "json_output"]

        if not all(capabilities.get(cap) for cap in required_capabilities):
            warnings.warn(
                "Client capabilities for MagenticOne must include vision, " "function calling, and json output.",
                stacklevel=2,
            )

        if not isinstance(client, BaseOpenAIChatCompletionClient):
            warnings.warn(
                "MagenticOne performs best with OpenAI GPT-4o model either " "through OpenAI or Azure OpenAI.",
                stacklevel=2,
            )

    def _create_group_chat_manager_factory(
        self,
        group_topic_type: str,
        output_topic_type: str,
        participant_topic_types,
        participant_descriptions,
        termination_condition,
        max_turns: int | None,
    ):
        if self._enable_human_oversight:
            return lambda: SecuredMagenticOneOrchestrator(
                group_topic_type,
                output_topic_type,
                participant_topic_types,
                participant_descriptions,
                max_turns,
                self._model_client,
                self._max_stalls,
                self._final_answer_prompt,
                termination_condition,
            )
        else:
            return lambda: MagenticOneOrchestrator(
                group_topic_type,
                output_topic_type,
                participant_topic_types,
                participant_descriptions,
                max_turns,
                self._model_client,
                self._max_stalls,
                self._final_answer_prompt,
                termination_condition,
            )