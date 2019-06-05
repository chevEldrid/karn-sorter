from PIL import Image
from picamera import PiCamera
import sys
import time

camera = PiCamera()
rotation_angle = 4
alignment_time = 2
area = (325, 550, 700, 650)
adjs_x = (-20, -10, 10, 20, 30, 0, 0, 0, 0, 0)
adjs_y = (0, 0, 0, 0, 0, -20, -10, 10, 20, 0)

def camera_setup(camera):
    camera.color_effects = (128, 128)
    camera.rotation = 0
    camera.resolution = (1000, 1000)

#given picture name, crop it to just be card name
def crop_picture(pic_name):
    img = Image.open(pic_name)
    cropped_img = img.crop(area)
    cropped_img.save(pic_name)
#produces string that lists the for dimensions of the cropped area
def string_crop(dimensions):
    temp = "Taking picture at: "
    for i in range(0, 4):
        temp += (str(dimensions[i])+",")
    return temp
#------------------------------------------------------
print("Welcome to The Crop Finder...")
camera_setup(camera)

#take 10 pictures at various croppings - see which is best
for i in range(0, 10):
    print(string_crop(area))
    time.sleep(alignment_time)
    pic_name = "crops/mtg_"+str(i)+".jpg"
    camera.capture(pic_name)
    #crop photo
    crop_picture(pic_name)
    print("Picture taken! See {0}!".format(pic_name))
    #adjust area
    #x
    x_0 = area[0] + adjs_x[i]
    x_1 = area[2] + adjs_x[i]
    #y
    y_0 = area[1] + adjs_y[i]
    y_1 = area[3] + adjs_y[i]
    area = (x_0, y_0, x_1, y_1)
