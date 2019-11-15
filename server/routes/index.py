from server import app
from flask import render_template
from ovp_job import getUserDetails
import json

@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


#@app.route('/report')
#def report():

#    user_details = getUserDetails(loginID='106471631@IBM.COM')
#    user_details = {k:(v.split(')')[0][1:] if v.startswith('(') else v) for k,v in user_details[0].iteritems()}
#    # print 'user_details:', user_details
#    # print 'user_details:', json.dumps(user_details, indent=4)
#    return json.dumps(user_details, indent=4)


@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
    return app.send_static_file('404.html')


@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
    return app.send_static_file('500.html')


