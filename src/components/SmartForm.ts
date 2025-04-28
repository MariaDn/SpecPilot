import { LitElement, html, css, nothing } from 'lit';
import { query, state } from 'lit/decorators';
import { t, localeContext, Translations } from '../i18n/locales';
import { consume } from '@lit/context';
import '@vaadin/button';
import '@vaadin/text-field';
import { TextArea } from '@vaadin/text-area';
import { callPublicGemini } from '../gemini';
import { ExportPanelCss } from './ExportPanelCss';

class SmartForm extends LitElement {
  static override styles = [
    ExportPanelCss.styles,
    css`
    :host {
      display: flex;
      flex-direction: column;
    }

    label {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
    }

    pre {
      white-space: pre-wrap;
      overflow-y: auto;
      max-height: 300px;
    }
  `];

  @state() geminiResponse: string = '';
  @state() isGenerating = false;

  @query('#name') nameField!: TextArea;
  @query('#description') descriptionField!: TextArea;

  render() {
    const buttonTitle = this.isGenerating
      ? t.form.generating
      : t.form.generateButton;
    return html`
      <h2>${t.form.title}</h2>
      <label for="projectName">
        ${t.form.projectName}

        <vaadin-text-field id="name" required></vaadin-text-field>
      </label>
      <label for="description"
        >${t.form.description}
        <vaadin-text-field id="description" required></vaadin-text-field>
      </label>
      <vaadin-button theme="primary" @click="${this.generateSpec}">
        ${buttonTitle}
      </vaadin-button>
      <h2>${t.preview.heading}</h2>
      <p>${t.preview.editHint}</p>
      <vaadin-text-area .value="${this.geminiResponse}"></vaadin-text-area>
    `;
  }

  async generateSpec() {
    const name = this.nameField.value || 'SpecPilot';
    const description =
      this.descriptionField.value ||
      'Quickly generate high-quality specifications for your projects.';
    console.log(name, description);

    const prompt = `Generate a specification for the project given name and short description.
    
    Name: ${name}.

    Description: ${description}.
    `;
    try {
      this.isGenerating = true;
      this.geminiResponse = await callPublicGemini(prompt);
    } finally {
      this.isGenerating = false;
    }

    this.dispatchEvent(
      new CustomEvent('spec-generated', {
        detail: { response: this.geminiResponse, name, description },
      })
    );
  }
}

customElements.define('smart-form', SmartForm);
