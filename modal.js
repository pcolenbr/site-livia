// Form validation for WhatsApp modal
document.addEventListener('DOMContentLoaded', function() {    
    
    const nomeInput = document.getElementById('nome');
    const telefoneInput = document.getElementById('telefone');
    const submitButton = document.querySelector('#whatsAppModal .btn-agendar-consulta');
    
    // Apply mask to telefone field for Brazilian format: (xx) x xxxx-xxxx
    const phoneMask = IMask(telefoneInput, {
        mask: '(00) 0 0000-0000',
        lazy: true
    });
    console.log('Modal.js: Phone mask applied');

    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            } else {
                event.preventDefault()

                const phoneNumber = phoneMask.unmaskedValue;
                const formattedPhone = '553184617174'; // Format for WhatsApp
                
                const now = new Date();
                const date = now.toISOString().split('T')[0]; // YYYY-MM-DD
                const time = now.toTimeString().split(' ')[0]; // HH:MM:SS

                const formData = new FormData();
                formData.append('name', nomeInput.value.trim());
                formData.append('phone', phoneNumber);
                formData.append('date', date);
                formData.append('time', time);

                const message = `Olá! Meu nome é ${nomeInput.value.trim()}. Gostaria de saber mais sobre a consulta da Dra. Livia`;
                const whatsappURL = `https://wa.me/${formattedPhone}?text=${encodeURIComponent(message)}`;

                console.log('Modal.js: Sending lead data to API in the background');
                fetch('https://draliviamacedo.com.br/save.php', {
                    method: 'POST',
                    body: formData
                })

                gtag_report_conversion();
                window.open(whatsappURL, '_blank');

                const modal = bootstrap.Modal.getInstance(document.getElementById('whatsAppModal'));
                if (modal) {
                    modal.hide();
                }
            }

            form.classList.add('was-validated')
        }, false)
    })
    
   
    
    
    console.log('Modal.js: Initialization complete');
});