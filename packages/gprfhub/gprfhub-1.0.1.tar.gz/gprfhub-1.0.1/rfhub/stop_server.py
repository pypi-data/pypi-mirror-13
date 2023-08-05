import os
import signal

current_dir = os.path.dirname(os.path.abspath(__file__))


def stop_server():
    try:
        # open pid file and kill the process
        with open("/tmp/gprfhub.pid", "r") as pid_f:
            pid = pid_f.read()
            os.kill(int(pid), signal.SIGINT)
        return True
    except OSError as oserr:
        print "This file needs to be ran with sudo or as root"
        print "Error:", oserr
        return False
    except IOError as ioerr:
        print "/tmp/gprfhub.pid does not exist. Server not running?"
        print "Error:", ioerr
        return False


# clean up pid file if stopping the server succeeded
if stop_server():
    os.remove("/tmp/gprfhub.pid")
    os.remove(current_dir + "/login_gprfhub.py")
