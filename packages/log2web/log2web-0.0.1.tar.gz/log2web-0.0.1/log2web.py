from flask import Flask
import sys
import os
import random
app = Flask(__name__)

view_html='''
<html>
<head>
<title>log2web</title>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js">
</script>
</head>
<body>
<div id="result"></div>
<hr>
<button onclick="toggle_scroll()"> Auto Scroll Toggle </button>
&nbsp;
<div style="display: inline" id="auto_scroll_stat">ON</div>
</body>
<script>
var autoscroll = "ON";
toggle_scroll = function(){
    if(autoscroll == "ON") autoscroll = "OFF";
    else autoscroll = "ON";
}

get_log = function(){
 $.ajax({url: "/info", success: function(result){
    $("#result").html("<xmp>"+result +"</xmp>");
    if(autoscroll == "ON")
        window.scrollTo(0,document.body.scrollHeight);
    $("#auto_scroll_stat").text(autoscroll);
 }});
}
setInterval(get_log,%s);
</script>
</html>
'''

refresh_msec = 1000
log_file = ''

@app.route("/info")
def info():
    global log_file
    if os.path.isfile(log_file):
        fo = open(log_file)
        content  = fo.read()
        return content
    else :
        return "There is no log file"

@app.route("/")
def view():
    global view_html
    global refresh_msec
    return view_html % refresh_msec


def pick_unused_port():
    return random.randint(59000,59999)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage : log2web sample.log 1000(refresh msec)"
        exit()
    log_file = sys.argv[1]
    refresh_msec = sys.argv[2]
    app.run(host="0.0.0.0",port=pick_unused_port())
