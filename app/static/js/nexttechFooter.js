class NexttechFooter extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        // `source` tags where the click came from. It travels to nexttech.com.ar as a
        // UTM param on the link, so nexttech's own Umami records it under Referrers /
        // UTM — centralized, and independent of whether the embedding site has Umami.
        // (A custom umami.track() can't work here: it would fire against the embedding
        // site's tracker, and rel="noreferrer" strips the referrer on navigation.)
        const source = this.getAttribute('source') || window.location.hostname;
        const href = 'https://nexttech.com.ar/?utm_source='
            + encodeURIComponent(source) + '&utm_medium=footer';

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
                <a href="${href}" target="_blank" rel="noopener">
                    <img src="https://nexttech.com.ar/static/assets/favicon.svg" alt="Next Tech Logo">
                    <span>Creado por Next Tech</span>
                </a>
            </div>
        `;
    }
}

customElements.define('nexttech-footer', NexttechFooter);
