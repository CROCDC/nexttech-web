class PantechFooter extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                .pantech-footer {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 1rem;
                    font-family: Arial, sans-serif;
                    cursor: pointer;
                    transition: opacity 0.3s ease;
                }
                
                .pantech-footer:hover {
                    opacity: 0.8;
                }
                
                .pantech-footer a {
                    display: flex;
                    align-items: center;
                    text-decoration: none;
                    color: inherit;
                }
                
                .pantech-footer img {
                    height: 30px;
                    margin-right: 10px;
                }
                
                .pantech-footer span {
                    color: inherit;
                    font-size: 14px;
                }
            </style>
            <div class="pantech-footer">
                <a href="https://pantech.solutions" target="_blank" rel="noopener noreferrer">
                    <img src="https://pantech.solutions/static/assets/favicon.svg" alt="Pantech Logo">
                    <span>Creado por Pantech Solutions</span>
                </a>
            </div>
        `;
    }
}

customElements.define('pantech-footer', PantechFooter); 