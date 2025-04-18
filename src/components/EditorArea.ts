import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';

class EditorArea extends LitElement {
    render() {
        return html`
            <div class="editor-area">
                <h2>${t.preview.heading}</h2>
                <p>${t.preview.editHint}</p>
                <textarea id="spec" name="spec"></textarea>
                <button @click="${this.saveSpec}">${t.export.saveAsPDF}</button>
            </div>
        `;
    }

    saveSpec() {
        // Logic to save the specification
    }
}

customElements.define('editor-area', EditorArea);
