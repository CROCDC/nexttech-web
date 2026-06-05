class NexttechFooter extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    background: transparent;
                }
                .nexttech-footer {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 1rem;
                    font-family: Arial, sans-serif;
                    cursor: pointer;
                    transition: opacity 0.3s ease;
                    background: transparent;
                }
                
                .nexttech-footer:hover {
                    opacity: 0.8;
                }
                
                .nexttech-footer a {
                    display: flex;
                    align-items: center;
                    text-decoration: none;
                    color: inherit;
                }
                
                .nexttech-footer img {
                    height: 30px;
                    margin-right: 10px;
                }
                
                .nexttech-footer span {
                    color: inherit;
                    font-size: 14px;
                }
            </style>
            <div class="nexttech-footer">
                <a href="https://nexttech.com.ar" target="_blank" rel="noopener noreferrer">
                    <img src="https://nexttech.com.ar/static/assets/favicon.svg" alt="Next Tech Logo">
                    <span>Creado por Next Tech</span>
                </a>
            </div>
        `;

        // The umami tracker lives in the host page; the footer is style-isolated in
        // Shadow DOM, so data-umami-event auto-tracking does not reach it. Use the JS
        // API instead. `source` lets each site that embeds the footer tag its own
        // clicks so they are distinguishable in the Umami dashboard.
        const source = this.getAttribute('source') || window.location.hostname;
        this.shadowRoot.querySelector('a').addEventListener('click', () => {
            window.umami?.track('nexttech-footer-click', { source });
        });
    }
}

customElements.define('nexttech-footer', NexttechFooter);
