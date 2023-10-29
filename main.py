import os
import random
from dbController import *
import flask
from flask import Flask, render_template, url_for, request, session, redirect
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = '6323422092:AAGtEOJWhvjfW411obuNeIM1T_e0NP3dsNM'

menu = [
    {"name": "Главная", "url": "/"},
    {"name": "Авторизация", "url": "avto"},
    {"name": "Регистрация", "url": "reg"}
]

@app.route("/insert", methods=['POST'])
def insert():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    user_names = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()

    if (request.form["log"] == '' or request.form["pass"] == ''):
        flask.flash('Для регистрации заполните все поля')
        return redirect('/reg', code=302)
    else:
        if user_names !=None:
            flask.flash('Данный логин уже занят')
            return redirect('/reg', code=302)
        else:
            if request.form["pass"]!=request.form["passtwo"]:
                flask.flash('Пароли не совпадают')
                return redirect('/reg' , code=302)
            else:
                hashas = hashlib.md5(request.form["pass"].encode())
                passw = hashas.hexdigest()
                cursor.execute('''INSERT INTO users('login', password) VALUES(?, ?)''', (request.form["log"],passw))
                connect.commit()
                user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
                session['user_login'] =user[1]
                session['user_id'] = user[0]
                return redirect('/profile', code=302)

