// Google Analytics
(function() {
    // Cargar el script de Google Analytics
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-EG3G4YZQ7Z';
    document.head.appendChild(script);

    // Configurar dataLayer y función gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-EG3G4YZQ7Z');
})(); 