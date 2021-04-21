from gevent import monkey
monkey.patch_all()

import cgi
from flask import Flask, render_template, request
from flask_socketio import SocketIO

import argparse
from pythonosc import udp_client

app = Flask(__name__)
socketio = SocketIO(app)
client = None


@app.route("/")
def main():
    return app.send_static_file("index.html")


@socketio.on("connect", namespace="/ws")
def ws_conn():
    print("Connected")
    socketio.emit("state", ["ready"], namespace="/ws")


@socketio.on("disconnect", namespace="/ws")
def ws_disconn():
    print("Disconnected")

@socketio.on("sustain", namespace="/ws")
def ws_sustain(message):
    print(f"Received {message}")
    client.send_message("/sustain", bool(message.get("pressed")))
    socketio.emit("state", [message.get("next_state", "error")], namespace="/ws")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005,
        help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

    try:
        socketio.run(app, "0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Stopping")
        socketio.emit("state", ["stopped"], namespace="/ws")