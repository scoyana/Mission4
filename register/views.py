from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from database.db import db
import os
import uuid

register_blueprint = Blueprint('register', __name__)

DEFAULT_PROFILE_IMAGE = 'default.png'

@register_blueprint.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        try:
            userId = request.form['userId'].lower()
            password = request.form['password']
            email = request.form['email']
            name = request.form['name']
            school = request.form['school']
            find_password = request.form.get('find_password', '')
            find_password_answer = request.form.get('find_password_answer', '')

            profile_image = request.files.get('profile_image')
            if profile_image and profile_image.filename:
                # 새로운 고유 파일명 생성 (원본 확장자 유지)
                file_extension = os.path.splitext(profile_image.filename)[1]
                filename = str(uuid.uuid4()) + file_extension
                
                # 프로필 이미지 저장 디렉토리 경로
                profile_image_path = os.path.join('static', 'img', 'profile')
                
                # 디렉토리가 없으면 생성
                os.makedirs(profile_image_path, exist_ok=True)
                
                # 파일 저장
                file_path = os.path.join(profile_image_path, filename)
                profile_image.save(file_path)
                profile_image_filename = filename
            else:
                # 프로필 이미지 미제공 시 기본 이미지 사용
                profile_image_filename = DEFAULT_PROFILE_IMAGE
            
            # 데이터베이스에 사용자 정보 저장
            now_str = db.get_current_time()
            db.execute_query(
                "INSERT INTO users (userId, password, name, school, email, profile_image, find_password, find_password_answer, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (userId, password, name, school, email, profile_image_filename, find_password, find_password_answer, now_str),
                commit=True
            )
            return render_template('register_success.html')
        except KeyError as e:
            return render_template('register.html', error='모든 필드를 입력해주세요.')
    
    return render_template('register.html')

@register_blueprint.route('/modify_user', methods=['POST'])
def modify_user():
    userId = request.form['userId']
    password = request.form['password']
    email = request.form['email']
    name = request.form['name']
    school = request.form['school']
    find_password = request.form['find_password']
    find_password_answer = request.form['find_password_answer']

    db.execute_query("UPDATE users SET password = %s, name = %s, school = %s, email = %s, find_password = %s, find_password_answer = %s WHERE userId = %s", (password, name, school, email, find_password, find_password_answer, userId), commit=True)
    return redirect(url_for('auth.myprofile'))


@register_blueprint.route('/delete_user', methods=['POST'])
def delete_user():
    userId = request.form['userId']
    db.execute_query("DELETE FROM users WHERE userId = %s", (userId,), commit=True)
    return redirect(url_for('auth.login'))

@register_blueprint.route('/check_user_id', methods=['POST'])
def check_user_id():
    userId = request.form['userId'].lower()
    user = db.execute_query("SELECT * FROM users WHERE userId = %s", (userId,), fetchone=True)
    return jsonify({'exists': user is not None})
