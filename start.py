#! /usr/bin/env python

print("       ___  ____     ")
print("  _ _ / _ \/ ___\ _  ")
print(" | '_| | | \___ \(_) ")
print(" | | | |_| |___) | | ")
print(" |_|  \___/\____/|_| ")
print(" ------ SYSTEM ----- ")
print("")

import settings
import profiles

# start the rOSi kernel
print("ROBOT DETAILS")
from modules.kernel import handler

if settings.MODULES:
    # load module: ordex
    if settings.MODULES & profiles.ordex:
        print("")
        print("LOADING: ordex")
        from modules import ordex
        handler._ordex(ordex)

    if settings.MODULES & profiles.cluster:
        print()
        print('LOADING: cluster')
        from modules import cluster
        cluster.run()

    # load module: WebHUD
    if settings.MODULES & profiles.WebHUD:
        print("")
        print("LOADING: WebHUD")
        from modules.WebHUD.manage import run_server
        if __name__ == '__main__':
            run_server()
