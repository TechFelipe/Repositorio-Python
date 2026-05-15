from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Currículo</title>
        </head>
        <body>
            <h1>Currículo</h1>

            <h2>Informações Pessoais</h2>
            <ul>
                <li><strong>Nome:</strong> Felipe Marcolino</li>  
                <li><strong>Email:</strong> 12400980@aluno.cotemig.com.br</li>
                <li><strong>Telefone:</strong> (11) 99999-9999</li>
            </ul>

            <h2>Conhecimentos</h2>
            <ul>
                <li><strong>Linguagens:</strong>C#, MySql, HTML & CSS
                </br>Python, dart/flutter, swift, kotlin</li>
                <li><strong>Cargo:</strong>Estudante</li>
                <li><strong>Período estimado de conclusão:</strong>Decembro 2026</li>
            </ul>
            <h2>Destaques</h2>
            <ul>
                <li><strong>Inglês:</strong> Avançado</li>
                <li><strong>Personalidade:</strong> Proativo, observador</li>
            </ul>
            
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
