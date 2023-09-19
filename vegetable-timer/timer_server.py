import random
from typing import Callable, Dict, Union
import zmq
from zmq import Socket
from enum import Enum, auto
from threading import Thread
from argparse import ArgumentParser
import time

import json

WIDTH = 35
PORTNUM_COMM = 23512
SOCKET_ADDRESS = f"ipc:///tmp/veggie_timer:{PORTNUM_COMM}"
context = zmq.Context()


class RequestMessages(str, Enum):
    PRESENCE_CHECK = 0
    SHUTDOWN = 1
    UPDATE = 2
    START_TIMER = 3
    CLEAR_TIMER = 4
    START_SERVER = 5


class ResponseMessages(str, Enum):
    SUCCESS = auto()
    ERROR = auto()


Handler = Callable[[RequestMessages], Union[ResponseMessages, str]]


class VegetableTimerServer:

    def __init__(self, default_timer_length=25*60, default_break_length=300) -> None:
        self.socket: Socket = context.socket(zmq.REP)
        self.shutdown_requested = False
        self.start_time = -1
        self.times_break = False
        self.break_ended = None

        self.timer_length = default_timer_length
        self.break_length = default_break_length

        self.handlers: Dict[RequestMessages, Handler] = {
            RequestMessages.PRESENCE_CHECK: lambda: ResponseMessages.SUCCESS,
            RequestMessages.SHUTDOWN: self.shutdown,
            RequestMessages.UPDATE: self.tick,
            RequestMessages.START_TIMER: self.start_timer,
            RequestMessages.CLEAR_TIMER: self.reset_timer
        }

    def start(self):
        self.socket.bind(SOCKET_ADDRESS)
        while not self.shutdown_requested:
            msg = self.socket.recv_string()
            try:
                print(f"[DEBUG] Received message on server: {msg}")
                resp = self.handlers[msg]()
                print(f"[DEBUG] Sending answer: {resp}")
                self.socket.send_string(resp)
            except KeyError as err:
                print(f"[WARN] Received unknown command message {msg}")

    def shutdown(self) -> ResponseMessages:
        self.shutdown_requested = True
        return ResponseMessages.SUCCESS

    def tick(self) -> str:
        if self.start_time < 0:  # no timer active
            return '{"text" : "' + 'Click to start timer'.center(WIDTH) + '"}'
        current_duration = self._get_current_duration()
        if current_duration > (self.timer_length + self.break_length):
            if self.break_ended is None:
                self.break_ended = int(time.time())
            resp = {
                "text": f"Break ended {(int(time.time())-self.break_ended) // 60} minutes ago.".center(WIDTH), "class": "done"}
            return json.dumps(resp)
        elif current_duration > self.timer_length:
            resp = self._format_to_waybar(
                current_duration-self.timer_length, self.break_length, title="Break: ")
            resp["class"] = "alert"
            return json.dumps(resp)
        else:
            return json.dumps(self._format_to_waybar(current_duration, self.timer_length))

    def _get_current_duration(self) -> int:
        return int(time.time()) - self.start_time

    def start_timer(self):
        if self.start_time > 0 and self._get_current_duration() <= self.timer_length:
            return ResponseMessages.ERROR
        self.break_ended = None
        self.start_time = int(time.time())
        return ResponseMessages.SUCCESS

    def reset_timer(self):
        self.start_time = -1
        self.break_ended = None
        return ResponseMessages.SUCCESS

    @staticmethod
    def start_new_server():
        server = VegetableTimerServer()
        server.start()
        server.socket.close()

    @staticmethod
    def _format_to_waybar(timer_secs: int, max_timer_secs: int, title: str = "") -> dict[str, str]:
        passed_str = f"{timer_secs // 60}min {timer_secs%60}s"
        total_str = f"{max_timer_secs // 60}min {max_timer_secs%60}s"
        return {"text": f"{title}{passed_str}/{total_str}".center(WIDTH),
                "class": f"{min(int(timer_secs/max_timer_secs*100),99)}"}

    @staticmethod
    def _is_server_up() -> bool:
        with context.socket(zmq.REQ) as socket:
            socket.connect(SOCKET_ADDRESS)
            socket.send_string(RequestMessages.PRESENCE_CHECK)
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            # fighting race cons one shitty non-deterministic hack at a time
            wait_noise = int(random.random() * 2000)
            poll_result = poller.poll(500+wait_noise)
            # if we heard something then the server is up
            is_up = len(poll_result) > 0
            if is_up:
                _ = socket.recv_string()
            return is_up

    @staticmethod
    def bring_up_if_down(max_retries=3):
        pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--request", choices=[m.value for m in RequestMessages], help="Choose appropriate number:" + ','.join(
        [f"{m.name}: {m.value}" for m in RequestMessages]), required=True)
    args = parser.parse_args()
    server_thread = None
    # check if we're the first ones and need to start the whole damn thing!
    is_up = VegetableTimerServer._is_server_up()
    if not is_up:
        if args.request == RequestMessages.START_SERVER:
            server_thread = Thread(
                None, VegetableTimerServer.start_new_server, args=[])
            print("[INFO] Starting new server...")
            server_thread.run()
        else:
            print('{ "text" : "Timer Server not started!"}')

    else:
        with context.socket(zmq.REQ) as socket:
            socket.connect(SOCKET_ADDRESS)
            socket.send_string(args.request)
            print(socket.recv_string())

    if server_thread is not None and server_thread.is_alive():
        server_thread.join()
