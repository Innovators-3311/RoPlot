from requests import session
from datetime import datetime
from time import sleep

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

REQUEST_TIMEOUT=0.2

# This session has a short timeout. The robot is close and fast.
s = session()

class StateClient:
    _url = ""
    last_state = {}

    def __init__(self, host=DEFAULT_HOST, 
                port=DEFAULT_PORT, path=DEFAULT_PATH):
        self._url = URL_STRING.format(host=host, port=port, path=path)

    def get_state(self):
        r = s.get(self._url, timeout=REQUEST_TIMEOUT)
        if r.status == 200:
            return r.json()


def monitor_robot():
    sc = StateClient()
    with Session(ENGINE) as session:
        try:
            state_log = sc.get_state()
        except Exception as e:
            print(e)
            return

        # Add all the values.
        with session.begin():
            for state in state_log:
                session.add_all(state)
                last_state = state

if __name__ == "__main__":
    while True:
        monitor_robot()
        sleep(0.5)
