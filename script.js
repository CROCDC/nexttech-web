// Menú móvil
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    menuToggle.querySelector('i').classList.toggle('fa-bars');
    menuToggle.querySelector('i').classList.toggle('fa-times');
});

// Cerrar menú al hacer clic en un enlace
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        menuToggle.querySelector('i').classList.add('fa-bars');
        menuToggle.querySelector('i').classList.remove('fa-times');
    });
});

// Animación suave del scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Animación del header al hacer scroll
let lastScroll = 0;
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        header.classList.remove('scroll-up');
        return;
    }
    
    if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
        header.classList.remove('scroll-up');
        header.classList.add('scroll-down');
    } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
        header.classList.remove('scroll-down');
        header.classList.add('scroll-up');
    }
    lastScroll = currentScroll;
});

// Función para inicializar el menú móvil
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (!menuToggle || !navLinks) return;
    
    menuToggle.addEventListener('click', () => {
        const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
        menuToggle.setAttribute('aria-expanded', !isExpanded);
        
        navLinks.classList.toggle('active');
        menuToggle.querySelector('i').classList.toggle('fa-bars');
        menuToggle.querySelector('i').classList.toggle('fa-times');
    });

    // Cerrar menú al hacer click en un enlace
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            menuToggle.querySelector('i').classList.add('fa-bars');
            menuToggle.querySelector('i').classList.remove('fa-times');
            menuToggle.setAttribute('aria-expanded', 'false');
        });
    });
}

// Función para inicializar la animación del scroll
function initScrollAnimation() {
    // Animación suave del scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
                
                // Actualizar la URL sin recargar la página
                history.pushState(null, '', targetId);
                
                // Actualizar el estado activo de los enlaces
                document.querySelectorAll('.nav-links a').forEach(link => {
                    link.removeAttribute('aria-current');
                });
                this.setAttribute('aria-current', 'page');
            }
        });
    });

    // Animación del header al hacer scroll
    let lastScroll = 0;
    const header = document.querySelector('.header');

    if (header) {
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll <= 0) {
                header.classList.remove('scroll-up');
                return;
            }
            
            if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
                header.classList.remove('scroll-up');
                header.classList.add('scroll-down');
            } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
                header.classList.remove('scroll-down');
                header.classList.add('scroll-up');
            }
            lastScroll = currentScroll;
        });
    }
}

// Services carousel functionality
function initServicesCarousel() {
    const carousel = document.querySelector('.services-carousel');
    const prevButton = document.querySelector('.carousel-button.prev');
    const nextButton = document.querySelector('.carousel-button.next');
    const cards = document.querySelectorAll('.service-card');
    
    if (!carousel || !prevButton || !nextButton || cards.length === 0) {
        console.warn('Elementos del carrusel no encontrados');
        return;
    }
    
    let currentIndex = 0;
    const cardWidth = cards[0].offsetWidth;
    const gap = 32; // 2rem gap
    let autoSlideInterval;

    function updateCarousel() {
        const offset = currentIndex * (cardWidth + gap);
        carousel.scrollTo({
            left: offset,
            behavior: 'smooth'
        });
        
        // Actualizar atributos ARIA para accesibilidad
        cards.forEach((card, index) => {
            if (index === currentIndex) {
                card.setAttribute('aria-hidden', 'false');
                card.setAttribute('tabindex', '0');
            } else {
                card.setAttribute('aria-hidden', 'true');
                card.setAttribute('tabindex', '-1');
            }
        });
    }

    function nextSlide() {
        currentIndex++;
        if (currentIndex >= cards.length) {
            currentIndex = 0;
        }
        updateCarousel();
    }

    function prevSlide() {
        currentIndex--;
        if (currentIndex < 0) {
            currentIndex = cards.length - 1;
        }
        updateCarousel();
    }

    function getVisibleCards() {
        if (window.innerWidth >= 1024) return 3;
        if (window.innerWidth >= 768) return 2;
        return 1;
    }

    function startAutoSlide() {
        stopAutoSlide(); // Limpiar intervalo existente
        autoSlideInterval = setInterval(nextSlide, 5000); // Cambiar cada 5 segundos
    }

    function stopAutoSlide() {
        if (autoSlideInterval) {
            clearInterval(autoSlideInterval);
        }
    }

    // Event listeners
    nextButton.addEventListener('click', () => {
        nextSlide();
        stopAutoSlide();
        startAutoSlide();
    });

    prevButton.addEventListener('click', () => {
        prevSlide();
        stopAutoSlide();
        startAutoSlide();
    });

    // Pausar auto-slide cuando el mouse está sobre el carrusel
    carousel.addEventListener('mouseenter', stopAutoSlide);
    carousel.addEventListener('mouseleave', startAutoSlide);

    // Update on window resize
    window.addEventListener('resize', () => {
        currentIndex = 0;
        updateCarousel();
        stopAutoSlide();
        startAutoSlide();
    });

    // Inicializar atributos ARIA
    cards.forEach((card, index) => {
        if (index === 0) {
            card.setAttribute('aria-hidden', 'false');
            card.setAttribute('tabindex', '0');
        } else {
            card.setAttribute('aria-hidden', 'true');
            card.setAttribute('tabindex', '-1');
        }
    });

    // Iniciar auto-slide
    startAutoSlide();
}

// Función para manejar el formulario de contacto
function initContactForm() {
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validación básica
            const nombre = document.getElementById('nombre').value.trim();
            const email = document.getElementById('email').value.trim();
            const mensaje = document.getElementById('mensaje').value.trim();
            
            if (!nombre || !email || !mensaje) {
                alert('Por favor, completa todos los campos');
                return;
            }
            
            // Validación de email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Por favor, ingresa un email válido');
                return;
            }
            
            // Aquí puedes agregar la lógica para enviar el formulario
            alert('¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.');
            contactForm.reset();
        });
    }
}

// Función para mejorar el rendimiento
function initPerformanceOptimizations() {
    // Lazy loading para imágenes
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback para navegadores que no soportan lazy loading nativo
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initServicesCarousel();
    initMobileMenu();
    initScrollAnimation();
    initContactForm();
    initPerformanceOptimizations();
}); 