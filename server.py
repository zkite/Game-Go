import os, json
from game import *
from jinja2 import FileSystemLoader, Environment
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

settings = {"static_path": os.path.join(os.path.dirname(__file__), "static")}


class Index(RequestHandler):
	templateLoader = FileSystemLoader(searchpath='templates')
	templateEnvironment = Environment(loader=templateLoader)
	template = templateEnvironment.get_template('index.html')
	def get(self):
		html_output = self.template.render()
		self.write(html_output)


class Handler(WebSocketHandler):
	clients = set()
	black = False
	white = False
	game = GoGame()

	def check_origin(self, origin):
		return True

	def open(self):
		if not Handler.black:
			Handler.clients.add(self)
			Handler.black = True
			self.color = {"name": "black", "value": BLACK}
			self.write_message(json.dumps({"action": "turn"}))
		else:
			Handler.clients.add(self)
			Handler.white = True
			self.color = {"name": "white", "value": WHITE}

	def on_message(self, message):
		x, y = [int(z) for z in message.split("_")]
		result = Handler.game.move_stone(x, y)

		if (result.status == VALID):
			for client in Handler.clients:
				client.write_message(json.dumps({"action": "put", "x": x, "y": y, "color": self.color["name"]}))

				for prisoner in result.prisoners:
					client.write_message(json.dumps({"action": "remove", "x": prisoner[0], "y": prisoner[1]}))

				score = Handler.game.calculate_score()
				client.write_message(json.dumps({'action':'score','score':{'black':score[0], 'white':score[1]}}))

				if client.color["value"] == Handler.game.to_play:
					client.write_message(json.dumps({"action": "turn"}))

		elif (result.status == COMPLETED):
			for client in Handler.clients:
				client.write_message(json.dumps({'action':'completed'}))
		else:
			self.write_message(json.dumps({"action": "nope"}))

	def on_close(self):
		Handler.clients.remove(self)
		if self.color["value"] == BLACK:
			Handler.black = False
		else:
			Handler.white = False


HTTPServer(Application(handlers=[(r'/', Index),(r"/game", Handler)],**settings)).listen('777')
IOLoop.instance().start()
