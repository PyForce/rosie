import time
import server
import thread
import controller

controller.timer_init()

my_server = server.Server(50007)
thread.start_new_thread(my_server.run, ())
thread.start_new_thread(my_server.sender_thread(), ())

while 1:
    time.sleep(2)
