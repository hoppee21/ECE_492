# pip install qrcode[pil]
import qrcode

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

data_to_encode = "ece492_test ETLCE3011xxt 192.168.0.195"
output_filename = "qr_code.png"
generate_qr_code(data_to_encode, output_filename)
print(f"QR code generated and saved as {output_filename}")