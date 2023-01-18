# ChatGPT Wrote most of this in response to 
# "Write a python webservice that serves a json list of dictionaries in response to queries"
import json
from flask import Flask
from datetime import datetime
from random import normalvariate
from math import sqrt
from time import sleep
from flask_apscheduler import APScheduler

START_TIME = datetime.now()

app = Flask(__name__)

INIT_X=8
INIT_Y=36
INIT_H = 0

LOG_INTERVAL = 0.1

# The velocity random walk rate
VEL_WALK_RATE = 0.1

class StateSim():
    cadence = 0.1
    x = INIT_X
    y = INIT_Y
    hdg = INIT_H
    vx = 3
    vy = 0
    vhdg = 10
    last_runtime = 0.0
    maxlen = 10000

    def __init__(self):
        self.state_log = []    
        self.start_time = datetime.now()

    def reset_match(self):
        """Reset the simulation back to the start of a match.
        """
        self.x = INIT_X
        self.y = INIT_Y
        self.hdg = INIT_H 
        self.vx = 1.0
        self.vy = 0
        self.vhdg = 10
        self.last_runtime=0
        self.start_time = datetime.now()
        self.reset_log()

    @property
    def runtime(self) -> float:
        """compute runtime

        Returns:
            float: total seconds since start of match
        """
        return (datetime.now() - self.start_time).total_seconds()

    def add_record(self):
        """Add a log record to the list.
        """
        self.update_state()
        self.state_log.append({
            "type": "CombinedLocalizer",
            "runTime": self.runtime,
            "x": self.x,
            "y": self.y,
            "heading": self.hdg,
            "xVelocity": self.vx,
            "yVelocity": self.vy,
            "headingRate": self.vhdg,
            # The following values are completely fictitious.
            "positionUncertainty": 1,
            "headingUncertainty": 5,
            "targetVisible": True,
            "secondsSinceVuforia": 123,
        })
        if len(self.state_log) > self.maxlen:
            self.state_log = self.state_log[-self.maxlen:]
        
    def update_state(self):
        """Update the simulation state
        """
        runtime = self.runtime
        dt = (runtime - self.last_runtime)
        self.hdg += self.vhdg * dt
        self.x += self.vx * dt
        self.y += self.vy * dt 
        self.vx += normalvariate(0, 0.1) * sqrt(dt)
        self.vy += normalvariate(0, 0.1) * sqrt(dt)
        self.last_runtime = self.runtime

    def reset_log(self):
        """Clear the log
        """
        self.state_log = []

    def run_forever(self):
        while True:
            self.add_record()
            sleep(LOG_INTERVAL)

state_log = StateSim()

@app.route('/', methods=['GET'])
def list_dicts():
    states = state_log.state_log    
    state_log.reset_log()
    return json.dumps(states)


if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(id='add-record', func=state_log.add_record, trigger='interval', seconds=0.1)
    scheduler.add_job(id='reset-match', func=state_log.reset_match, trigger='interval', seconds=300)

    app.run(port=8079)