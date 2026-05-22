from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')    

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/layout')
def layout():
    return render_template('layout.html')



if __name__ == '__main__':
    app.run(debug=True)