from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from . import bot

class MySyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        print("connection established")
        self.send({
            'type': 'websocket.accept'
        })
        
    def websocket_receive(self, event):
        print(event['text'])
        for i in range(10):
            self.send({
                'type': 'websocket.send',
                'text': str(i)
            })

    def websocket_disconnect(self, event):
        print("Disconnected")
        raise StopConsumer()

class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        client_message = event['text']
        if client_message == "initial message decided by developers":
            await self.send({
                'type': 'websocket.send',
                'text': "Hello !!...You can call me tai or Di.Im here to assist you with the issues your facing\nand will be confidential between us..\nSo shall we start?? please enter 'YES' if you like to proceed and 'NO' if don't"
            })
        elif client_message.lower() == "yes":
            await self.send({
                'type': 'websocket.send',
                'text': "Ask me and Tai will guide you with your issues!!"
            })
        elif client_message.lower() == "no":
            await self.send({
                'type': 'websocket.send',
                'text': "Its okay if you're not ready...Feel free to comeback anytime\nyour Didi will always help you!!"
            })
        else:
            server_answer = bot.api(client_message)
            await self.send({
                'type': 'websocket.send',
                'text': server_answer
            })

    async def websocket_disconnect(self, event):
        raise StopConsumer()