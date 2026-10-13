import qrcode
from PIL import Image
import os

def generate_qr_code(url, output_folder, monument_name):
    if not url.startswith('http'):
        return None, 'Please enter a valid URL starting with http or https'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    filename = monument_name.replace(' ', '_') + '_qr.png'
    output_path = os.path.join(output_folder, filename)
    img.save(output_path)
    return output_path, None