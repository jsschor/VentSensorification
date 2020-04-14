def decimalToBinary(n):
    binar = bin(n).replace("0b","")
    if len(binar)<8:
        binar = ("0" * (8-len(binar))) + binar
    return binar


import time
import spidev

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 0

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)

# Set SPI speed and mode
spi.max_speed_hz = 70000
spi.mode = 0

a,b,c,d = spi.readbytes(4)
# firstByte = decimalToBinary(a)
# secondByte = decimalToBinary(b)
# thirdByte = decimalToBinary(c)
# fourthByte = decimalToBinary(d)

# output = firstByte[2:] + secondByte
# outputDec = int("0b"+output,2)
if not a&192:
    outputDec = ((a&63)<<8) | b

    pressure = ((outputDec-1638)*(120))/(14745-1638)-60

    # tempOut = thirdByte + fourthByte[0:3]
    # tempOutDec = int("0b"+tempOut,2)
    tempOutDec = (c<<3) | (d>>5)

    temp = ((tempOutDec/2047)*200)-50
    # From transfer function in datasheet

    print(decimalToBinary(a))
    print(decimalToBinary(b))
    # print(int("0b" + output,2))
    print(pressure)
    # print(tempOut)
    print(tempOutDec)
    print(temp)
else:
    print('Error')