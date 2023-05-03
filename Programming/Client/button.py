import pygame
from utils import draw_text, ping_server

display_info = pygame.display.Info()

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False
		self.margin = (0, 0)

	def set_position(self, x, y):
		self.rect.topleft = (x, y)

	def set_margin(self, x, y):
		self.margin = (x, y)

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()
		pos = (
			pos[0] - self.margin[0],
			pos[1] - self.margin[1]
		)

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

class ServerButton():
	def __init__(self, width, height, x, y, color: list[int], server,
			text_color = (255, 255, 255),
			additionals_to_coords = None, 
			transparent = None, 
			font = None
		):
		self.clicked = False
		self.additionals_to_coords = additionals_to_coords
		self.width = width
		self.height = height
		self.x = x
		self.y = y
		self.font = font
		self.text_color = text_color
		self.color = color # [1, 2, 3]
		self.canvas = pygame.Surface((width, height))
		self.server = server
		self.transparent = transparent # {"color": [1,2,3], "time": seconds}
		if transparent:
			self.transparent = {
				"time": int(transparent["time"] * 60),
				"color": []
			}
			for i in range(3):
				colcode = transparent["color"][i]
				self.transparent["color"].append({
					"code": colcode,
					"at_once": (colcode - color[i]) / self.transparent["time"]
				})
		self.timer = 0
		self.last_ping = ""

	def available(self):
		return 'address' in self.server and 'port' in self.server
	
	def get_color(self):
		if not self.transparent or self.timer == 0:
			return (self.color[0], self.color[1], self.color[2])
		colors = []
		for i in range(3):
			data = int(self.color[i] + self.transparent["color"][i]["at_once"] * self.timer)
			colors.append(data)
		return (colors[0], colors[1], colors[2])

	def is_mouse_in_canvas(self):
		posX, posY = pygame.mouse.get_pos()
		x = (self.additionals_to_coords["x"] if self.additionals_to_coords else 0) + self.x
		y = (self.additionals_to_coords["y"] if self.additionals_to_coords else 0) + self.y
		return (x <= posX <= x + self.width) and (y <= posY <= y + self.height)

	def draw(self, surface: pygame.Surface, ping: bool):
		action = False

		#check mouseover and clicked conditions
		if self.is_mouse_in_canvas():
			if self.transparent and self.timer < self.transparent["time"]:
				self.timer += 1
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True
		elif self.transparent and self.timer > 0:
			self.timer -= 1

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		self.canvas.fill(self.get_color())

		draw_text(self.canvas, ("Сервер " + self.server["name"]), 0, 0, orientation="left", font=self.font, text_color=self.text_color)
		if ping and "port" in self.server and "address" in self.server:
			self.last_ping = ping_server(self.server["address"])
		draw_text(self.canvas, self.last_ping, 0, 0, orientation="right", font=self.font, text_color=self.text_color)
	
		surface.blit(self.canvas, (self.x, self.y))
		
		return action

class CanvasButton():
	def __init__(self, width, height, x, y, color: list[int], contents, 
			additionals_to_coords = None, 
			transparent = None, 
			font = None,
			orientation = ""
		):
		self.clicked = False
		self.additionals_to_coords = additionals_to_coords
		self.width = width
		self.height = height
		self.x = x
		self.y = y
		self.font = font
		self.orientation = orientation
		self.color = color # [1, 2, 3]
		self.canvas = pygame.Surface((width, height))
		self.contents = contents
		self.transparent = transparent # {"color": [1,2,3], "time": seconds}
		if transparent:
			self.transparent = {
				"time": int(transparent["time"] * 60),
				"color": []
			}
			for i in range(3):
				colcode = transparent["color"][i]
				self.transparent["color"].append({
					"code": colcode,
					"at_once": (colcode - color[i]) / self.transparent["time"]
				})
		self.timer = 0
		self.last_ping = 0

	def get_color(self):
		if not self.transparent or self.timer == 0:
			return (self.color[0], self.color[1], self.color[2])
		colors = []
		for i in range(3):
			data = int(self.color[i] + self.transparent["color"][i]["at_once"] * self.timer)
			colors.append(data)
		return (colors[0], colors[1], colors[2])

	def is_mouse_in_canvas(self):
		posX, posY = pygame.mouse.get_pos()
		x = (self.additionals_to_coords["x"] if self.additionals_to_coords else 0) + self.x
		y = (self.additionals_to_coords["y"] if self.additionals_to_coords else 0) + self.y
		return (x <= posX <= x + self.width) and (y <= posY <= y + self.height)

	def draw(self, surface: pygame.Surface, ping = False):
		action = False

		#check mouseover and clicked conditions
		if self.is_mouse_in_canvas():
			if self.transparent and self.timer < self.transparent["time"]:
				self.timer += 1
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True
		elif self.transparent and self.timer > 0:
			self.timer -= 1

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		self.canvas.fill(self.get_color())

		for content in self.contents:
			text = content["text"]
			if "ping|" in content["text"]:
				if ping:
					self.last_ping = ping_server(content["text"].replace("ping|", "", 1))
				text = self.last_ping
			draw_text(self.canvas, text, content["x"], content["y"], orientation=self.orientation, font=self.font, text_color=content["color"])
	
		surface.blit(self.canvas, (self.x, self.y))
		
		return action

