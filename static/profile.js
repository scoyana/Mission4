function triggerFileInput() {
    document.getElementById('profile_image_input').click();
}

function uploadImage(input) {
    if (input.files && input.files[0]) {
        const formData = new FormData();
        formData.append('profile_image', input.files[0]);

        fetch('/auth/update_profile_image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 이미지 미리보기 업데이트
                document.querySelector('.profile-image').src = URL.createObjectURL(input.files[0]);
                // 페이지 새로고침
                setTimeout(() => location.reload(), 500);
            } else {
                alert('이미지 업로드에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('이미지 업로드 중 오류가 발생했습니다.');
        });
    }
} 