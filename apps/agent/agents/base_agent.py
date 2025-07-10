# apps/agent/agents/base_agent.py

import time
from abc import ABC, abstractmethod
from typing import Any, Dict
from apps.agent.models import AgentExecutionLog


class BaseAgent(ABC):
    """
    Base class for all internal agents. Handles execution logging and timing.
    """

    def __init__(self):
        self.log_instance = None

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        self.log_instance = AgentExecutionLog.objects.create(
            agent_name=self.name(),
            input_data=input_data,
        )

        try:
            result = self.execute(input_data)
            duration = time.time() - start_time
            self.log_instance.output_data = result
            self.log_instance.duration = duration
            self.log_instance.success = True
            self.log_instance.save()
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.log_instance.success = False
            self.log_instance.error_message = str(e)
            self.log_instance.duration = duration
            self.log_instance.save()
            raise

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core logic of the agent. Subclasses must implement this.
        """
        pass

    def name(self) -> str:
        return self.__class__.__name__

    def log_event(self, message: str, metadata: Dict[str, Any] = None):
        """
        Log a custom event during agent execution.
        """
        if self.log_instance:
            self.log_instance.logs.create(message=message, metadata=metadata or {})
