import telnetlib, threading, socket ,queue, os, sys, random


class socketserver(threading.Thread):
    """Socket server, starts a server on a fixed port, writes all recived messages to stdin and sends new queue items back"""
    def __init__(self, inqueue, outqueue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.daemon = True
        self.HOST = ''
        self.PORT = random.randint(50000,50100)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.HOST,self.PORT))
    def run(self):
        self.soc.listen(1)
        conn, addr = self.soc.accept()
        if addr[0] != "127.0.0.1":
            return
        conn.setblocking(False)
        while True:
            try:
                data = conn.recv(1024)
            except BlockingIOError:
                data = b""
            if data:
                if data == b"/kill\n":
                    break
                self.outqueue.put(data,False)
            try:
                val = self.inqueue.get(block=False)
                conn.sendall(val.encode())
            except queue.Empty:
                pass # no data avalable

# Threads:
# Discord.py < runs discord.py
# Telnet < accepts input
# socket server < runs a socket that interfaces discord.py and telnet
# autologout < when the discord bot is blocking, this detects the server shutting down and logs out the bot
def telnetThread(port):
    print("telnet connect")
    i = telnetlib.Telnet("localhost",port)
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

def getincoming():
    try:
        mes = [oq.get(False)]
    except queue.Empty:
        return []
    return mes

import discord
import asyncio
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        thr.start()
    async def on_message(self,message):
        if message.author != message.guild.get_member(self.user.id):
            mes = message.clean_content
            iq.put("{}:{}\n".format(message.author.display_name,mes))
    async def my_background_task(self):
        await self.wait_until_ready()
        channel = self.get_channel(int(channelid))
        print("Chatting in {}".format(channel.name))
        while not self.is_closed():
            newmes = getincoming()
            for mes in newmes:
                mes = mes.decode()
                if mes.startswith("/"):
                    mes = mes.split("/")[1]
                    if mes.startswith("channel"):
                        newchannelid = mes.split(" ")[1]
                        print("Switching to channel...")
                        channel = self.get_channel(int(newchannelid))
                        print("Chatting in {}".format(channel.name))
                    elif mes.startswith("list-channel"):
                        serverid = mes.split(" ")[1]
                        dserver = self.get_guild(int(serverid))
                        print("Channels in server {}".format(dserver.name))
                        #print(dserver.channels)
                        for chanel in dserver.channels:
                            if isinstance(chanel,discord.TextChannel):
                                print("{}:{}".format(chanel.name,chanel.id))
                    else:
                        print("Invalid Command!")
                else:
                    await channel.send(mes)
            await asyncio.sleep(1) # task runs every 60 seconds



iq = queue.Queue()
oq = queue.Queue()
server = socketserver(iq,oq)
server.start()
thr = threading.Thread(target=telnetThread,args=(server.PORT,),daemon=True)

def autologout(server,dclient):
    server.join()
    print("Logging Out")
    loop = dclient.loop
    dclient.logouttask = loop.create_task(dclient.logout())
    i = False
    while not i:
        i = dclient.is_closed()
client = MyClient()
autolog = threading.Thread(target=autologout,args=(server,client),daemon=False)
autolog.start()
client.run(discordkey)
autolog.join()
