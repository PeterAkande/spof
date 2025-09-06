"""
Simple Chatbot Prompt

A clean example of using SPOF to build structured chatbot prompts.
This demonstrates the core building blocks: personality, conversation context, and directions.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel
from spof.spof import InstructionBlock, ModelBlock, Text, Items, wrap_model


class ChatMessage(BaseModel):
    """Individual chat message with sender, timestamp, and content"""

    sender: Literal["User", "Assistant"]
    timestamp: datetime
    content: str

    __block_name__ = "chat_message"

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}


class PersonalityBlock(InstructionBlock):
    """Define the chatbot's personality and behavior"""

    name: str
    traits: List[str]
    communication_style: str

    def __init__(self):
        super().__init__(
            name="Alex",
            traits=[
                "Friendly and approachable",
                "Helpful and proactive",
                "Curious and engaging",
                "Professional but warm",
            ],
            communication_style="Conversational, clear, and empathetic. Use 'I' naturally when speaking.",
        )


class ConversationHistoryBlock(InstructionBlock):
    """Recent conversation messages for context"""

    messages: List[ChatMessage]
    total_messages: int

    def __init__(self, messages: List[ChatMessage]):
        super().__init__(
            messages=messages[-10:],  # Keep last 10 messages
            total_messages=len(messages),
        )


class DirectionsBlock(InstructionBlock):
    """Clear instructions for the chatbot"""

    primary_goals: List[str]
    response_guidelines: Items
    safety_rules: Items

    def __init__(self):
        super().__init__(
            primary_goals=[
                "Listen carefully to understand user needs",
                "Provide helpful, accurate information",
                "Ask clarifying questions when needed",
                "Maintain a friendly, professional tone",
            ],
            response_guidelines=Items(
                [
                    "Keep responses concise but thorough",
                    "Use examples when helpful",
                    "Acknowledge when you don't know something",
                    "Offer follow-up suggestions",
                ],
                block_name="guidelines",
            ),
            safety_rules=Items(
                [
                    "Never provide harmful or dangerous advice",
                    "Protect user privacy and data",
                    "Be respectful of all individuals and groups",
                    "Decline inappropriate requests politely",
                ],
                block_name="safety",
            ),
        )


class CurrentContextBlock(InstructionBlock):
    """Current conversation state and context"""

    timestamp: str
    user_message: str
    session_info: str

    def __init__(self, user_message: str):
        super().__init__(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_message=user_message,
            session_info="New conversation session",
        )


class ChatbotPrompt(InstructionBlock):
    """Complete chatbot prompt structure"""

    introduction: Text
    personality: PersonalityBlock
    directions: DirectionsBlock
    conversation_history: Optional[ConversationHistoryBlock]
    current_context: CurrentContextBlock
    final_instruction: Text

    def __init__(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
    ):
        super().__init__(
            introduction=Text(
                "You are Alex, a helpful AI assistant. Respond naturally and helpfully to user messages.",
                block_name="role",
            ),
            personality=PersonalityBlock(),
            directions=DirectionsBlock(),
            conversation_history=(
                ConversationHistoryBlock(conversation_history)
                if conversation_history
                else None
            ),
            current_context=CurrentContextBlock(user_message),
            final_instruction=Text(
                "Based on the user's message and conversation context, provide a helpful, "
                "friendly response that follows your personality and guidelines.",
                block_name="task",
            ),
        )


# Example usage
if __name__ == "__main__":
    # Create a simple chatbot prompt
    user_input = "Hi! Can you help me plan a weekend trip to Paris?"

    # Previous conversation context using structured ChatMessage models
    chat_history = [
        ChatMessage(
            sender="User",
            timestamp=datetime(2025, 9, 6, 14, 30, 0),
            content="Hello there!",
        ),
        ChatMessage(
            sender="Assistant",
            timestamp=datetime(2025, 9, 6, 14, 30, 5),
            content="Hi! I'm Alex, your helpful assistant. How can I help you today?",
        ),
        ChatMessage(
            sender="User",
            timestamp=datetime(2025, 9, 6, 14, 31, 0),
            content="I'm looking for travel advice",
        ),
        ChatMessage(
            sender="Assistant",
            timestamp=datetime(2025, 9, 6, 14, 31, 3),
            content="I'd love to help with travel planning! What destination are you considering?",
        ),
    ]

    # Build the prompt
    prompt = ChatbotPrompt(user_input, chat_history)

    # Render in different formats
    with open("chatbot.xml", "w") as f:
        f.write(prompt.to_xml())

    with open("chatbot.md", "w") as f:
        f.write(prompt.to_markdown())

    with open("chatbot.json", "w") as f:
        f.write(prompt.to_json())
