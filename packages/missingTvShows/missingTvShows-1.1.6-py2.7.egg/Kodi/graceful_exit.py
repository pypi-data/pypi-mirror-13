import signal
import sys
class Graceful_Exit():
    def __init__(self):
        self.original_sigint = signal.getsignal(signal.SIGINT)

    def __enter__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def __exit__(self, *args):
        signal.signal(signal.SIGINT, self.original_sigint)

    def exit_gracefully(self, signum, frame):
        # restore the original signal handler as otherwise evil things will happen
        # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant

        real_raw_input = vars(__builtins__).get('raw_input',input)

        try:
            if real_raw_input('\nReally quit? (y/n)> ').lower().startswith('y'):
                sys.exit(1)
        except KeyboardInterrupt:
            print("Ok ok, quitting")
            sys.exit(1)

        # restore the exit gracefully handler here
        signal.signal(signal.SIGINT, self.exit_gracefully)
