// Mobile navigation drawer
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (!menuToggle || !navLinks) return;

    const icon = menuToggle.querySelector('i');

    menuToggle.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('active');
        menuToggle.setAttribute('aria-expanded', String(isOpen));
        if (icon) {
            icon.classList.toggle('fa-bars', !isOpen);
            icon.classList.toggle('fa-times', isOpen);
        }
    });

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
            if (icon) { icon.classList.add('fa-bars'); icon.classList.remove('fa-times'); }
        });
    });
}

// Header background intensifies once the page is scrolled
function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;
    const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 12);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
}

// Smooth in-page anchor scrolling
function initAnchorScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || targetId.length < 2) return;
            const target = document.querySelector(targetId);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
            history.pushState(null, '', targetId);
        });
    });
}

// Reveal elements as they enter the viewport
function initReveal() {
    const items = document.querySelectorAll('.reveal:not(.in)');
    if (!items.length) return;

    if (!('IntersectionObserver' in window)) {
        items.forEach(el => el.classList.add('in'));
        return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    items.forEach(el => observer.observe(el));
}

// Horizontal projects scroller (home featured section)
function initProjectScroller() {
    const scroller = document.getElementById('featuredProjects');
    if (!scroller) return;
    const wrap = scroller.closest('.projects-scroller-wrap');
    const prev = wrap.querySelector('.scroller-btn.prev');
    const next = wrap.querySelector('.scroller-btn.next');

    const step = () => {
        const card = scroller.querySelector('.project-card');
        return card ? card.offsetWidth + 22 : 320;
    };

    prev && prev.addEventListener('click', () => scroller.scrollBy({ left: -step(), behavior: 'smooth' }));
    next && next.addEventListener('click', () => scroller.scrollBy({ left: step(), behavior: 'smooth' }));

    const update = () => {
        const max = scroller.scrollWidth - scroller.clientWidth;
        const atStart = scroller.scrollLeft <= 8;
        const atEnd = scroller.scrollLeft >= max - 8;
        wrap.classList.toggle('at-start', atStart);
        wrap.classList.toggle('at-end', atEnd || max <= 8);
        if (prev) prev.disabled = atStart;
        if (next) next.disabled = atEnd || max <= 8;
    };

    scroller.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
}

// Contact form -> POST /send-message
function initContactForm() {
    const contactForm = document.querySelector('.contact-form');
    if (!contactForm) return;

    contactForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const message = document.getElementById('message').value.trim();

        if (!name || !email || !message) {
            showMessage('Por favor complete todos los campos', 'error');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showMessage('Por favor ingrese un email válido', 'error');
            return;
        }

        try {
            showMessage('Enviando mensaje...', 'info');

            const response = await fetch('/send-message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, message })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('¡Mensaje enviado con éxito!', 'success');
                contactForm.reset();
            } else {
                throw new Error(data.error || 'Error al enviar el mensaje');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Hubo un error al enviar el mensaje. Por favor intente nuevamente.', 'error');
        }
    });
}

function showMessage(message, type) {
    document.querySelectorAll('.alert-message').forEach(msg => msg.remove());

    const messageDiv = document.createElement('div');
    messageDiv.className = `alert-message ${type}`;

    const icon = document.createElement('span');
    icon.className = 'message-icon';
    icon.innerHTML = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';

    const messageText = document.createElement('span');
    messageText.className = 'message-text';
    messageText.textContent = message;

    messageDiv.appendChild(icon);
    messageDiv.appendChild(messageText);

    const form = document.querySelector('.contact-form');
    form.parentNode.insertBefore(messageDiv, form);

    setTimeout(() => messageDiv.classList.add('show'), 10);
    setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initHeaderScroll();
    initAnchorScroll();
    initReveal();
    initProjectScroller();
    initContactForm();
});
