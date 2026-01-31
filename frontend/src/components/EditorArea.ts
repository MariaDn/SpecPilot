import { LitElement, html, css } from 'lit';
import { property } from 'lit/decorators';
import { t } from '../i18n/locales';
import { ExportCss } from './ExportCss';
import '@vaadin/text-area';
import '@vaadin/button';

class EditorArea extends LitElement {
  static styles = [
    ExportCss.styles,
    css`
    :host {
      display: flex;
      flex-direction: column;
    }
  `];

  @property() generatedSpec = '';

  render() {
    return html`
      <h2>${t.preview.heading}</h2>
      <p>${t.preview.editHint}</p>
      <vaadin-text-area .value="${this.generatedSpec}"></vaadin-text-area>
      <vaadin-button @click="${this.saveSpec}">
        ${t.export.saveAsPDF}
      </vaadin-button>
    `;
  }

  saveSpec() {
    // Logic to save the specification
  }
}

customElements.define('editor-area', EditorArea);