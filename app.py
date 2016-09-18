#!/usr/bin/env python

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import pjsua as pj
import thread,threading
from flask import Flask,jsonify
from flask import render_template
from flask import request, redirect, url_for
from flask_cors import CORS, cross_origin
from DoorStation import DoorStation
import json

flaskApp = Flask(__name__)
CORS(flaskApp)

door_station = None

config = open('config.json').read(100000)

@flaskApp.route('/')
def index():
    return jsonify({})

@flaskApp.route('/call/<uri>')
def make_call(uri):
    global door_station
    try:
        uri = "sip:5020@192.168.1.129"
        return jsonify({
            'call' : door_station.get_sip_agent().make_call(uri)
        })
    except pj.Error, e:
        print "Exception: " + str(e)
        return "Exception: " + str(e)

if __name__ == "__main__":
    try:
        # Start
        door_station = DoorStation()
        door_station.init_ui(config['contacts'])
        door_station.init_sip_agent(config['sip_cfg'],config['log_level'])
        door_station.get_ui().display()
        flaskApp.run(host='0.0.0.0', port=config['http_port'],debug=True,use_reloader=False)

    except pj.Error, e:
        print "Exception: " + str(e)

    # Shutdown
    door_station.get_sip_agent().transport = None
    door_station.get_sip_agent().account.delete()
    door_station.get_sip_agent().account = None
    door_station.get_sip_agent().lib.destroy()
    door_station.get_sip_agent().lib = None
