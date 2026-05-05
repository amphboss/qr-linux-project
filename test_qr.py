from shared.qr_generator import QRGenerator

qr = QRGenerator()
path = qr.generate("Hello from QR project")

print("QR создан:", path)
