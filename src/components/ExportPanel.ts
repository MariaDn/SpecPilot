import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';

class ExportPanel extends LitElement {
  render() {
    return html`
      <div class="export-panel">
          <button @click="${this.exportPDF}">Export as PDF</button>
          <button @click="${this.exportMarkdown}">Export as Markdown</button>
          <button @click="${this.exportLink}">Export as Link</button>
      </div>
    `;
  }

  exportPDF() {
  }

  exportMarkdown() {
  }

  exportLink() {
  }
}

customElements.define('export-panel', ExportPanel);
