# Mission4_Flask_board
## Flask, MySQL 을 활용한 게시판 만들기 ver.2

이 프로젝트는 Flask와 pymysql을 이용하여 간단한 게시판을 구현한 미니 프로젝트다.
글 생성, 읽기, 업데이트(수정), 삭제 그리고 기준 별 검색 기능을 포함하고 있으며, MySQL을 사용하여 데이터를 관리했다.
기존의 Mission3_Flask_board프로젝트의 CRUD 구현의 확장 버전이다.

### 기존 기능
- [x] 글 생성
- [x] 글 읽기
- [x] 글 업데이트(수정)
- [x] 글 삭제
- [x] 글 제목, 내용, 통합 검색
- [x] 조회 수 표시

+ 회원가입, 로그인, 개인 프로필등 유저관리 기능을 추가 했다.
+ 파일 업로드, 다운로드등의 기능도 구현했지만 **보안적인 측면에서 굉장히 취약**할 것으로 예상된다.

### 기술 스택
- Python >= 3.8
- Flask
- pymysql
- MySQL 8.0
- HTML, CSS, JavaScript

### 가상환경 생성 및 활성화
python -m venv venv  

source venv/bin/activate  # Windows는 venv\Scripts\activate

### 필수 패키지 설치
pip install -r requirements.txt
