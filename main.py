import time
import server2
import thread

__author__ = 'Silvio'

if __name__ == '__main__':
    my_server = server2.newServer(50007)
    thread.start_new_thread(my_server.run, ())
    thread.start_new_thread(my_server.sender_thread(), ())

    while 1:
        time.sleep(2)
