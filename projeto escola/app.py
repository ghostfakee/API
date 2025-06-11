from flask import Flask, render_template
import requests
from flask import make_response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from flask import request, redirect, url_for

app = Flask(__name__)

API_URL = "http://localhost:3001"

@app.route('/')
def home():
    return '<h2>Sistema Escola - Acesse/alunos, /cursos ou /matrculas</h2>'

@app.route('/alunos')
def listar_alunos():
    try:
        response = requests.get(f"{API_URL}/Aluno")
        alunos = response.json()
        return render_template('alunos.html', alunos=alunos)
    except Exception as e:
        return f"erro ao carregar alunos: {e}"

@app.route('/cursos')
def listar_cursos():
    try:
        response = requests.get(f"{API_URL}/curso")
        cursos = response.json()
        return render_template('cursos.html', cursos=cursos)
    except Exception as e:
        return f"erro ao carregar cursos: {e}"
    
@app.route('/matriculas')
def listar_matriculas():
    try:
        # Consumo das APIs
        alunos_response = requests.get(f"{API_URL}/Aluno")
        cursos_response = requests.get(f"{API_URL}/curso")
        matriculas_response = requests.get(f"{API_URL}/alino_curso")

        alunos = alunos_response.json()
        cursos = cursos_response.json()
        matriculas = matriculas_response.json()

        # Índice rápido por ID
        aluno_por_id = {a['id']: a['title'] for a in alunos}
        curso_por_id = {c['id']: c['text'] for c in cursos}


        lista_matriculas = []

        for m in matriculas:
            nome_aluno = aluno_por_id.get(m['AlunoId'], 'Desconhecido')
            nome_curso = curso_por_id.get(m['cursoId'], 'Desconhecido')
            lista_matriculas.append({
                'aluno': nome_aluno,
                'curso': nome_curso
            })

        return render_template('matriculas.html', matriculas=lista_matriculas)

    except Exception as e:
        return f"erro ao carregar matrículas: {e}"
    
@app.route('/relatorio')
def gerar_relatorio():
    try:
        alunos = requests.get(f"{API_URL}/Aluno").json()
        cursos = requests.get(f"{API_URL}/curso").json()
        matriculas = requests.get(f"{API_URL}/alino_curso").json()

        aluno_por_id = {a['id']: a['title'] for a in alunos}
        curso_por_id = {c['id']: c['text'] for c in cursos}

        # Criar PDF na memória
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setTitle("Relatório de Matrículas")
        width, height = A4

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, height - 50, "Relatório de Matrículas")

        pdf.setFont("Helvetica", 12)
        y = height - 100
        for m in matriculas:
            aluno = aluno_por_id.get(m['AlunoId'], 'Desconhecido')
            curso = curso_por_id.get(m['cursoId'], 'Desconhecido')
            linha = f"{aluno} está matriculado em {curso}"
            pdf.drawString(50, y, linha)
            y -= 20
            if y < 50:
                pdf.showPage()
                y = height - 50

        pdf.save()
        buffer.seek(0)

        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
        return response

    except Exception as e:
        return f"Erro ao gerar relatório: {e}"
    
@app.route('/alunos/novo', methods=['GET', 'POST'])
def novo_aluno():
    if request.method == 'POST':
        novo = {
            "title": request.form['title'],
            "views": int(request.form['views'])
        }
        requests.post(f"{API_URL}/Aluno", json=novo)
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', aluno=None)

# Editar aluno
@app.route('/alunos/editar/<id>', methods=['GET', 'POST'])
def editar_aluno(id):
    if request.method == 'POST':
        atualizado = {
            "title": request.form['title'],
            "views": int(request.form['views'])
        }
        requests.put(f"{API_URL}/Aluno/{id}", json=atualizado)
        return redirect(url_for('listar_alunos'))
    aluno = requests.get(f"{API_URL}/Aluno/{id}").json()
    return render_template('aluno_form.html', aluno=aluno)

# Deletar aluno
@app.route('/alunos/deletar/<id>', methods=['POST'])
def deletar_aluno(id):
    requests.delete(f"{API_URL}/Aluno/{id}")
    return redirect(url_for('listar_alunos'))


if __name__ == '__main__':
    app.run(debug=True)
