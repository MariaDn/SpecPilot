import { LitElement, html, css, nothing } from 'lit';
import { query, state } from 'lit/decorators';
import { t, localeContext, Translations } from '../i18n/locales';
import { consume } from '@lit/context';
import '@vaadin/button';
import '@vaadin/text-field';
import '@vaadin/checkbox';
import { TextArea } from '@vaadin/text-area';
import { callPublicGemini } from '../gemini';
import { ExportCss } from './ExportCss';
import './ExportPanel';

class SmartForm extends LitElement {
  static override styles = [
    ExportCss.styles,
    css`
    :host {
      display: flex;
      flex-direction: column;
    }

    .form-block {
      display: flex;
      flex-direction: column;
      flex: 1 1 auto;
      min-width: 200px;
    }

    .left-form {
      gap: 18px;
    }

    .form-block h2 {
      text-align: center;
      color: #ffffff;
    }

    label {
      display: flex;
      flex-direction: column;
      margin-bottom: 12px;
      color: #e0e0e0;
    }

    .label-text {
      margin-bottom: 6px;
      font-weight: 500;
    }

    pre {
      white-space: pre-wrap;
      overflow-y: auto;
      max-height: 300px;
    }

    .flex {
      display: flex;
      gap: 40px;
      flex-wrap: wrap;
    }

    .form-section {
      border-top: 1px solid #444;
      padding-top: 12px;
      margin-top: 12px;
    }
    
    .form-section-title {
      font-weight: 600;
      color: #adb5bd;
      margin-bottom: 12px;
    }
    
    .option-group {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 12px;
    }
  `];

  @state() geminiResponse: string = '';
  @state() isGenerating = false;

  @query('#name') nameField!: TextArea;
  @query('#description') descriptionField!: TextArea;
  @query('#timeline') timelineField!: TextArea;
  @query('#budget') budgetField!: TextArea;
  @query('#audience') audienceField!: TextArea;
  @query('#objectives') objectivesField!: TextArea;

  render() {
    const buttonTitle = this.isGenerating
      ? t.form.generating
      : t.form.generateButton;
    return html`
      <div class="flex">
        <div class="form-block left-form">
          <h2>${t.form.title}</h2>
          
          <!-- Basic Info Section -->
          <div class="form-section">
            <div class="form-section-title">${t.form.basicInfo}</div>
            <label>
              <span class="label-text">${t.form.projectName}</span>
              <vaadin-text-field id="name"></vaadin-text-field>
            </label>
            <label>
              <span class="label-text">${t.form.description}</span>
              <vaadin-text-area id="description"></vaadin-text-area>
            </label>
          </div>
          
          <!-- Project Details Section -->
          <div class="form-section">
            <div class="form-section-title">${t.form.projectDetails}</div>
            <label>
              <span class="label-text">${t.form.timeline}</span>
              <vaadin-text-field id="timeline"></vaadin-text-field>
            </label>
            <label>
              <span class="label-text">${t.form.budget}</span>
              <vaadin-text-field id="budget"></vaadin-text-field>
            </label>
          </div>
          
          <!-- Target & Goals Section -->
          <div class="form-section">
            <div class="form-section-title">${t.form.targetGoals}</div>
            <label>
              <span class="label-text">${t.form.audience}</span>
              <vaadin-text-area id="audience"></vaadin-text-area>
            </label>
            <label>
              <span class="label-text">${t.form.objectives}</span>
              <vaadin-text-area id="objectives"></vaadin-text-area>
            </label>
          </div>
          <vaadin-button theme="primary" @click="${this.generateSpec}">
            ${buttonTitle}
          </vaadin-button>
        </div>
        <div class="form-block">
          <h2>${t.preview.heading}</h2>
          <p>${t.preview.editHint}</p>
          <vaadin-text-area .value="${this.geminiResponse}" style="min-height: 400px;"></vaadin-text-area>
          <p>${t.preview.askAIHint}</p>
          <vaadin-text-area></vaadin-text-area>
          <export-panel></export-panel>
        </div>
      </div>
    `;
  }

  async generateSpec() {
    const name = this.nameField.value || 'SpecPilot';
    const description = this.descriptionField.value || 
      'Quickly generate high-quality specifications for your projects.';
    const timeline = this.timelineField?.value || '';
    const budget = this.budgetField?.value || '';
    const audience = this.audienceField?.value || '';
    const objectives = this.objectivesField?.value || '';
    
    // Get checked technologies
    const techCheckboxes = this.shadowRoot?.querySelectorAll('.option-group:first-of-type vaadin-checkbox');
    const selectedTech = Array.from(techCheckboxes || [])
      .filter((checkbox: any) => checkbox.checked)
      .map((checkbox: any) => checkbox.textContent)
      .join(', ');
      
    // Get checked integrations
    const integrationCheckboxes = this.shadowRoot?.querySelectorAll('.option-group:last-of-type vaadin-checkbox');
    const selectedIntegrations = Array.from(integrationCheckboxes || [])
      .filter((checkbox: any) => checkbox.checked)
      .map((checkbox: any) => checkbox.textContent)
      .join(', ');
    
    console.log(name, description);

    const prompt = `Generate a technical specification for the project with the following details:
    
    Project Name: ${name}
    Project Description: ${description}
    ${timeline ? `Timeline: ${timeline}` : ''}
    ${budget ? `Budget: ${budget}` : ''}
    ${audience ? `Target Audience: ${audience}` : ''}
    ${objectives ? `Objectives: ${objectives}` : ''}
    ${selectedTech ? `Technologies: ${selectedTech}` : ''}
    ${selectedIntegrations ? `Integrations: ${selectedIntegrations}` : ''}
    
    Please include the following sections:
    1. Project Overview
    2. Goals and Objectives
    3. Target Audience
    4. Technical Requirements
    5. Features and Functionality
    6. Timeline and Milestones
    7. Budget Considerations
    
    Make the specification detailed, well-structured, and professional.
    `;
    
    try {
      this.isGenerating = true;
      this.geminiResponse = await callPublicGemini(prompt);
    } finally {
      this.isGenerating = false;
    }

    this.dispatchEvent(
      new CustomEvent('spec-generated', {
        detail: { 
          response: this.geminiResponse, 
          name, 
          description,
          timeline,
          budget,
          audience,
          objectives,
          selectedTech,
          selectedIntegrations
        },
      })
    );
  }
}

customElements.define('smart-form', SmartForm);