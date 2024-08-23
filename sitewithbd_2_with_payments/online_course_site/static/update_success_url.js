document.addEventListener('DOMContentLoaded', function () {
            function updateSuccessURLs() {
                const forms = document.querySelectorAll('form');

                forms.forEach(form => {
                    const statusField = form.querySelector('.status');
                    const successURLField = form.querySelector('.successURL');
                    const summaField = form.querySelector('.sum');

                    if (statusField && successURLField && summaField) {
                        const status = statusField.value;
                        const sum = summaField.value;
                        const baseURL = `https://${window.location.host}`;
                        const successURL = `${baseURL}/payment_success/${status}`;

                        successURLField.value = successURL;
                        summaField.value = sum;
                    }
                });
            }

            updateSuccessURLs();
});