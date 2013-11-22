#!/usr/bin/env python
# encoding: utf-8

import os.path
import json
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver

import Adafruit_BBIO.PWM as PWM

class CarController:
	def __init__(self):
		self.servo_pin = "P8_13"
		self.duty_min = 3
		self.duty_max = 14.5
		self.duty_span = self.duty_max - self.duty_min

		init_val = 0.5 * self.duty_span + self.duty_min
		PWM.start(self.servo_pin, init_val, 60.0)

	def __del__(self):
		PWM.stop(self.servo_pin)
		PWM.cleanup()

	def steer(self, v):
		v = float(v) / 100
		if v < 0:
			v = 0
		elif v > 1:
		 v = 1
		duty = float(v) * self.duty_span + self.duty_min
		PWM.set_duty_cycle(self.servo_pin, duty)
		print "steer: " + str(v)
 
class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("index.html", title="Car Controller")

class SocketHandler(tornado.websocket.WebSocketHandler):
	def __init__(self, *args, **kwargs):
		super(SocketHandler, self).__init__(*args, **kwargs)
		self.conns = []
		self.car = CarController()

	def open(self):
		if self not in self.conns:
			self.conns.append(self)
		print "connected"

	def on_close(self):
		if self in self.conns:
			self.conns.remove(self)
		print "disconnected"

	def on_message(self, message):
		data = json.loads(message)
		operation = data['operation']
		value = data['value']

		if operation == 'steer':
			self.car.steer(value)

if __name__ == "__main__":
  app = tornado.web.Application(
    handlers=[
      (r"/websocket", SocketHandler),
      (r"/", MainHandler)],
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates"))

  http_server = tornado.httpserver.HTTPServer(app)
  http_server.listen(80)
  tornado.ioloop.IOLoop.instance().start()
