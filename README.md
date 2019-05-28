# discordTelnet
My attempt to give discord.py a telnet interface.

# My plan
When there is a discord message, the on_message fires, and it adds the formatted message to the queue.
This causes the socket server to send it to the telnet client.
When the user sends a message, it calls the send message function for discord.py.
I hope this workds