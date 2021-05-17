from pa.control.control import Control
from pa.settings import live_strategies
from threading import Thread

if __name__ == '__main__':
    control = Control(live_strategies[0], live_strategies[1])
    control_thread = Thread(target=control.run)
    run_flag = control.run_flag
    events = control.events
    control_thread.start()
    control.run()