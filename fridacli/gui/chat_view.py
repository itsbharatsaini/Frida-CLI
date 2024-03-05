from textual.app import ComposeResult
from textual.containers import VerticalScroll, Vertical
from textual.events import Mount
from textual.widgets import Static, Input, Label, MarkdownViewer
from .chat_responses.system_response import SystemUserResponse, SystemFridaResponse
from fridacli.chatbot import ChatbotAgent

text = """
# Fibonacci Sequence in Python

The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones, usually starting with 0 and 1.

## Recursive Approach

```python
def fibonacci_recursive(n):
    if n <= 1:
        return n
    else:
        return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)
```
"""


class ChatView(Static):
    input_text = ""
    agent_chatbot = ChatbotAgent()

    def compose(self) -> ComposeResult:
        with Vertical():
            with VerticalScroll(id="chat_scroll"):
                pass
            yield Input(id="input_chat")

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        # self.input_text = message.value
        pass

    async def on_input_submitted(self):
        """
        Get and decorate the response given the user input
        """
        user_input = self.query_one("#input_chat", Input).value
        self.query_one("#chat_scroll", VerticalScroll).mount(
            SystemUserResponse(user_input)
        )
        self.query_one("#input_chat", Input).clear()

        response = self.agent_chatbot.chat(user_input, True)

        self.query_one("#chat_scroll", VerticalScroll).mount(SystemFridaResponse(response))
        self.query_one("#chat_scroll", VerticalScroll).scroll_down(animate=True)

    def _on_mount(self, event: Mount):
        pass
