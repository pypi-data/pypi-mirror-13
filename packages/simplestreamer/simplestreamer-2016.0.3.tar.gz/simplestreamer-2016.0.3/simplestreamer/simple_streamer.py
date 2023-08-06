import threading
import socket
import pickle
import time
import math


class SimpleStreamer:

    def __init__(self, port=5202, autostart=True):
        self.port = port
        self.clients = {}
        self.subscriptions = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.subscription_update_thread = threading.Thread(target=self._subscription_update_thread)
        self.data_receive_thread = threading.Thread(target=self._data_receive_thread)
        self._stop = False
        self.data = {}
        self.data_lock = threading.Lock()
        self.last_chunked_packet_id = 0
        if autostart:
            self.start()

    def start(self):
        self.data_receive_thread.start()
        self.subscription_update_thread.start()

    def _data_receive_thread(self):
        self.socket.bind(("0.0.0.0", self.port))
        buffer_pools = {}
        while not self._stop:
            str_dat, client_id = self.socket.recvfrom(4096)
            try:
                dict_data = pickle.loads(str_dat)
            except EOFError as e:
                print(e)
                continue

            # Chunked packet received
            if dict_data['type'] == "chunk":
                if client_id not in buffer_pools:
                    buffer_pools[client_id] = {"id": -1}
                if dict_data["id"] > buffer_pools[client_id]["id"]:
                    buffer_pools[client_id]["id"] = dict_data["id"]
                    buffer_pools[client_id]["chunks"] = {}
                    buffer_pools[client_id]["count"] = dict_data["count"]
                buffer_pools[client_id]["chunks"][dict_data["cid"]] = dict_data["data"]
                if len(buffer_pools[client_id]["chunks"]) >= buffer_pools[client_id]["count"]:
                    str_dat = b"".join(buffer_pools[client_id]["chunks"][i] for i in range(buffer_pools[client_id]["count"]))
                    try:
                        dict_data = pickle.loads(str_dat)
                    except EOFError as e:
                        print(e)
                        continue

            # Subscription update received
            if dict_data['type'] == "sub":
                dict_data = dict_data['data']

                if client_id not in self.clients:
                    self.clients[client_id] = {"last_send": 0}
                    print("new client: {}".format(client_id))
                dict_data['last_beat'] = time.time()
                self.clients[client_id].update(dict_data)

            # Data update received
            elif dict_data["type"] == "data":
                with self.data_lock:
                    self.data[dict_data["id"]] = dict_data["data"]

    def _subscription_update_thread(self):
        while not self._stop:
            for sub_id in self.subscriptions:
                data = {"type": "sub", "data": self.subscriptions[sub_id]}
                self.socket.sendto(pickle.dumps(data), sub_id)
            time.sleep(1.5)

    def subscribe(self, address, port, id, updates_per_sec=10):
        self.subscriptions[(address, port)] = {'id': id, 'ups': updates_per_sec}
        self.data[id] = {}

    def send_data(self, data):
        current_time = time.time()
        dead_clients = []
        for client_id in self.clients:
            if (current_time - self.clients[client_id]['last_beat']) > 2:
                dead_clients.append(client_id)
                continue
            if (current_time - self.clients[client_id]['last_send']) > 1/self.clients[client_id]['ups']:
                client_data = {"type": "data", "id": self.clients[client_id]['id'], 'data': data}
                self._send_dict(client_data, client_id)
                self.clients[client_id]['last_send'] = current_time
        for client_id in dead_clients:
            print("client lost: {}".format(client_id))
            del self.clients[client_id]

    def _send_dict(self, dict, addr_info):
        dict_pkl = pickle.dumps(dict)
        if len(dict_pkl) > 500:
            self.last_chunked_packet_id += 1
            pid = self.last_chunked_packet_id
            count = math.ceil(len(dict_pkl)/300)
            for i in range(count):
                chunk = {"type": "chunk", "id": pid, "cid": i, "count": count, "data": dict_pkl[i*300:(i+1)*300]}
                self._send_dict(chunk, addr_info)
        else:
            self.socket.sendto(dict_pkl, addr_info)

    def get_data(self, id=None):
        with self.data_lock:
            if id is None:
                return self.data
            else:
                return self.data[id]

    def stop(self):
        self._stop = True
        self.data_receive_thread.join()
        self.subscription_update_thread.join()