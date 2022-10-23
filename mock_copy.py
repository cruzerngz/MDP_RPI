import socket
from time import sleep
from multiprocessing import Process

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
# server_address = ('127.0.0.1', 12345)
server_address = ('192.168.12.1', 10003)
print(f'starting up on {server_address[0]} port {server_address[1]}')
sock.connect(server_address)

img1_val, img1_dist = None, None

def capture_img():
    while True:
        message = 'IMG:CA1'
        print('sending: ', message)
        sock.send(message.encode('utf-8'))

        sleep(5)


if __name__ == '__main__':

    t = Process(target=capture_img, args=())
    t.start()

    img1_val, img1_dist = None, None
    image_taken = False

    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            
            if not data:
                continue

            if data[:4] == 'IMG:' and data[:8] == 'IMG:CA1:':
                img1_val, img1_dist = data[8:].split(',')
                img1_dist = int(img1_dist)
                if img1_val in ('38', '39'):
                    image_taken = True
                else:
                    image_taken = False

            if 'START' in data and image_taken:
                t.terminate()
                break

        except:
            print('Error, closing socket')
            sock.close()
            break

        sleep(0.001)

   # RUN THE COMMAND
    if img1_val == '38':
        message = f'STM:\\sll{img1_dist};'
    elif img1_val == '39':
        message = f'STM:\\slr{img1_dist};'
    else:
        print("NOT WORKING")
        exit(0)
    print('sending: ', message)
    sock.send(message.encode('utf-8'))
    
    # WAIT FOR COMMAND TO FINISH
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if '&' in data:
                break

        except:
            print('Error, closing socket2')
            sock.close()
            break

        sleep(0.001)

    # CAP 2ND IMG
    message = 'IMG:CA2'
    print('sending: ', message)
    sock.send(message.encode('utf-8'))

    img2_val, img2_dist = None, None
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')

            if data[:4] == 'IMG:' and data[:8] == 'IMG:CA2:':
                img2_val, img2_dist = data[8:].split(',')
                img2_dist = int(img2_dist)
                break

        except:
            print('Error, closing socket2')
            sock.close()
            break

        sleep(0.001)
    
    # RUN THE COMMAND
    if img2_val == '39':
        message = f'STM:\\sbl{img2_dist};'
    elif img2_val == '38':
        message = f'STM:\\sbr{img2_dist};'
    else:
        print("NOT WORKING")
        exit(0)
    sock.send(message.encode('utf-8'))
    print('sending: ', message)

    sleep(0.1)
    
    # message = 'IMG:DONE'
    # print('sending: ', message)
    # sock.send(message.encode('utf-8'))
    
    # WAIT FOR COMMAND TO FINISH
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if '&' in data:
                break

        except:
            print('Error, closing socket2')
            sock.close()
            break

        sleep(0.001)

    sleep(0.3)
    
    message = f'STM:\\fo;'
    sock.send(message.encode('utf-8'))
    print('sending: ', message)

    # WAIT FOR COMMAND TO FINISH
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if '&' in data:
                break

        except:
            print('Error, closing socket2')
            sock.close()
            break

        sleep(0.001)
    
    print('finish')
    

