from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    """Return 'Hello from Arctic OS'."""
    return 'Hello from Arctic OS'

if __name__ == '__main__':
    app.run(debug=True)