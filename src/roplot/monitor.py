from requests import session
from datetime import datetime
from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATA_PATH='data'
TODAY = datetime.now().strftime("%Y-%m-%d")
ENGINE = create_engine(f"sqlalchemy://{DATA_PATH}/{TODAY}.sqlite")

DEFAULT_HOST=r"192.168.43.1"
DEFAULT_PORT="8079"
DEFAULT_PATH=""

URL_STRING = r"http://{host}:{port}/{path}"
RUNTIME_FIELD = "runtime"

# This session has a short timeout. The robot is close and fast.
s = session(timeout = 0.2)

class StateClient:
    _url = ""

    def __init__(self, host=DEFAULT_HOST, 
                port=DEFAULT_PORT, path=DEFAULT_PATH):
        self._url = URL_STRING.format(host=host, port=port, path=path)
        self.create_db()


    def create_db(self, data_path=DATA_PATH):
        today = datetime.now().strftime("%Y-%m-%d")
        self._con = connect(f"{data_path}/{today}.tinydb")
        self.con.execute("CREATE TABLE state_data(timestamp, state)")


    def get_state(self):
        r = s.get(self._url)
        if r.status == 200:
            return r.json()

def monitor_robot():
    sc = StateClient()
    with Session(ENGINE) as session:
        try:
            state = sc.get_state()
        except Exception as e:
            print(e)
            sleep(1)

        # Add all the values.
        with session.begin():
            for val in state:
                session.add_all(val)
