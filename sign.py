# from http://flask.pocoo.org/ tutorial
from flask import Flask, request, jsonify
#from flask_cors import CORS
from flask import render_template, redirect, g, url_for, abort
from flask import send_from_directory
from flask_babel import Babel
from flask_paginate import Pagination, get_page_parameter
import requests
import json
import sys

import pprint

templates_dir = './' #sys.argv[1]
static_dir = '/home/pi/src/signage/static' #sys.argv[2]
app = Flask(__name__, template_folder=templates_dir)
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './i18n'
babel = Babel(app)
#CORS(app)
'''
pybabel init -i fr.po -d ./i18n/ -l fr
pybabel compile -d i18n/
later only 	$ pybabel update -i fr.po -d i18n
'''

@app.before_request
def before():
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] not in ('fr', 'en'):
            return abort(404)
        g.current_lang = request.view_args['lang_code']
        request.view_args.pop('lang_code')

@babel.localeselector
def get_locale():
    return g.get('current_lang', 'en')

@app.route('/')
def root():
    return redirect(url_for('search', lang_code='en'))

def _send_static(filename):
    return send_from_directory(static_dir, filename)

#@app.route('/<string:page_name>/')
@app.route('/static/<string:page_name>')
def static_page(page_name):
    return _send_static(page_name)
    #return render_template('%s' % page_name)

@app.route('/css/<string:page_name>')
def css_page(page_name):
    return _send_static(page_name)

@app.route("/<lang_code>/search", methods=['GET'])
def search():
    qval = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    print (qval, request.get_json(), request.data, request.args)
    res = None
    pagination = None
    if qval:
        res = _get_search(qval, page)
        if res:
            res = json.loads(res)['response']
            total, per_page = res['record_count'], 20
            href=''.join(['/en/search?q=',qval,
                           '&num=20&page={0}'])
            if total > per_page:
                pagination = Pagination(page=page, per_page=per_page,
                                    href = href, bs_version=4,
                                    total=total, record_name='users')
    return render_template('index.html', qval=qval or '', res=res, locale=get_locale(),
                           pagination=pagination)

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8080)
    #test()

    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('', 8001), app)
    http_server.serve_forever()

