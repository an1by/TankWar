import pygame
from utils import draw_text, ping_server

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

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

class CanvasButton():
	def __init__(self, width, height, x, y, color, additionals_to_coords, contents, transparent):
		self.clicked = False
		self.additionals_to_coords = additionals_to_coords
		self.width = width
		self.height = height
		self.x = x
		self.y = y
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
		x = self.additionals_to_coords["x"] + self.x
		y = self.additionals_to_coords["y"] + self.y
		return (x <= posX <= x + self.width) and (y <= posY <= y + self.height)

	def draw(self, surface, ping):
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
			draw_text(self.canvas, text, content["color"], content["x"], content["y"])
	
		surface.blit(self.canvas, (self.x, self.y))
		
		return action
