from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/cotemig/<nome>')
def cotemig(nome):
    return f'Olá {nome}'



if __name__ == '__main__':
    app.run(debug=True)


