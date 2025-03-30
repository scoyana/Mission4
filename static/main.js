// 모든 폼 제출 이벤트를 처리하는 함수
function handleFormSubmit(event) {
  event.preventDefault();

  // 폼의 종류에 따라 다른 메시지 표시
  let message = "";
  const form = event.target;

  if (form.id === "post_form") {
    message = "게시글을 작성하시겠습니까?";
  } else if (form.action && form.action.includes("/edit")) {
    message = "게시글을 수정하시겠습니까?";
  } else if (form.classList.contains("delete_form")) {
    message =
      "정말로 이 게시글을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.";
  }

  // 확인 메시지 표시 후 처리
  if (confirm(message)) {
    form.submit();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const secretButton = document.getElementById("secret_button");
  if (secretButton) {
    secretButton.addEventListener("click", function () {
      document.querySelectorAll(".secret_form").forEach((element) => {
        if (element.style.display === "none" || element.style.display === "") {
          element.style.display = "block"; // 보이게 설정
        } else {
          element.style.display = "none"; // 숨기기
        }
      });
    });
  }

  // const noUserButtons = document.querySelectorAll(".no_user");
  // // 세션에 user_id가 있는지 확인
  // // HTML에 session['user_id']가 있다면 로그인된 상태
  // const isLoggedIn = document.querySelector('a[href*="logout"]') !== null;

  // // 로그인 상태라면 회원가입과 로그인 버튼을 숨김
  // if (isLoggedIn) {
  //   noUserButtons.forEach((button) => {
  //     button.style.display = "none";
  //   });
  // }

  // 프로필 이미지 미리보기
  function previewImage(input) {
    const preview = document.getElementById("image_preview");
    const previewImg = preview.querySelector("img");

    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        previewImg.src = e.target.result;
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  // 중복확인 버튼 이벤트 리스너 추가
  const checkUserIdButton = document.getElementById("checkUserId");
  if (checkUserIdButton) {
    checkUserIdButton.addEventListener("click", checkUserId);
  }
});

function checkUserId() {
  const userId = document.getElementById("userId").value;
  if (!userId) {
    alert("아이디를 입력해주세요.");
    return;
  }

  fetch("/register/check_user_id", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `userId=${encodeURIComponent(userId)}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.exists) {
        alert("이미 사용중인 아이디입니다.");
      } else {
        alert("사용 가능한 아이디입니다.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("중복 확인 중 오류가 발생했습니다.");
    });
}
