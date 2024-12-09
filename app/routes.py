from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, make_response
from .models import db, Task, User
from sqlalchemy.exc import SQLAlchemyError
import csv

main = Blueprint('main', __name__)

@main.before_app_request
def load_user():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@main.route('/')
def index():
    if not g.user:
        return redirect(url_for('main.login'))

    tasks = Task.query.filter_by(user_id=g.user.id).all()
    return render_template('index.html', tasks=tasks)

@main.route('/add-task', methods=['POST'])
def add_task():
    if not g.user:
        return redirect(url_for('main.login'))

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        flash('O título da tarefa não pode estar vazio!', 'error')
        return redirect(url_for('main.index'))

    try:
        new_task = Task(title=title, description=description, user_id=g.user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Tarefa adicionada com sucesso!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao adicionar a tarefa.', 'error')

    return redirect(url_for('main.index'))

@main.route('/complete-task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if not g.user:
        return redirect(url_for('main.login'))

    task = Task.query.filter_by(id=task_id, user_id=g.user.id).first()
    if not task:
        flash('Tarefa não encontrada.', 'error')
        return redirect(url_for('main.index'))

    try:
        task.completed = not task.completed
        db.session.commit()
        status = "concluída" if task.completed else "marcada como não concluída"
        flash(f'Tarefa {status} com sucesso!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao atualizar o status da tarefa.', 'error')

    return redirect(url_for('main.index'))

@main.route('/delete-task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if not g.user:
        return redirect(url_for('main.login'))

    task = Task.query.filter_by(id=task_id, user_id=g.user.id).first()
    if not task:
        flash('Tarefa não encontrada.', 'error')
        return redirect(url_for('main.index'))

    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarefa excluída com sucesso!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao excluir a tarefa.', 'error')

    return redirect(url_for('main.index'))

@main.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if not g.user:
        return redirect(url_for('main.login'))

    task = Task.query.filter_by(id=task_id, user_id=g.user.id).first()
    if not task:
        flash('Tarefa não encontrada.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            task.title = request.form.get('title', '').strip()
            task.description = request.form.get('description', '').strip()

            if not task.title:
                flash('O título da tarefa não pode estar vazio!', 'error')
                return redirect(url_for('main.edit_task', task_id=task_id))

            db.session.commit()
            flash('Tarefa editada com sucesso!', 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Erro ao editar a tarefa.', 'error')
        return redirect(url_for('main.index'))

    return render_template('edit_task.html', task=task)

@main.route('/export-tasks', methods=['GET'])
def export_tasks():
    if not g.user:
        return redirect(url_for('main.login'))

    tasks = Task.query.filter_by(user_id=g.user.id).all()
    output = [['ID', 'Título', 'Descrição', 'Concluída']]
    for task in tasks:
        output.append([task.id, task.title, task.description, 'Sim' if task.completed else 'Não'])

    si = csv.StringIO()
    writer = csv.writer(si)
    writer.writerows(output)

    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=tasks.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not email or not password:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('Email já registrado. Tente outro.', 'error')
            return redirect(url_for('main.register'))

        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro bem-sucedido! Faça login.', 'success')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Erro ao registrar o usuário.', 'error')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login bem-sucedido.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Credenciais inválidas.', 'error')

    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu.', 'success')
    return redirect(url_for('main.login'))