#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
from flask import Flask
import flask

from flask.ext.cors import CORS

app = Flask(__name__, template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'))

app.config.from_pyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),'flask.conf'))
if os.path.isfile(os.path.join(os.getcwd(), 'flask.conf')):
    app.config.from_pyfile(os.path.join(os.getcwd(),'flask.conf'))

if app.config['CORS']:
    CORS(app)

def getUrl(base, path):
    url = path[len(base):]
    return '/'.join(url.split(os.sep))

def getParent(path):
    parent = '/'.join([i for i in path.split('/') if len(i)][:-1])
    if parent:
        return '/' + parent + '/'
    return '/'


def colorConsole():
    import myterm, logging
    class StreamHandler(myterm.StreamHandler):
        """
            Change level by http code
        """
        def __init__(self, stream=None):
            myterm.StreamHandler.__init__(self, stream)
        
        def emit(self, record):
            try:
                http_return = int(record.msg.split('-')[-2].split(' ')[-2])
                if http_return >= 400:
                    record.levelno = 30
                if http_return >= 500:
                    record.levelno = 40
            except:
                pass
            myterm.StreamHandler.emit(self, record)

    ch = StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    log.addHandler(ch)
 

@app.route("/icons/folder.gif")
def iconfolder():
    return flask.send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'), 'folder.gif')

@app.route("/icons/file.gif")
def iconfile():
    return flask.send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'), 'file.gif')

@app.route("/icons/back.gif")
def iconback():
    return flask.send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'), 'back.gif')


@app.route("/")
@app.route("/<path:path>")
def static_web(path=""):
    try:
        if os.path.isdir(os.path.join(app.config['PATH_HTML'],path)):# and path[-1]== "/":
            if os.path.isfile(os.path.join(app.config['PATH_HTML'],path, app.config['DIRECTORY_INDEX'])):
                elt = os.path.abspath(os.path.join(app.config['PATH_HTML'],path, app.config['DIRECTORY_INDEX']))
                return flask.redirect(getUrl(app.config['PATH_HTML'],elt))#"/" + path + app.config['DIRECTORY_INDEX'])
            if app.config['INDEX']:
                parent = getParent(path)
                dirs = []
                files = []
                for i in os.listdir(os.path.join(app.config['PATH_HTML'],path)):
                    elt = os.path.abspath(os.path.join(app.config['PATH_HTML'],path,i))
                    if os.path.isfile(elt):
                        files.append({'name':i, 'path': getUrl(app.config['PATH_HTML'],elt) })#elt[len(app.config['PATH_HTML']):]})
                    else:
                        dirs.append({'name':i, 'path': getUrl(app.config['PATH_HTML'],elt)+'/'})#elt[len(app.config['PATH_HTML']):]+'/'})
                return flask.render_template('dirs.html', parent= parent, path=path, dirs=dirs, files=files)
            return flask.abort(404)
        return flask.send_from_directory(app.config['PATH_HTML'],path)
    except: 
        flask.abort(404)

def main():
    if app.config['COLOR']:
        colorConsole()
    app.run(host = app.config['HOST'],
            port = app.config['PORT'])

if __name__ == "__main__":
    main()
