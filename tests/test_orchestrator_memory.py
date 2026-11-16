from ard_intelligence.agents import AGENTS
from ard_intelligence.memory import MemoryStore
from ard_intelligence.orchestrator import Orchestrator

class FakeProvider:
    def __init__(self): self.system = ""
    def generate(self, prompt, *, system=""):
        self.system = system
        return "ok"

def test_orchestrator_routes_and_persists(tmp_path):
    memory = MemoryStore(tmp_path / "memory.db")
    provider = FakeProvider()
    orchestrator = Orchestrator(provider, memory)
    assert orchestrator.route("Help me fix this Python bug") == "developer"
    assert orchestrator.handle("How can I research this topic?") == "ok"
    assert provider.system == AGENTS["research"].system_prompt
    assert memory.history() == [("user", "How can I research this topic?"), ("assistant", "ok")]

def test_knowledge_search(tmp_path):
    memory = MemoryStore(tmp_path / "memory.db")
    memory.add_knowledge("Deployment notes", "Use a staging review before deployment")
    assert memory.search("Deployment")[0][0] == "Deployment notes"
