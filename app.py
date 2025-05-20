import gradio as gr
import openai
import time
import datetime
import os

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
OPENAI_MODEL = "gpt-4"

SYSTEM_PROMPT = """
You are an intelligent, friendly Software Engineering expert. Help users understand and apply concepts from SDLC, Agile, OOP, UML, Git, Clean Code, Testing, and more. Give structured, concise answers with examples and code snippets when needed. Use Markdown and code formatting where appropriate.
"""

# Initial message memory
chat_history = []

# Example prompts
example_prompts = [
    "Explain the phases of the Software Development Life Cycle (SDLC).",
    "What are SOLID principles in OOP?",
    "Give an example of a Factory Design Pattern in Python.",
    "How does Git branching work in a team environment?",
    "What is unit testing and why is it important?"
]

# Main chatbot function
def chatbot_interface(user_input, topic):
    if not user_input:
        return chat_history, "Please enter a question."

    user_message = {"role": "user", "content": f"[Topic: {topic}] {user_input}"}
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history + [user_message]

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7
        )
        bot_response = response.choices[0].message.content
    except Exception as e:
        bot_response = f"Error: {str(e)}"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history.append(user_message)
    chat_history.append({"role": "assistant", "content": bot_response})
    return chat_history, ""

# Clear chat
def clear_history():
    global chat_history
    chat_history = []
    return [], ""

# Download chat
def download_chat():
    chat_text = "\n".join([
        f"User: {m['content']}" if m["role"] == "user" else f"Bot: {m['content']}"
        for m in chat_history
    ])
    filename = f"chat_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(chat_text)
    return filename

# Gradio UI
topics = ["General", "SDLC", "Agile", "Design Patterns", "UML", "Git", "SOLID Principles", "Testing & QA"]

def render_chat():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 💬 Software Engineering Chatbot
        Welcome to your expert assistant for all things Software Engineering! Select a topic and ask anything.
        """)

        with gr.Row():
            topic_dropdown = gr.Dropdown(choices=topics, label="Select Topic", value="General")

        chatbot = gr.Chatbot(height=400)
        input_box = gr.Textbox(label="Your question...", placeholder="Ask about SDLC, OOP, Git, etc.", lines=2)
        submit_btn = gr.Button("Send")
        clear_btn = gr.Button("Clear Chat")
        download_btn = gr.Button("📥 Download Chat")
        example_box = gr.Examples(example_prompts, inputs=input_box)
        error_box = gr.Textbox(visible=False)

        def on_submit(user_input, topic):
            result, error = chatbot_interface(user_input, topic)
            formatted = [(m['content'], None) if m['role'] == 'user' else (None, m['content']) for m in result]
            return formatted, ""

        submit_btn.click(on_submit, inputs=[input_box, topic_dropdown], outputs=[chatbot, error_box])
        clear_btn.click(clear_history, outputs=[chatbot, error_box])
        download_btn.click(fn=download_chat, outputs=[], show_progress=False)

    return demo

# Run app
if __name__ == "__main__":
    demo = render_chat()
    demo.launch()
