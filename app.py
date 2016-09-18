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

flaskApp = Flask(__name__)
CORS(flaskApp)

log_level=0
http_port = 8086
door_app = None
sip_cfg = {
    'registrar' : "192.168.1.129", 
    'username' : "5010", 
    'local_sip_port' : 5080,
    'passwrd' : "123456"
}

contacts = [{
    'name':'aaaaa','number':'11'
},{
    'name':'bbbbb','number':'22'
},{
    'name':'ccccc','number':'33'
},{
    'name':'ddddd','number':'44'
},{
    'name':'eeeee','number':'55'
},{
    'name':'fffff','number':'66'
},{
    'name':'ggggg','number':'77'
},{
    'name':'hhhhh','number':'88'
}]

@flaskApp.route('/')
def index():
    return jsonify({})

@flaskApp.route('/call/<uri>')
def make_call(uri):
    global door_app
    try:
        uri = "sip:5020@192.168.1.129"
        return jsonify({
            'call' : door_app.get_sip_agent().make_call(uri)
        })
    except pj.Error, e:
        print "Exception: " + str(e)
        return "Exception: " + str(e)

if __name__ == "__main__":
    try:
        # Start
        door_app = DoorApp()
        door_app.init_ui(contacts)
        door_app.init_sip_agent(sip_cfg,log_level)
        door_app.get_ui().display()
        flaskApp.run(host='0.0.0.0', port=http_port,debug=True,use_reloader=False)
        
    except pj.Error, e:
        print "Exception: " + str(e)
        
    # Shutdown
    door_app.get_sip_agent().transport = None
    door_app.get_sip_agent().account.delete()
    door_app.get_sip_agent().account = None
    door_app.get_sip_agent().lib.destroy()
    door_app.get_sip_agent().lib = None
