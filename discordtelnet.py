import telnetlib, threading, socket ,queue


class socketserver(threading.Thread):
    """Socket server, starts a server on a fixed port, writes all recived messages to stdin and sends new queue items back"""
    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.daemon = True
        self.HOST = ''
        self.PORT = 50008
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.HOST,self.PORT))
    def run(self):
        self.soc.listen(1)
        conn, addr = self.soc.accept()
        conn.setblocking(False)
        while True:
            try:
                data = conn.recv(1024)
            except BlockingIOError:
                data = b""
            if data:
                print(data)
            try:
                val = self.queue.get(block=False)
                conn.sendall(val.encode())
            except queue.Empty:
                pass # no data avalable

# Threads:
# Discord.py < runs discord.py
# Telnet < accepts input
# socket server < runs a socket that interfaces discord.py and telnet
print("Starting socket server in a new thread")
q = queue.Queue()
s = socketserver(q)
s.start()
print("done")
print("adding default messages")
q.put("discord.py telnet interface\n")
q.put("i hope this works\n")
q.put("If the queue sending messages works, you should see these messages\n")
print("done")
print("telnet connect")
i = telnetlib.Telnet("localhost",50008)
print("done")
print("\n")
try:
    i.mt_interact()
except KeyboardInterrupt:
    pass
i.close()