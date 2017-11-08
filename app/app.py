from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Algo VPN Generator'

@app.route('/test')
def test():
    return 'The app appears to be working correctly.'