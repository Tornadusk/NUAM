// Agrega botón mostrar/ocultar para el campo password en Admin Usuarios
(function() {
  function setupToggle() {
    var input = document.querySelector('input[name="password"]');
    if (!input || input.dataset.toggleReady) return;
    input.dataset.toggleReady = '1';

    var wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '👁';
    btn.title = 'Mostrar/Ocultar';
    btn.style.position = 'absolute';
    btn.style.right = '8px';
    btn.style.top = '50%';
    btn.style.transform = 'translateY(-50%)';
    btn.style.border = 'none';
    btn.style.background = 'transparent';
    btn.style.cursor = 'pointer';
    wrapper.appendChild(btn);

    btn.addEventListener('click', function() {
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupToggle);
  } else {
    setupToggle();
  }
})();