@app.route("/check", methods=['POST'])
def check():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
    hashas = hashlib.md5(request.form["pass"].encode())
    passw = hashas.hexdigest()

    if user!=None:
        if passw==user[2]:
            session['user_login'] = user[1]
            session['user_id'] = user[0]

            if 'adres' in session and session['adres']!=None:
                if session['type']==2:
                    ad = session['adres']
                    href = cursor.execute(
                        '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                        (session['idlink'],)).fetchone()

                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                    connect.commit()
                    session['idlink'] = None
                    session['adid'] = None
                    session['type'] = None
                    session['adres']=None
                    session['user_login'] = None
                    session['user_id'] = None
                    connect.close()
                    return redirect(f"{ad}")
                else:
                    if session['adid']==session['user_id']:
                        ad = session['adres']
                        href = cursor.execute(
                            '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                            (session['idlink'],)).fetchone()

                        cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                        connect.commit()
                        session['idlink'] = None
                        session['adid'] = None
                        session['type'] = None
                        session['adres'] = None
                        session['user_login'] = None
                        session['user_id'] = None
                        connect.commit()
                        connect.close()
                        return redirect(f"{ad}")
                    else:
                        session['user_login']=None
                        session['user_id']=None
                        session['adid'] = None
                        session['type'] = None
                        session['adres'] = None
                        connect.close()
                        return redirect('/no', code=302)
            else:
                connect.close()
                return redirect('/profile', code=302)
        else:
            flask.flash('Пароль не подходит')
            connect.close()
            return redirect('/avto', code=302)
    else:
        flask.flash('такого аккаунта не существует')
        connect.close()
        return redirect('/avto', code=302)

@app.route("/delete", methods=['POST'])
def delete():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    cursor.execute('''DELETE FROM 'links' WHERE id = ?''', (request.form['idd'],))
    connect.commit()
    connect.close()
    return redirect('/profile', code=302)

@app.route("/short", methods=['POST'])
def short():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()

    if request.form['href'] == '':
        session['psevdo'] = 1
        flask.flash(f'Укажите ссылку')
        connect.close()
        return redirect('/', code=302)
    else:
        if request.form['psevdo'] == '':
            user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
        else:
            name_psevdo = cursor.execute('''SELECT * FROM 'links' WHERE hreflink=? ''', (request.form['psevdo'],)).fetchall()
            if name_psevdo !=[]:
                session['psevdo']=1
                flask.flash(f'Данный псевдоним занят')
                connect.close()
                return redirect('/', code=302)
            else:
                user_adress = request.form['psevdo']

        type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

        if request.form['how']==type[0][0]:
            if ('user_id' in session and session['user_id']!=None):
                cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how'],0))
                connect.commit()
                flask.flash(f'{user_adress}')
                connect.close()
                return redirect('/', code=302)
            else:
                cursor.execute('''INSERT INTO links('link', 'hreflink', 'link_type_id', 'user_id', 'count') VALUES(?, ?, ?, ?)''', (request.form['href'], user_adress, request.form['how'], None, 0))
                connect.commit()
                flask.flash(f'{user_adress}')
                connect.close()
                return redirect('/', code=302)

        elif request.form['how']==type[1][0]:
            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how'], 0))
            connect.commit()
            flask.flash(f'{user_adress}')
            connect.close()
            return redirect('/', code=302)
        else:
            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how'], 0))
            connect.commit()
            flask.flash(f'{user_adress}')
            connect.close()
            return redirect('/', code=302)

@app.route("/href/<hashref>")
def direct(hashref):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    href = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (hashref, ) ).fetchone()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

    if href[4]==type[0][0]:
        cursor.execute('''UPDATE links SET count = ? WHERE id=?''',(href[5]+1, href[0]))
        connect.commit()
        connect.close()
        return redirect(f"{href[1]}")

    elif href[4]==type[1][0]:
        if 'user_id' in session and session['user_id']!=None:
            cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
            connect.commit()
            connect.close()
            return redirect(f"{href[1]}")
        else:
            session['adres'] = href[1]
            session['type'] = 2
            session['adid'] = href[3]
            session['idlink'] = href[0]
            connect.close()
            return redirect('/avto', code=302)

    elif href[4]==type[2][0]:
        if 'user_id' in session and session['user_id'] != None:
            if (href[3]==session['user_id']):
                cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                connect.commit()
                connect.close()
                return redirect(f"{href[1]}")
            else:
                connect.close()
                return redirect('/no', code=302)
        else:
            session['adres'] = href[1]
            session['type'] = 3
            session['adid'] = href[3]
            session['idlink'] = href[0]
            connect.close()
            return redirect('/avto', code=302)

@app.route("/logout", methods=['POST'])
def logout():
    session['user_login']=None
    session['user_id'] = None
    return redirect('/', code=302)

@app.route("/updatehref", methods=['POST'])
def updatehref():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    name = cursor.execute('''SELECT * FROM 'links' WHERE hreflink = ? ''', (request.form["hreflink"],)).fetchone()

    if (name !=None):
        if (name[3]==session['user_id']):
            if (request.form["types"]!='0'):
                cursor.execute('''UPDATE links SET link_type_id = ? WHERE id = ?''', (request.form["types"],request.form["idlink"]))
                connect.commit()
                flask.flash('Все успешно изменено')
                connect.close()
                return redirect('/profile', code=302)
            else:
                connect.close()
                return redirect('/profile', code=302)
        else:
            flask.flash(f'Имя {request.form["hreflink"]} уже занято')
            connect.close()
            return redirect('/profile', code=302)
    else:
        if (request.form["types"]!='0'):
            cursor.execute('''UPDATE links SET hreflink = ?, link_type_id = ? WHERE id = ?''',(request.form["hreflink"], request.form["types"], request.form["idlink"]))
            connect.commit()
            flask.flash('Все успешно изменено')
            connect.close()
            return redirect('/profile', code=302)
        else:
            cursor.execute('''UPDATE links SET hreflink = ? WHERE id = ?''',(request.form["hreflink"], request.form["idlink"]))
            connect.commit()
            flask.flash('Все успешно изменено')
            connect.close()
            return redirect('/profile', code=302)

@app.route("/")
def index():
    if 'psevdo' in session and session['psevdo'] !=1:
        baselink = request.host_url
    else:
        baselink = ''
    session['psevdo']=0
    if 'user_login' in session and session['user_login'] !=None:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},
        ]
    else:
        session['user_login']=None
        session['user_id']=None
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": "Авторизация", "url": "avto"},
            {"name": "Регистрация", "url": "reg"}
        ]
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
    connect.close()
    return render_template('index.html', title="Главная", menu=menu, type=type, baselink=baselink)

@app.route("/reg")
def reg():
    return render_template('reg.html', title="Регистрация", menu=menu)

@app.route("/avto")
def avto():
    return render_template('avto.html', title="Авторизация", menu=menu)

@app.route("/no")
def no():
    return render_template('no.html', title="Доступ ограничен")

@app.route("/profile")
def profile():
    baselink = request.host_url
    if 'user_login' in session and session['user_login']!=None:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},
        ]
    else:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": "Авторизация", "url": "avto"},
            {"name": "Регистрация", "url": "reg"}
        ]
        return render_template('index.html', title="Главная", menu=menu)

    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
    connect.close()
    return render_template('profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)


if __name__ =="__main__":
    app.run(debug=True)