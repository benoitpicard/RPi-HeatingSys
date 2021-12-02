# Answer to a question on Flask mailing list
# http://librelist.com/browser//flask/2012/6/30/using-ajax-with-flask/
# NOTE: *REALLY* don't do the thing with putting the HTML in a global
#       variable like I have, I just wanted to keep everything in one
#       file for the sake of completeness of answer.
#       It's generally a very bad way to do things :)
#
from flask import Flask, request, jsonify

import pandas as pd
import json

file1 = open(r"aaatest1.txt","a+") 
file1.write('\n----')
file1.close() 

app = Flask(__name__)

html_page = """<!DOCTYPE HTML>
<html>
<head>
<title>Rough AJAX Test</title>

<script>
    function loadXMLDoc()
    {
        var req = new XMLHttpRequest()
        req.onreadystatechange = function()
        {
            if (req.readyState == 4)
            {
                if (req.status != 200)
                {
                    //error handling code here
                }
                else
                {
                    var response = JSON.parse(req.responseText)
                    document.getElementById('myDiv').innerHTML = response.username
                }
            }
        }
    
        req.open('POST', '/ajax')
        req.setRequestHeader("Content-type", "application/json")
        var un = document.getElementById('scname').value
        var sec = document.getElementById('secret').value
        var postVars = {
          scname: document.getElementById('scname').value,
          secret: document.getElementById('secret').value
        };
        req.send(JSON.stringify(postVars))
//        var postVars = 'username='+un+'&secret='+sec
//        req.send(postVars)
        
        return false
    }
</script>

</head>
<body>
<h1>Flask AJAX Test</h1>
<form action="" method="POST">
<input type="text" name="scname" id="scname">
<input type="text" name="secret" id="secret" value="shhh">
<input type="button" value="Submit" onclick="return loadXMLDoc()">
</form>
<div id="myDiv"></div>
</body>
</html>"""

@app.route('/')
def index():
    return html_page
        
        
@app.route('/ajax', methods = ['POST'])
def ajax_request():
#    username = request.form['username']
#    secret = request.form['secret']
 #   request.json()
 
    file1 = open(r"aaatest1.txt","a+") 
    file1.write('\najax sent:\n')
    file1.write(str(request.data))
    y = json.loads(request.data)
    file1.write('\n'+y['scname'])
    file1.write('\n'+y['secret'])
    file1.close() 

    return '1'
#    content = request.data
#    converted = content
#    return converted
#    return "Hello, Flask!"
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=False)