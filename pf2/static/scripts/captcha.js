function captchaVerified() {
    document.getElementById("sendButton").classList.remove('feedback-button--disabled');
}


document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById("sendButton")
    if (!sendButton.classList.contains('feedback-button-disabled')) {
        const form = document.getElementById('feedbackForm');
        form.addEventListener('submit', async function (event) {
            event.preventDefault(); // Prevent default form submission behavior

            document.body.classList.add('loading');
            const formData = new FormData(form);

            try {
                const response = await fetch('/send-feedback', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.status === 'success') {
                    alert('Успешно отправлено.');
                    form.reset()
                } else {
                    alert('Возникла ошибка: ' + result.message);
                }
            } catch (error) {
                alert('При отправке письма возникла ошибка.');
            } finally {
                document.body.classList.remove('loading');
            }
        });
    }
});

