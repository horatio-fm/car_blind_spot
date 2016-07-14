### Disclaimer:
### The user of the program below is solely responsible for any consequences derived
### from decisions made based on it. No warranty is made to its accuracy, utility or completeness.
### horatio.fm@gmail.com
### https://github.com/horatio-fm/car_blind_spot

from pylab import *
from matplotlib.widgets import Slider, Button, RadioButtons

from matplotlib.patches import Rectangle
import math
import numpy as np

def rotate_point(p, center, angle):
	x = center[0] + (p[0] - center[0])*math.cos(angle)
	x -= (p[1] - center[1])*math.sin(angle)

	y = center[1] + (p[0] - center[0])*math.sin(angle)
	y += (p[1] - center[1])*math.cos(angle)

	return [x, y]

def get_points_on_segment_A_B(a, b, no_of_reflection_points):
	slope = (b[1] - a[1])/(b[0] - a[0])
	ordinate = b[1] - slope * b[0]
	for x in np.linspace(a[0], b[0], no_of_reflection_points):
		y = x * slope + ordinate
		yield x,y

def get_angle_of_reflected_ray(mirror_angle, point_on_mirror, driver_position):
	alpha = math.atan((point_on_mirror[1] - 0)/(point_on_mirror[0] - driver_position))
	delta = math.pi/2 - (mirror_angle - alpha)
	# print(math.degrees(mirror_angle), math.degrees(alpha), math.degrees(delta))
	return alpha - 2*delta

class mirror():
	def __init__(self, pos, size, name, angle1 = 0):
		self.name = name
		self.pos = pos
		self.size = size
		self.plot_first_time = True
		self.length_of_rays = 60
		self.no_of_reflection_points = 10

		self.driver_position = 0
		self.mirror_reflection_lines_in = []
		self.mirror_reflection_lines_out = []

		pos = self.pos
		size = self.size
		self.angle = angle1

		self.mirror_reflection_lines_out = \
		[plot([], [], lw=1, color='blue')[0] for i in range(2)] + \
		[plot([], [], lw=1, color='cyan')[0] for i in range(self.no_of_reflection_points - 2)]

		self.mirror_reflection_lines_in = \
		[plot([], [], lw=2, color='blue')[0] for i in range(2)] + \
		[plot([], [], lw=1, color='cyan')[0] for i in range(self.no_of_reflection_points - 2)]

		self.line, = plot([], [], lw=2, color='red')

	def __call__(self):
		run(self, angle1 = 0)

	def run(self, angle1 = 0):
		pos = self.pos
		size = self.size
		self.angle = angle1

		A = [pos[0] - size/2.0, pos[1]]
		B = [pos[0] + size/2.0, pos[1]]

		A, *middle, B = [p for p in \
		get_points_on_segment_A_B(rotate_point(A, pos,angle1),rotate_point(B, pos,angle1), \
								  self.no_of_reflection_points)]
		lists_of_points =  [[A, B], middle]

		counter = 0
		for points in lists_of_points:
			for p in points:
				self.mirror_reflection_lines_out[counter].set_xdata([self.driver_position, p[0]])
				self.mirror_reflection_lines_out[counter].set_ydata([0, p[1]])

				angle2 = get_angle_of_reflected_ray(angle1, p, self.driver_position)

				length_and_direction_of_rays = (2*int(p[0] < self.driver_position) - 1) * self.length_of_rays
				self.mirror_reflection_lines_in[counter].set_xdata([p[0], p[0] + length_and_direction_of_rays*math.cos(angle2)])
				self.mirror_reflection_lines_in[counter].set_ydata([p[1], p[1] + length_and_direction_of_rays*math.sin(angle2)])

				counter += 1

		self.line.set_xdata([A[0], B[0]])
		self.line.set_ydata([A[1], B[1]])

ax = subplot(121)
# subplots_adjust(left=0.25, bottom=0.25)
subplots_adjust(left=0, bottom=0)

axis([-5, 5, -20, 2])
ax.set_aspect('equal')

mng = plt.get_current_fig_manager()
# mng.window.state('zoomed')

left_m = mirror([-.55, .6], .19, "left mirror")
right_m = mirror([1.2, .6], .19, "right mirror")
review_m = mirror([.32, .44], .215, "review mirror")

ax.add_patch(Rectangle(( -.45,  -2.5), 1.5, 4, facecolor="grey"))
axcolor = 'lightgoldenrodyellow'

patch = []
axs = []
car_sliders = []
for idx, (t, init_pos, name) in enumerate(zip([( -3.75,  -5), ( 2.75,  -5)], [-6, -10], ["car left", "car right"])):
	patch.append(Rectangle(t, 1.5, 4, facecolor="red"))
	axs.append(ax.add_patch(patch[-1]))
	sax = axes([0.55, 0.1 + 0.05*idx, 0.3, 0.03], axisbg=axcolor)
	car_sliders.append(Slider(sax, name, -20, 2, valinit=init_pos))
	car_sliders[-1].on_changed(axs[idx].set_y)
	car_sliders[-1].set_val(init_pos)

def run(pos):
	review_m.driver_position = pos
	left_m.driver_position = pos
	right_m.driver_position = pos
	review_m.run(review_m.angle)
	right_m.run(right_m.angle)
	left_m.run(left_m.angle)

mirror_list = [review_m, right_m, left_m, sys.modules[__name__]]

mirror_sliders = []
for idx, (name, slider_range) in enumerate(zip([m.name for m in mirror_list[:-1]] +["driver position"], [1, 1, 1, 0.5])):
	sax  = axes([0.55, 0.25 + 0.05*idx, 0.3, 0.03], axisbg=axcolor)
	mirror_sliders.append(Slider(sax, name, -slider_range, slider_range, valinit=0))
	mirror_sliders[-1].on_changed(mirror_list[idx].run)
	mirror_sliders[-1].set_val(0)

rax = axes([0.55, 0.5, 0.05, 0.15], axisbg=axcolor)
radio = RadioButtons(rax, ('default', 'old', 'new1', 'new2','set_left', 'set_right'), active=0)

def different_setups(setup):
	import json
	with open('state_%s1.json'%setup, 'r') as fp:
		vals = json.load(fp)
	for i, m in enumerate(mirror_sliders + car_sliders):
		m.set_val(vals[i])

radio.on_clicked(different_setups)

def button_save_function(d):
	vals = []
	for m in mirror_sliders + car_sliders:
		vals.append(m.val)

	import json
	fn = 'state_%s1.json'%radio.val
	with open(fn, 'w') as fp:
		json.dump(vals, fp)
	with open("last_saved.json", 'w') as fp:
		json.dump(radio.val, fp)

ax_button_save = axes([0.65, 0.5, 0.05, 0.03], axisbg=axcolor)
button_save = Button(ax_button_save, 'save')
button_save.on_clicked(button_save_function)

def button_get_last_saved(d):
	import json
	with open("last_saved.json", 'r') as fp:
		different_setups(json.load(fp))

ax_button_save = axes([0.65, 0.55, 0.10, 0.03], axisbg=axcolor)
button_save = Button(ax_button_save, 'get_last_saved')
button_save.on_clicked(button_get_last_saved)

# different_setups('old')

ax.plot([-1.5, -1.5], [-60, 2], color="black")
ax.plot([2, 2], [-60, 2], color="black")

show()
