"""Central intent router and agent orchestrator."""
from __future__ import annotations
import logging
from .agents import AGENTS
from .memory import MemoryStore
from .providers import ModelProvider

log = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, provider: ModelProvider, memory: MemoryStore):
        self.provider, self.memory = provider, memory

    @staticmethod
    def route(task: str) -> str:
        text = task.casefold()
        routes = [
            ("cybersecurity", ("security", "vulnerability", "cyber", "incident response", "threat")),
            ("kali", ("kali", "ssh vm")),
            ("windows", ("windows", "powershell", "registry")),
            ("developer", ("code", "python", "program", "software", "bug", "test")),
            ("research", ("research", "find sources", "latest", "web")),
            ("knowledge", ("remember", "knowledge base", "what did i save")),
        ]
        for agent, terms in routes:
            if any(term in text for term in terms):
                return agent
        return "research"

    def handle(self, task: str) -> str:
        key = self.route(task)
        agent = AGENTS[key]
        context = self.memory.search(task, limit=3)
        prompt = task
        if context:
            prompt += "\n\nRelevant saved knowledge:\n" + "\n".join(f"{title}: {content}" for title, content in context)
        try:
            answer = self.provider.generate(prompt, system=agent.system_prompt)
        except Exception:
            log.exception("Model provider request failed")
            answer = "The configured model provider failed. Check its availability and application logs."
        self.memory.add_message("user", task)
        self.memory.add_message("assistant", answer)
        return answer
