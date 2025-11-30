import spidev
import time

# Open SPI bus 0, device 0 (CE0)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000  # 1 MHz


def read_register(addr):
    # For MFRC522, MSB=0 means read, LSB=0 (address shifted left 1)
    cmd = ((addr << 1) & 0x7E) | 0x80  # set MSB for read
    resp = spi.xfer2([cmd, 0])
    return resp[1]  # the second byte is the register value


try:
    version = read_register(0x37)  # VersionReg
    print(f"MFRC522 VersionReg = 0x{version:02X}")
finally:
    spi.close()
