from requests import session
from datetime import datetime
from time import sleep
from .state_records import StateRecord, Base, FieldPowerPlay, Robot
from .database import SessionLocal, ENGINE
from logging import info, INFO, basicConfig
from folium import Map

from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sas = SessionLocal()

DEFAULT_HOST=r"192.168.43.1"
DEFAULT_PORT="8079"
DEFAULT_PATH=""

URL_STRING = r"http://{host}:{port}/{path}"
RUNTIME_FIELD = "runtime"

DEFAULT_WAIT=0.25

REQUEST_TIMEOUT=0.2

basicConfig(level=INFO)

app = Flask(__name__)

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
    with sas as session:
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

# TODO: Find docs on how to make a lightweight http response. handle_get returns a field as html.
class StateRepeater:

    def __init__(self, session: Session):
        """Create a StateRepeater class. This is a lightweight http server that renders the field and the robot.

        Args:
            session (Session): a sqlalchemy session to grab state from.
        """
        self.session = session
        self.fpp = FieldPowerPlay()
        crs = "Simple"
        # Define our field_map.
        self.field_map = Map(location=[72, 72], zoom_start=2, min_zoom=1, max_zoom=4, tiles=None, crs=crs)
        self.fpp.add_to(self.field_map, show_junctions=True)
        self.robot = Robot((17, 16))
        self.field_map.add_child(self.robot)

    def update_robot(self):
        """Updated the robot location from the latest state
        """
        state = StateRecord.get_latest(self.session, type="CombinedLocalizer")
        # TODO: Check the age of the latest state. Warn if it's old.
        self.robot.position = (state.record['x'], state.record['y'])
        self.robot.heading = state.record['heading']

    def handle_get(self):
        self.update_robot()
        html = self.field_map.get_root().render()
        return html


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

def entrypoint(scheduler):
    """An entrypoint for installers.
    """
    args = parse_args()
    wait = args.wait
    Base.metadata.create_all(ENGINE)
    kwargs = vars(args)
    scheduler.add_job(id='monitor-robot', func=monitor_robot, kwargs=kwargs, trigger='interval', seconds=wait)

sr = StateRepeater(sas)
@app.route("/map")
def handle_get():
    return sr.handle_get()

# if __name__ == "__main__":
#     entrypoint()

if __name__ == '__main__':
    from flask_apscheduler import APScheduler

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    entrypoint(scheduler)

    app.run(port=5000)