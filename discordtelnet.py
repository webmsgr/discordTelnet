import telnetlib, threading, socket ,queue, os,sys


class socketserver(threading.Thread):
    """Socket server, starts a server on a fixed port, writes all recived messages to stdin and sends new queue items back"""
    def __init__(self, inqueue, outqueue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.inqueue = inqueue
        self.outqueue = outqueue
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
                if data == b"(kill)\n":
                    break
            try:
                val = self.inqueue.get(block=False)
                conn.sendall(val.encode())
            except queue.Empty:
                pass # no data avalable

# Threads:
# Discord.py < runs discord.py
# Telnet < accepts input
# socket server < runs a socket that interfaces discord.py and telnet
def telnetThread(port):
    print("telnet connect")
    i = telnetlib.Telnet("localhost",50008)
    print("done")
    print("\n")
    try:
        i.mt_interact()
    except KeyboardInterrupt:
        pass
    i.close()

discordkey = os.environ.get("dkey", None)
if discordkey is None:
    print("Set the environ dkey to your discord api key for discord.py")
    sys.exit(1)
channelid = os.environ.get("channelid",None)
if channelid is None:
    print("Set the environ channelid to the channel id of the discord channel you want to talk in")
    sys.exit(1)

# do discord.py stuff


iq = queue.Queue()
oq = queue.Queue()
server = socketserver(iq,oq)
server.start()
thr = threading.Thread(target=telnetThread,args=(server.PORT,),daemon=True)
thr.start()
server.join()
