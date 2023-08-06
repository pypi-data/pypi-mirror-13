import traceback
import qrcode
import uuid

from io import BytesIO
from base64 import b64encode

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from django.conf import settings

app_sticker_template = settings.APP_STICKER_TEMPLATE
redeem_card_template = settings.REDEEM_CARD_TEMPLATE
reward_card_template = settings.REWARD_CARD_TEMPLATE 

font_filename = settings.FONT_FILENAME


def generate_qrcode(data, box_size=6, border=2):
    try:    
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )    
        qr.add_data(data)
        qr.make()
        
        img = qr.make_image()
        return img
    
    except:
        traceback.print_exc()
        return None
  
def generate_form(data, box_size, border, template, x, y, w, h):
    form_image = Image.open(template)
    qrcode_image = generate_qrcode(data, box_size, border) 
    qrcode_image = qrcode_image.resize((w, h), Image.ANTIALIAS)
    
    form_image.paste(qrcode_image, (x, y))    
    
    output = BytesIO()
    form_image.save(output,  format="png")
    output.seek(0)
    
    output_s = b64encode(output.read())
    return 'data:image/png;base64,%s' % output_s.decode()

def generate_reward_form(data, reward, passcode, box_size, border, template,
                        x, y, w, h):
    form_image = Image.open(template)
    qrcode_image = generate_qrcode(data, box_size, border) 
    qrcode_image = qrcode_image.resize((w, h), Image.ANTIALIAS)
    form_image.paste(qrcode_image, (x, y))
        
    try:
        #Add reward text
        """W1, H1 = (264, 60)
        font = ImageFont.truetype(font=font_filename, size=20)    
        text_img = Image.new("RGB", (W1, H1), (222, 88, 70))
        draw = ImageDraw.Draw(text_img)
        
        wt, ht = draw.textsize(reward, font=font)
        draw.text(((W1-wt)/2,(H1-ht)/2), reward, font=font)
        form_image.paste(text_img, (80, 110))"""
        
        #Add reward text
        W2, H2 = (368, 40) 
    
        font = ImageFont.truetype(font=font_filename, size=20)    
        text_img = Image.new("RGB", (W2, H2), (222, 88, 70))
        draw = ImageDraw.Draw(text_img)
        
        wt, ht = draw.textsize(reward, font=font)
        draw.text(((W2-wt)/2,(H2-ht-10)/2), reward, font=font)
        form_image.paste(text_img, (80, 185)) 
        
    
        output = BytesIO()
        form_image.save(output,  format="png")
        output.seek(0)
        
        output_s = b64encode(output.read())
        return 'data:image/png;base64,%s' % output_s.decode()
    except:
        traceback.print_exc()
        return None
        
def generate_key():
    return uuid.uuid4().hex

