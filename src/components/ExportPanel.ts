import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';
import '@vaadin/button';
import { styles } from './ExportPanelCss';

class ExportPanel extends LitElement {
  static override styles = styles;

  render() {
    return html`
      <div class="export-panel">
        <vaadin-button theme="primary" @click="${this.exportPDF}"
          >Export as PDF</vaadin-button
        >
        <vaadin-button theme="primary" @click="${this.exportMarkdown}"
          >Export as Markdown</vaadin-button
        >
        <vaadin-button theme="primary" @click="${this.exportLink}"
          >Export as Link</vaadin-button
        >
      </div>
    `;
  }

  exportPDF() {}

  exportMarkdown() {}

  exportLink() {}
}

customElements.define('export-panel', ExportPanel);
