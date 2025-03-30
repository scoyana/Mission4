from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database.db import db
import os
from datetime import datetime


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        userId = request.form['userId'].lower()
        password = request.form['password']
        user = db.execute_query("SELECT * FROM users WHERE userId = %s AND password = %s", (userId, password), fetchone=True)
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='아이디 또는 비밀번호가 일치하지 않습니다.')
    return render_template('login.html')

@auth_blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@auth_blueprint.route('/find_id', methods=['POST', 'GET'])
def find_id():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        user_ids = db.execute_query("SELECT * FROM users WHERE name = %s AND email = %s", (name, email))
        if user_ids:
            return render_template('find_id.html', user_ids=user_ids)
        else:
            return render_template('find_id.html', error='이름 또는 이메일이 일치하지 않습니다.')
    return render_template('find_id.html')

@auth_blueprint.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        try:
            userId = request.form['userId']
            find_password = request.form.get('find_password', '')
            find_password_answer = request.form.get('find_password_answer', '')
            
            user = db.execute_query(
                """SELECT * FROM users 
                   WHERE userId = %s 
                   AND find_password = %s 
                   AND find_password_answer = %s""",
                (userId, find_password, find_password_answer),
                fetchone=True
            )
            
            if user:
                return redirect(url_for('auth.reset_password', user_id=user['id']))
            else:
                return render_template('find_password.html', 
                                     error='입력하신 정보와 일치하는 계정을 찾을 수 없습니다.')
        except KeyError:
            return render_template('find_password.html', 
                                 error='모든 필드를 입력해주세요.')
    
    return render_template('find_password.html')

@auth_blueprint.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            return render_template('reset_password.html', 
                                 user_id=user_id,
                                 error='비밀번호가 일치하지 않습니다.')
        
        db.execute_query(
            "UPDATE users SET password = %s WHERE id = %s",
            (new_password, user_id),
            commit=True
        )
        
        
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', user_id=user_id)

@auth_blueprint.route('/myprofile')
def myprofile():
    user = db.execute_query("SELECT * FROM users WHERE id = %s", (session['user_id'],), fetchone=True)
    return render_template('myprofile.html', user=user)

@auth_blueprint.route('/profile/<int:user_id>')
def profile(user_id):
    user = db.execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    return render_template('profile.html', user=user)

@auth_blueprint.route('/modify_user', methods=['GET', 'POST'])
def modify_user():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        user = db.execute_query("SELECT * FROM users WHERE id = %s", (session['user_id'],), fetchone=True)
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        school = request.form['school']
        find_password = request.form['find_password']
        find_password_answer = request.form['find_password_answer']

        db.execute_query(
            "UPDATE users SET password = %s, name = %s, school = %s, email = %s, find_password = %s, find_password_answer = %s WHERE id = %s",
            (password, name, school, email, find_password, find_password_answer, session['user_id']),
            commit=True
        )
        return redirect(url_for('auth.myprofile'))
    
    user = db.execute_query("SELECT * FROM users WHERE id = %s", (session['user_id'],), fetchone=True)
    return render_template('modify_user.html', user=user)

@auth_blueprint.route('/delete_user', methods=['POST'])
def delete_user():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        db.execute_query("DELETE FROM users WHERE id = %s", (session['user_id'],), commit=True)
        session.pop('user_id', None)
        
        return redirect(url_for('home'))

@auth_blueprint.route('/update_profile_image', methods=['POST'])
def update_profile_image():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '로그인이 필요합니다.'})
    
    profile_image = request.files['profile_image']
    if profile_image:
        # 이전 프로필 이미지 삭제 (기본 이미지는 제외)
        user = db.execute_query("SELECT profile_image FROM users WHERE id = %s", 
                              (session['user_id'],), fetchone=True)
        if user['profile_image'] != 'default.png':
            old_image_path = os.path.join('static', 'img', 'profile', user['profile_image'])
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # 새 이미지 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{timestamp}_{profile_image.filename}"
        profile_image_path = os.path.join('static', 'img', 'profile')
        
        if not os.path.exists(profile_image_path):
            os.makedirs(profile_image_path)
        
        profile_image.save(os.path.join(profile_image_path, new_filename))
        
        # DB 업데이트
        db.execute_query(
            "UPDATE users SET profile_image = %s WHERE id = %s",
            (new_filename, session['user_id']),
            commit=True
        )
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': '이미지 업로드에 실패했습니다.'})
