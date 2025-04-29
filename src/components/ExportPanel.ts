import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';
import '@vaadin/button';
import { ExportCss } from './ExportCss';

class ExportPanel extends LitElement {
  static override styles = [
    ExportCss.styles,
    css`
    :host {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      flex-wrap: wrap;
    }
  `];

  render() {
    return html`
      <vaadin-button theme="tertiary" @click="${this.exportPDF}"
        >${t.export.saveAsPDF}</vaadin-button
      >
      <vaadin-button theme="tertiary" @click="${this.exportMarkdown}"
        >${t.export.saveAsMarkdown}</vaadin-button
      >
      <vaadin-button theme="tertiary" @click="${this.exportLink}"
        >${t.export.copyLink}</vaadin-button
      >
    `;
  }

  exportPDF() {}

  exportMarkdown() {}

  exportLink() {}
}

customElements.define('export-panel', ExportPanel);
