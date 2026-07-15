from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import ili9341
from PIL import Image
import time 


serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
device = ili9341(serial, rotate=1)

image = Image.open("monkey.jpg")
image = image.resize((device.width, device.height))
image = image.convert("RGB")

# device.display(image)

def main():
    with canvas(device) as draw:

        text = 'hello'
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((30, 40), text, fill="red")
        time.sleep(5)




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass