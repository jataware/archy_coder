import logging
from flask import Flask, render_template_string, request, jsonify
import flask.cli
import threading

from typing import Callable
from easyrepl import readl

# Disable Flask's default logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# really disable extra logging that they don't want you to disable lol: 
# https://github.com/cs01/gdbgui/issues/425#issuecomment-1086871191
# https://github.com/cs01/gdbgui/issues/425#issuecomment-1119836533
flask.cli.show_server_banner = lambda *args: None


app = Flask(__name__)

index_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat Assistant & Terminal</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <div id="chat_history" style="width: 50%; height: 300px; overflow-y: scroll; border: 1px solid black; padding: 10px;"></div>
    <input id="chat_input" type="text" style="width: 50%;">
    <button id="send_button">Send</button>

    <script>
        function appendMessage(message) {
            $("#chat_history").append("<p>" + message + "</p>");
            $("#chat_history").scrollTop($("#chat_history")[0].scrollHeight);
        }

        $("#send_button").click(function() {
            var message = $("#chat_input").val();
            $("#chat_input").val("");
            appendMessage("You: " + message);

            $.post("/send_message", {message: message}, function(data) {
                appendMessage("AI: " + data.response);
            });
        });

        $("#chat_input").keypress(function(e) {
            if (e.which === 13) {  // Enter key
                $("#send_button").click();
            }
        });
    </script>
</body>
</html>
'''


"""
def chat_callback(message:str) -> str:
    # Process a user's message and return the AI's response
"""
chat_callback = None

"""
def terminal_callback(command:str) -> None:
    # Execute command using os.system or subprocess
    # any output should be printed to the terminal
    # no value should be returned
"""
terminal_callback = None

def register_chat_callback(callback:Callable[[str], str]):
    global chat_callback
    chat_callback = callback

def register_terminal_callback(callback:Callable[[str], None]):
    global terminal_callback
    terminal_callback = callback


@app.route("/")
def index():
    return render_template_string(index_html)

@app.route("/send_message", methods=["POST"])
def send_message():
    message = request.form["message"]

    assert chat_callback is not None, "chat_callback must be registered before running the Flask app"

    response = chat_callback(message)

    # # Process the message and respond with the AI's response
    # response = "AI response goes here"  # Replace with actual AI response

    return jsonify({"response": response})

def command_input_loop():
    assert terminal_callback is not None, "terminal_callback must be registered before running the Flask app"
    while True:
        # command_input = input(">>> ")
        command_input = readl(prompt=">>> ")
        terminal_callback(command_input)
        # print(f"Executed: {command_input}")
        # # Execute command_input using os.system or subprocess
        # # ...


def run_dual_input():
    app_url = "http://127.0.0.1:5000"
    print(f"Chat Assistant at {app_url}")
    
    # start the thread with the terminal input
    command_input_thread = threading.Thread(target=command_input_loop, daemon=True)
    command_input_thread.start()

    # Set up the Flask app to run with minimal output
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
