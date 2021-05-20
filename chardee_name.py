from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import textwrap


def generate_name_card(name):
    og_name = name
    name = name.upper().replace(" ", "\n")
    para = name.split()

    img = Image.open("tommys_color.jpg")
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    font = ImageFont.truetype("chardee_font.otf", 90)

    w, h = draw.textsize(name, font = font)
    draw

    W,H = img.size
    current_h, pad = (H-h)/2, 10
    for line in para:
        w, h = draw.textsize(line, font=font)
        draw.text(((W - w) / 2, current_h), line,(239,198,46), font=font)
        current_h += h + pad

    #w, h = draw.textsize(name, font = font)
    #draw.text(((W - w) / 2, (H-h)/2),name,(239,198,46), font=font)
    file_name = name+'_card.jpg'
    img.save(file_name)
    return file_name

#generate_name_card("Gabrene Nicheck")
