import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if api_key is None:
    print("OPENROUTER_API_KEY not found. Please check your .env file.")
    exit()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "Answer normally and naturally. "
    "Do not print safety labels, moderation labels, hidden metadata, "
    "or text like 'User Safety' or 'Response Safety'. "
    "The current year is 2026."
)


class ChatAgent:
    def __init__(self, model, max_turns=5):
        self.model = model
        self.max_turns = max_turns
        self.last_usage = None

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def ask(self, text):
        self.messages.append({
            "role": "user",
            "content": text
        })

        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )

        self.last_usage = response.usage

        answer = response.choices[0].message.content

        self.messages.append({
            "role": "assistant",
            "content": answer
        })

        self.keep_only_recent_messages()

        return answer

    def keep_only_recent_messages(self):
        # 1 system message + last max_turns user/assistant pairs
        max_messages = 1 + 2 * self.max_turns

        if len(self.messages) > max_messages:
            system_message = self.messages[0]
            recent_messages = self.messages[-2 * self.max_turns:]
            self.messages = [system_message] + recent_messages

    def reset(self):
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
        self.last_usage = None

    def print_tokens(self):
        if self.last_usage is None:
            print("No token usage yet.")
        else:
            print(self.last_usage)


print("Choose model:")
print("1. openrouter/free")
print("2. enter custom model")

choice = input("Enter choice: ").strip()

if choice == "2":
    model_name = input("Enter model name: ").strip()
    if model_name == "":
        model_name = "openrouter/free"
else:
    model_name = "openrouter/free"


bot = ChatAgent(model=model_name, max_turns=5)

print()
print("Chat started.")
print("Type exit or quit to stop.")
print("Type /reset to clear memory.")
print("Type /tokens to see token usage.")
print()

while True:
    user_input = input("[YOU] ").strip()

    if user_input == "":
        continue

    if user_input.lower() == "exit" or user_input.lower() == "quit":
        print("Goodbye!")
        break

    if user_input.lower() == "/reset":
        bot.reset()
        print("Memory cleared.")
        continue

    if user_input.lower() == "/tokens":
        bot.print_tokens()
        continue

    try:
        reply = bot.ask(user_input)
        print("[MODEL]", reply)
    except Exception as e:
        print("Something went wrong:")
        print(e)

        # remove the last user message if model call failed
        if len(bot.messages) > 1 and bot.messages[-1]["role"] == "user":
            bot.messages.pop()
