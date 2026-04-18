# core/brain.py

from groq import Groq
import config

class Brain:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.AI_MODEL
        self.conversation_history = []

        # This is Jarvis's personality
        self.system_prompt = f"""
        You are {config.ASSISTANT_NAME}, a smart, helpful, and witty AI desktop assistant.
        You are talking to {config.USER_NAME}.
        Keep responses concise and conversational — you are being spoken aloud.
        No bullet points or markdown. Just natural sentences.
        """

    def ask(self, user_input):
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Send to Groq
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ]
        )

        # Extract reply
        reply = response.choices[0].message.content

        # Add reply to history so Jarvis remembers context
        self.conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    def clear_memory(self):
        self.conversation_history = []