class SwitchButton():
	def __init__(self, width, height, x, y, color: list[int], 
			content,
			values,
			additionals_to_coords = None, 
			transparent = None, 
			font = None
		):
		self.clicked = False
		self.additionals_to_coords = additionals_to_coords
		self.width = width
		self.height = height
		self.x = x
		self.y = y
		self.values = values
		self.color = color # [1, 2, 3]
		self.font = font
		self.canvas = pygame.Surface((width, height))
		self.text_canvas = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
		self.value_canvas = pygame.Surface((height, height))
		self.content = content
		self.current_value = 0
		self.transparent = transparent # {"color": [1,2,3], "time": seconds}
		if transparent:
			self.transparent = {
				"time": int(transparent["time"] * 60),
				"color": []
			}
			for i in range(3):
				colcode = transparent["color"][i]
				self.transparent["color"].append({
					"code": colcode,
					"at_once": (colcode - color[i]) / self.transparent["time"]
				})
		self.timer = 0
		self.last_ping = 0

	def get_color(self):
		if not self.transparent or self.timer == 0:
			return (self.color[0], self.color[1], self.color[2])
		colors = []
		for i in range(3):
			data = int(self.color[i] + self.transparent["color"][i]["at_once"] * self.timer)
			colors.append(data)
		return (colors[0], colors[1], colors[2])
	
	def get_second_color(self):
		colors = self.get_color()
		return (colors[0] - 30, colors[1] - 30, colors[2] - 30)

	def is_mouse_in_canvas(self):
		posX, posY = pygame.mouse.get_pos()
		x = (self.additionals_to_coords["x"] if self.additionals_to_coords else 0) + self.x
		y = (self.additionals_to_coords["y"] if self.additionals_to_coords else 0) + self.y
		return (x <= posX <= x + self.width) and (y <= posY <= y + self.height)

	def switch(self):
		self.current_value = 0 if self.current_value + 1 >= len(self.values) else self.current_value + 1
		return self.values[self.current_value]

	def current(self):
		return self.values[self.current_value]

	def draw(self, surface: pygame.Surface):
		action = False

		#check mouseover and clicked conditions
		if self.is_mouse_in_canvas():
			if self.transparent and self.timer < self.transparent["time"]:
				self.timer += 1
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True
		elif self.transparent and self.timer > 0:
			self.timer -= 1

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		self.canvas.fill(self.get_color())
		surface.blit(self.canvas, (self.x, self.y))

		self.text_canvas.fill((0,0,0,0))
		if self.content["text"] != None:
			self.value_canvas.fill(self.get_second_color())
			surface.blit(self.value_canvas, (self.x + self.width - self.height, self.y))
			
			draw_text(self.text_canvas, self. content["text"], self.content["x"], self.content["y"], orientation="left", font=self.font, text_color=self.content["color"])
			draw_text(self.text_canvas, self.current(), self.content["x"], self.content["y"], orientation="right", font=self.font, text_color=self.content["color"])
		else:
			draw_text(self.text_canvas, self.current(), self.content["x"], self.content["y"], orientation="center", font=self.font, text_color=self.content["color"])
		surface.blit(self.text_canvas, (self.x, self.y))
		
		return action