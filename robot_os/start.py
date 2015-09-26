import time
import threading


print('Loading modules...')
try:
    import server
    print('modules... Ok')
except Exception as e:
    print(e)
    print('modules... Fail')


IP = '10.0.0.1'
PORT = 3128
LISTEN = 1


if __name__ == '__main__':
    print('Creating server...')
    myServer = server.ThreadedServer((IP, PORT), server.UDPHandler)

    server_thread = threading.Thread(target=myServer.serve_forever)
    # server_thread.daemon = True

    print('Starting server...')
    server_thread.start()

    #TODO: Find another way
    try:
        while True:
            time.sleep(2**32)
    except KeyboardInterrupt as e:
        myServer.shutdown()
        myServer.server_close()
