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
import UI
import json

flaskApp = Flask(__name__)
CORS(flaskApp)

door_station = None

def load_config(filename):
    def ascii_encode_dict(data):
        def ascii_encode(x):
            if callable(getattr(x, "encode", None)):
                return x.encode('ascii')
            return x
        return dict(map(ascii_encode, pair) for pair in data.items())
    return json.loads(open(filename).read(100000),object_hook=ascii_encode_dict)

config = load_config('config.json')

@flaskApp.route('/')
def index():
    return jsonify({})

@flaskApp.route('/call/',)
def make_call():
    global door_station
    uri = request.args.get('uri', '')
    try:
        #uri = "sip:5020@192.168.1.129"
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
        #door_station.init_sip_agent(config['sip_cfg'],config['log_level'])
        flaskApp.run(host='0.0.0.0', port=config['http_port'],debug=True,use_reloader=False)

    except pj.Error, e:
        print "Exception: " + str(e)

    # Shutdown
    door_station.get_sip_agent().transport = None
    door_station.get_sip_agent().account.delete()
    door_station.get_sip_agent().account = None
    door_station.get_sip_agent().lib.destroy()
    door_station.get_sip_agent().lib = None
