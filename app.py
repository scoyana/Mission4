from flask import Flask, request, url_for, redirect, render_template, session, send_file, flash
from database.db import db
from register.views import register_blueprint
from auth.views import auth_blueprint
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['FLASH_MESSAGES'] = True

db.init_db()

app.register_blueprint(register_blueprint, url_prefix='/register')
app.register_blueprint(auth_blueprint, url_prefix='/auth')


# 게시판 메인 화면
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    # 전체 게시글 수 조회
    total_posts = db.execute_query("SELECT COUNT(*) as count FROM post", fetchone=True)['count']
    total_pages = (total_posts + per_page - 1) // per_page
    
    # 페이지네이션된 게시글 조회
    posts = db.execute_query("""
        SELECT p.*, u.userId 
        FROM post p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    
    # 사용자 정보 조회
    user = None
    if 'user_id' in session:
        user = db.execute_query(
            "SELECT * FROM users WHERE id = %s",
            (session['user_id'],),
            fetchone=True
        )
    
    return render_template('index.html', 
                         posts=posts, 
                         current_page=page,
                         total_pages=total_pages,
                         user=user)

# 게시판 작성
@app.route('/post', methods=['POST', 'GET'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        secret = request.form.get('secret', None)
        if secret == '':
            secret = None
        now_str = db.get_current_time()
        user_id = session['user_id']
        
        # 게시글 저장
        db.execute_query(
            "INSERT INTO post(title, content, created_at, secret, user_id) VALUES(%s, %s, %s, %s, %s)",
            (title, content, now_str, secret, user_id),
            commit=True
        )
        post_id = db.cursor.lastrowid
        
        # 파일 업로드 처리
        files = request.files.getlist('files')
        if files and files[0].filename:  # 파일이 있는 경우에만 처리
            # 파일 저장 디렉토리 생성
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            for file in files:
                if file.filename:
                    # 파일명에 타임스탬프 추가
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{file.filename}"
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    
                    # DB에 파일 정보 저장
                    db.execute_query(
                        """INSERT INTO post_files(post_id, original_filename, stored_filename, 
                           file_size, created_at) 
                           VALUES(%s, %s, %s, %s, %s)""",
                        (post_id, file.filename, filename,
                         os.path.getsize(file_path), now_str),
                        commit=True
                    )
        
        return redirect(url_for('home'))
    return render_template('post.html')

@app.route('/download/<int:file_id>')
def download_file(file_id):
    file_info = db.execute_query(
        "SELECT * FROM post_files WHERE id = %s",
        (file_id,),
        fetchone=True
    )
    
    if file_info:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info['stored_filename'])
        if os.path.exists(file_path):
            # 다운로드 카운트 증가
            db.execute_query(
                "UPDATE post_files SET download_count = download_count + 1 WHERE id = %s",
                (file_id,),
                commit=True
            )
            return send_file(
                file_path,
                as_attachment=True,
                download_name=file_info['original_filename']
            )
    return "파일을 찾을 수 없습니다.", 404

# 게시글 상세보기
@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def view_post(post_id):
    # 게시글 조회
    post = db.execute_query(
        "SELECT p.*, u.userId FROM post p JOIN users u ON p.user_id = u.id WHERE p.id = %s",
        (post_id,),
        fetchone=True
    )
    
    if not post:
        flash('게시글을 찾을 수 없습니다.', 'error')
        return redirect(url_for('home'))
    
    db.execute_query("UPDATE post SET views = views + 1 WHERE id = %s", (post_id,), commit=True)
    
    # 첨부 파일 정보 조회
    files = db.execute_query(
        "SELECT * FROM post_files WHERE post_id = %s ORDER BY created_at",
        (post_id,)
    )
    
    return render_template('view_post.html', post=post, files=files)

# 비밀글 확인
@app.route('/post/<int:post_id>/check', methods=['POST', 'GET'])
def post_check(post_id):
    if request.method == 'POST':
        post = db.execute_query("SELECT * FROM post WHERE id = %s", (post_id,), fetchone=True)
        if post['secret'] == request.form['secret']:
            return redirect(url_for('view_post', post_id=post_id))
        else:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('post_check.html', post_id=post_id)
        
    return render_template('post_check.html', post_id=post_id)

# 게시글 수정
@app.route('/post/<int:post_id>/edit', methods=['POST', 'GET'])
def edit_post(post_id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        secret = request.form.get('secret', None)
        if secret == '':
            secret = None
            
        db.execute_query(
            "UPDATE post SET title = %s, content = %s, secret = %s WHERE id = %s",
            (title, content, secret, post_id), 
            commit=True
        )
        flash('게시글이 수정되었습니다.', 'success')
        return redirect(url_for('view_post', post_id=post_id))
        
    return render_template('edit_post.html', post=post)

# 게시글 삭제
@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    
    
    # 첨부파일 삭제
    files = db.execute_query(
        "SELECT stored_filename FROM post_files WHERE post_id = %s",
        (post_id,)
    )
    
    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file['stored_filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # 데이터베이스에서 파일 정보 삭제
    db.execute_query(
        "DELETE FROM post_files WHERE post_id = %s",
        (post_id,),
        commit=True
    )
    
    # 게시글 삭제
    db.execute_query(
        "DELETE FROM post WHERE id = %s",
        (post_id,),
        commit=True
    )
    flash('게시글이 삭제되었습니다.', 'success')
    return redirect(url_for('home'))

# 검색
@app.route('/search', methods=['POST', 'GET'])
def search():
    # GET 요청 처리를 위해 form과 args 모두 확인
    keyword = request.form.get('keyword') or request.args.get('keyword', '')
    search_option = request.form.get('search_option') or request.args.get('search_option', 'title')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    # 기본 쿼리 설정
    count_query = "SELECT COUNT(*) as count FROM post p JOIN users u ON p.user_id = u.id"
    base_query = """
        SELECT p.*, u.userId 
        FROM post p 
        JOIN users u ON p.user_id = u.id
    """
    where_clause = ""
    params = []
    
    # 검색 조건에 따른 쿼리 수정
    if keyword:
        if search_option == 'title':
            where_clause = " WHERE p.title LIKE %s"
            params = ['%' + keyword + '%']
        elif search_option == 'content':
            where_clause = " WHERE p.content LIKE %s"
            params = ['%' + keyword + '%']
        elif search_option == 'user':
            where_clause = " WHERE u.userId LIKE %s"
            params = ['%' + keyword + '%']
        elif search_option == 'all':
            where_clause = " WHERE p.title LIKE %s OR p.content LIKE %s OR u.userId LIKE %s"
            params = ['%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%']
    
    # 전체 게시글 수 조회
    total_posts = db.execute_query(count_query + where_clause, params, fetchone=True)['count']
    total_pages = (total_posts + per_page - 1) // per_page
    
    # 페이지네이션된 검색 결과 조회
    final_query = base_query + where_clause + " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
    search_params = params + [per_page, offset]
    posts = db.execute_query(final_query, search_params)
    
    # 사용자 정보 조회
    user = None
    if 'user_id' in session:
        user = db.execute_query(
            "SELECT * FROM users WHERE id = %s",
            (session['user_id'],),
            fetchone=True
        )
    
    return render_template('index.html', 
                         posts=posts,
                         keyword=keyword,
                         search_option=search_option,
                         current_page=page,
                         total_pages=total_pages,
                         user=user)

if __name__ == '__main__':
    app.run(debug=True)
