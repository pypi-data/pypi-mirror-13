import fcntl
import serial
import binascii


def calculate_checksum(frameData):
    print 'calculating checksum'
    checksum = 0
    for a in frameData:
        checksum += int(a, 16)
    return hex(int('0xFF', 16)-int(str(hex(checksum))[-2:], 16))


def create_frame(address, data):
    print 'creating frame'
    frameDelimiter = "7E"
    frameType = "10"
    frameId = "01"
    destAdd = "FF FE"
    broadcastR = "00"
    options = "00"

    d = ' '.join([frameType, frameId, address, destAdd, broadcastR, options])
    arr = d.split(' ')
    for a in data:
        arr.append(str(a.encode('hex')))

    checksum = calculate_checksum(arr)
    arr = arr[::-1]
    arr.append(str(hex(len(arr))).replace('0x', ''))
    arr.append("00")
    arr.append(frameDelimiter)
    arr = arr[::-1]
    arr.append(str(checksum).replace('0x', ''))
    cmd = ''.join(b for b in arr)

    return cmd


def send_transmit_request(address, data, get_response=False, port='/dev/ttyUSB0', baudrate=9600, timeout=3.0):
    frame = create_frame(address, data)
    ba = bytearray.fromhex(frame)
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    #fcntl.flock(ser.fileno(), fcntl.LOCK_EX)
    ser.write(ba)
    ser.close()
    if get_response:
        return ba, frame, read_serial()
    return ba, frame


def read_serial():

    ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=3.0)
    s = b''

    #bytesToRead = ser.inWaiting()

    s += ser.read()
    if binascii.hexlify(s) == b'7e':
        w = ser.read(2)
        s += w
        l = int(binascii.hexlify(w), 16)
        s += ser.read(l + 2)
        s = binascii.hexlify(s)

        if s[6:8] == b'90':  # Receive Request, checksum verification not needed.
            data = s[32:-2]
            data = binascii.unhexlify(data).decode('utf-8').strip('\0')
            return data
    else:
        s = b''
        return 'nothing here'
