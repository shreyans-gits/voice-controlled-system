from groq import Groq
import config

class Brain:
    def __init__(self,system_prompt_addition=""):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.AI_MODEL
        self.conversation_history = []

        # This is NOVA's personality
        self.system_prompt = f"""
        You are {config.ASSISTANT_NAME}, a smart, helpful, and witty AI desktop assistant.
        You are talking to {config.USER_NAME}.
        Keep responses concise and conversational — you are being spoken aloud.
        No bullet points or markdown. Just natural sentences.
        {f"Known facts about the user from past sessions: {system_prompt_addition}" if system_prompt_addition else ""}
        """

        # memory_data = Memory().load()
        # self.system_prompt = f"You are NOVA, a helpful AI assistant. Known facts about user: {memory_data}"

    def get_intent(self,query):
        try:
            intent_prompt = f"""
            You are an intent classifier. Classify the following query into exactly one of these intents:
            WEATHER, BATTERY, CPU, RAM, SEARCH, WATCH, WIKIPEDIA, NEWS, REMINDER, 
            WHATSAPP, SPOTIFY_PLAY, SPOTIFY_PAUSE, SPOTIFY_SKIP, POMODORO, 
            SUMMARIZE, FLASHCARD, CONVERSATION, SCREEN_READ, SCREEN_EXPLAIN, SCREEN_SUMMARIZE, APP_OPEN, 
            CLIPBOARD_EXPLAIN, CLIPBOARD_TRANSLATE,
            VOLUME_UP, VOLUME_DOWN, BRIGHTNESS_SET

            Rules:
            - Reply with just the intent word, nothing else
            - No punctuation, no explanation
            - If unsure, return CONVERSATION

            Query: {query}
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": intent_prompt}
                ],
                temperature=0, 
                max_tokens=10 
            )
            intent = response.choices[0].message.content.strip().upper()
            print(f"--- Intent Detected: {intent} ---")
            return intent
        
        except Exception as e:
            print(f"Intent Error: {e}")
            return "CONVERSATION"
        
    def extract_subject(self, query, intent):
        try:
            extract_prompt = f"""
            Extract only the search subject from this query. 
            Return just the subject, nothing else, no punctuation.

            Examples:
            'I want to watch some game videos' -> 'game videos'
            'search images of India' -> 'images of India'
            'learn about Indian history' -> 'Indian history'
            'put on some Drake' -> 'Drake'

            Query: {query}
            Intent: {intent}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": extract_prompt}
                ],
                temperature=0,
                max_tokens=20
            )

            subject = response.choices[0].message.content.strip()
            
            print(f"--- Subject Extracted: {subject} ---")
            
            return subject

        except Exception as e:
            print(f"Extraction Error: {e}")
            return query
        
    def extract_number(self, query, intent):
        try:
            extract_prompt = f"""
            Extract only the number out of the query.
            Return just the subject, nothing else, no punctuation.

            Examples:
            'Increase the volume by 10' -> '10'
            'Decrease the brighteness by 20' -> '20'

            Query: {query}
            Intent: {intent}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": extract_prompt}
                ],
                temperature=0,
                max_tokens=20
            )

            subject = response.choices[0].message.content.strip()
            
            print(f"--- Value Extracted: {subject} ---")
            
            return int(subject)

        except Exception as e:
            print(f"Extraction Error: {e}")
            return None

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

        # Add reply to history so NOVA remembers context
        self.conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    def clear_memory(self):
        self.conversation_history = []

    def summarize(self, session_log, old_summary):
        prompt = f"""
        You are an expert at condensing information. 
        Below is a chat log between an AI (NOVA) and Shreyans, and an old summary of Shreyans.
        
        OLD SUMMARY: {old_summary}
        NEW LOG: {session_log}
        
        Task: Extract key facts about Shreyans (preferences, interests, recent activities, or school updates).
        Merge them with the old summary into a single, cohesive, bullet-pointed paragraph. 
        Keep it under 150 words. Focus on facts that would help NOVA be a better assistant.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def summary(self,text):
        prompt = f"""
        You are an expert at condensing information. 
        Below is one or 2 paragraphs of information
        
        Information : {text}
        
        Task: Extract key facts from these and give a short summary
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content