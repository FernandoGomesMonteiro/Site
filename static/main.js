document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;

    alert(`Obrigado, ${name}! Entraremos em contato com você pelo e-mail ${email}.`);
});