from requests import session
from datetime import datetime
from time import sleep
from state_records import StateRecord, Base
from logging import info, INFO, basicConfig

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATA_PATH='data'
TODAY = datetime.now().strftime("%Y-%m-%d")
ENGINE = create_engine(f"sqlite:///{DATA_PATH}/{TODAY}.sqlite")

DEFAULT_HOST=r"192.168.43.1"
DEFAULT_PORT="8079"
DEFAULT_PATH=""

URL_STRING = r"http://{host}:{port}/{path}"
RUNTIME_FIELD = "runtime"

DEFAULT_WAIT=0.25

REQUEST_TIMEOUT=0.2

basicConfig(level=INFO)

# This session has a short timeout. The robot is close and fast.
s = session()

class StateClient:
    _url = ""
    last_state = {}

    def __init__(self, host=DEFAULT_HOST, 
                port=DEFAULT_PORT, path=DEFAULT_PATH,
                timeout=REQUEST_TIMEOUT):
        self._url = URL_STRING.format(host=host, port=port, path=path)
        self.timeout = timeout

    def get_state(self):
        r = s.get(self._url, timeout=self.timeout)
        if r.status_code == 200:
            return r.json()


def monitor_robot(**kwargs):
    scargs = {k:v for k,v in kwargs.items() if k in ('host', 'port', 'path', 'timeout')}
    sc = StateClient(**scargs)
    with Session(ENGINE) as session:
        try:
            state_log = sc.get_state()
        except Exception as e:
            print(e)
            return

        # Add all the values.
        with session.begin():
            all_states = [ StateRecord(state) for state in state_log]
            session.add_all(all_states)
            if len(state_log)>0:
                last_state = state_log[-1]
        info(f"Saved {len(all_states)} states")

def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # add arguments with default values
    parser.add_argument('--host', default=DEFAULT_HOST)
    parser.add_argument('--port', default=DEFAULT_PORT)
    parser.add_argument('--path', default=DEFAULT_PATH)
    parser.add_argument('--timeout', default=REQUEST_TIMEOUT)
    parser.add_argument('--wait', default=DEFAULT_WAIT)

    return parser.parse_args()

def entrypoint():
    """An entrypoint for installers.
    """
    args = parse_args()
    wait = args.wait
    Base.metadata.create_all(ENGINE)
    kwargs = vars(args)
    while True:
        monitor_robot(**kwargs)
        sleep(wait)


if __name__ == "__main__":
    entrypoint()