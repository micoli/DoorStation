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
from flask import request, redirect, url_for,send_file
from flask_cors import CORS, cross_origin
from DoorStation import DoorStation
import UI
import json
import logging
import glob
import os

flaskApp = Flask(__name__)
CORS(flaskApp)

door_station = None
logger = logging.getLogger('app')

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
    return "\n".join([w.replace('/ram/', '<img src="/pic/').replace('.jpg','.jpg">') for w in sorted(glob.glob('/ram/*.jpg'), key=os.path.getsize,reverse=True)])

@flaskApp.route('/pic/<pic>')
def picture(pic):
    return send_file("/ram/"+pic, mimetype='image/jpg')

@flaskApp.route('/list')
def thumb():
    return jsonify({
        "list" : [w.replace('/ram/', '') for w in sorted(glob.glob('/ram/*.jpg'), key=os.path.getsize,reverse=True) ]
    })

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
        logger.exception("Exception: " + str(e))
        return "Exception: " + str(e)

if __name__ == "__main__":
    logging.basicConfig(filename='/ram/doorstation.log', level=logging.DEBUG)
    try:
        # Start
        door_station = DoorStation()
        door_station.init_ui(config['ui_cfg'],config['contacts'])
        door_station.init_sip_agent(config['sip_cfg'],config['log_level'])
        door_station.init_webcam({})
        flaskApp.run(host='0.0.0.0', port=config['http_port'],debug=True,use_reloader=False)

    except pj.Error, e:
        logger.error("Exception: " + str(e))

    # Shutdown
    door_station.get_sip_agent().transport = None
    door_station.get_sip_agent().account.delete()
    door_station.get_sip_agent().account = None
    door_station.get_sip_agent().lib.destroy()
    door_station.get_sip_agent().lib = None
