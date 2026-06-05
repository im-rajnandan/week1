# Week 1 Submission

I built a simple terminal-based chatbot using OpenRouter with the OpenAI-compatible Python SDK.

The main file for my implementation is:

```text
chatbot.py
```

I kept the project simple as the main goal of this week was to understand the basic LLM API call properly. The chatbot runs in the terminal, takes user input, sends it to a model, prints the model response, and keeps enough conversation history so that it can answer based on earlier messages.

The chatbot currently supports:

```text
- terminal input/output
- OpenRouter API calls
- model selection before starting
- multi-turn conversation memory
- a ChatAgent class
- a rolling buffer for recent turns
- /reset command
- /tokens command
- exit / quit command
```

---

## How I approached it

I first started with: take one input, send it to the model, and print the reply.

After that, I converted it into a loop so that I could keep chatting with the model. But then I realized that simply calling the API again and again is not enough for a real conversation. The model does not automatically remember previous calls.

That was the main thing I learnt from this task: the API is stateless.

The chatbot only remembers earlier messages because my code stores them and sends them again in the next API call.

So the most important part of the project became the `messages` list.

At the start, the list contains the system message:

```python
self.messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]
```

Whenever the user types something, I append it as a user message:

```python
self.messages.append({
    "role": "user",
    "content": text
})
```

Then I send the full message list to the model:

```python
response = client.chat.completions.create(
    model=self.model,
    messages=self.messages,
)
```

After the model replies, I also append the assistant's reply:

```python
self.messages.append({
    "role": "assistant",
    "content": answer
})
```

So the conversation memory is not inside OpenRouter or inside the model. The memory is inside my Python program.

---

## ChatAgent class

I made a simple `ChatAgent` class to keep the chatbot logic in one place.

The class stores:

```text
- the model name
- the messages list
- maximum number of turns to keep
- last token usage
```

The main method is `ask()`.

Its flow is:

```text
1. Add the user's message to self.messages
2. Send the full self.messages list to the model
3. Extract the assistant's answer
4. Add the assistant's answer back to self.messages
5. Trim old messages if the history becomes too long
6. Return the answer
```

This helped me understand that a chatbot is basically a loop around API calls with some state management added around it.

---

## API key safety

I did not put the API key directly inside the Python file.

Instead, I stored it in a local `.env` file:

```text
OPENROUTER_API_KEY=...
```

Then I loaded it in Python using:

```python
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
```

I also added `.env` to `.gitignore`.

This was an important part of the assignment because API keys should not be pushed to GitHub. I understood that even for a small assignment, the key should be treated like a password.

---

## Model selection

I added a small model selection step before the chat starts.

The chatbot asks the user to choose between:

```text
1. openrouter/free
2. enter custom model
```

Initially, I tried using the model mentioned in the README:

```text
deepseek/deepseek-v4-flash:free
```

But while running the code, I got an error saying:

```text
No endpoints found for deepseek/deepseek-v4-flash:free
```

So I changed the default model to:

```text
openrouter/free
```

This was one practical thing I discovered while testing: model availability can change. Because of that, it is better to allow model selection instead of hardcoding only one model forever.

I also kept the option to enter a custom model manually, so the chatbot is not tied to only one model.

---

## Conversation memory test

To check whether memory was working, I tested the chatbot like this:

```text
User: my name is nemoultra
Assistant: Hello, nemoultra...

User: what is my name?
Assistant: Your name is nemoultra...
```

This showed that the chatbot was able to use earlier messages.

But the important point is that it remembered only because the first message was still present inside `self.messages`.

Then I tested the `/reset` command.

After `/reset`, the message list goes back to only the system prompt. So when I ask my name again, the model should not know it anymore.

```text
If I keep the messages, the model seems to remember.
If I remove the messages, the model forgets.
```

---

## Rolling buffer

I also added a simple rolling buffer.

Without a rolling buffer, the `messages` list keeps growing forever. That means every new API call sends all old messages again.

This can cause:

```text
- more token usage
- slower responses
- context length problems
- unnecessary old messages being sent repeatedly
```

So I used `max_turns`.

In my code, one turn means:

```text
one user message + one assistant message
```

That is why the maximum number of messages is:

```python
max_messages = 1 + 2 * self.max_turns
```

The `1` is for the system message.

The `2 * self.max_turns` is for the recent user-assistant pairs.

If the message list becomes too long, I keep the system message and only the most recent turns.

This is a simple approach, but it is enough to show the idea that context is not free.

---

## Commands implemented

I implemented these commands:

```text
exit
quit
```

These stop the chatbot.

```text
/reset
```

This clears the conversation memory and starts again with only the system prompt.

```text
/tokens
```

This prints the token usage from the last API call.

The `/tokens` command helped me see that both the input history and the model output use tokens. So if I keep too much history, every call becomes heavier.

---

## Weird things I noticed while testing

While testing with `openrouter/free`, I noticed some strange outputs sometimes.

For example, at one point the model printed things like:

```text
User Safety: safe
Response Safety: safe
```

This was not coming from my code. It was part of the model response.

I think this happened because `openrouter/free` can route to different free models, so the behavior is not always exactly the same. Some models may expose weird safety-format text or behave differently.

I also noticed that when I asked the current year, the model sometimes said an older year. Then when I corrected it in the conversation, it used my correction later.

This helped me understand another thing: the model does not automatically know live real-world information unless it is provided in the current prompt or conversation.

To reduce the weird safety-label output, I improved the system prompt slightly and told the model to answer normally and not print labels like `User Safety` or `Response Safety`.

---

## What I learnt

The biggest learning from this week was that a basic chatbot is not magic. At the core, it is mostly:

```text
messages list + API call + loop
```

The model only sees what I send in the current request.

I also understood the roles better:

```text
system     -> instructions for the assistant
user       -> messages from the human
assistant  -> previous replies from the model
```

Before doing this, I thought conversation memory was something the model handled automatically. Now I understand that the conversation is represented as a structured list of role-tagged messages, and my code is responsible for maintaining it.

I also learnt why `.env` and `.gitignore` matter. They are not just setup details. They are part of writing safe code.

---

The main takeaway for me is:

```text
The LLM API is stateless.
The messages list is the chatbot's memory.
The program is responsible for managing that memory.
```

This feels like the foundation for building more advanced agents later, where the same idea will extend to tools, retrieval, summarization, and longer-term memory.
