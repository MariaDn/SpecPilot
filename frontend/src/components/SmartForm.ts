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

    .error-container {
      background-color: #ff4d4f20;
      border: 1px solid #ff4d4f;
      color: #ff4d4f;
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 16px;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `];

  @state() geminiResponse: string = '';
  @state() isGenerating = false;
  @state() private errorMessage: string = '';

  @query('#name') nameField!: any;
  @query('#description') descriptionField!: any;
  @query('#timeline') timelineField!: any;
  @query('#budget') budgetField!: any;
  @query('#audience') audienceField!: any;
  @query('#objectives') objectivesField!: any;

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
          <div class="form-block left-form">
            ${this.errorMessage 
              ? html`
                  <div class="error-container">
                    <span>⚠️</span>
                    <div>${this.errorMessage}</div>
                  </div>` 
              : nothing}
          <vaadin-button theme="primary" @click="${this.generateSpec}" ?disabled="${this.isGenerating}">
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
    
    const fullPrompt = `Generate a technical specification for the project:
    Name: ${name}
    Description: ${description}
    Timeline: ${timeline}
    Budget: ${budget}
    Audience: ${audience}
    Objectives: ${objectives}
    `;
    
    this.errorMessage = '';
    this.isGenerating = true;

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: fullPrompt }),
      });

      if (!response.ok) {
        if (response.status === 422) {
          throw new Error('Помилка валідації: Перевірте введені дані.');
        } else if (response.status === 500) {
          throw new Error('Серверна помилка: Можливо, Qdrant або модель MamayLM недоступні.');
        } else {
          throw new Error(`Помилка сервера: Статус ${response.status}`);
        }
      }

      const data = await response.json();
      
      this.geminiResponse = data.generated_text;

    } catch (error: any) {
      console.error("Помилка при генерації:", error);
      if (error.message === 'Failed to fetch') {
        this.errorMessage = 'Неможливо з’єднатися з бекендом. Перевірте, чи запущено Docker-контейнери.';
    } else {
        this.errorMessage = error.message || 'Сталася невідома помилка.';
    }
    } finally {
      this.isGenerating = false;
    }

    this.dispatchEvent(
      new CustomEvent('spec-generated', {
        detail: { 
          response: this.geminiResponse, 
          name, 
          description
        },
      })
    );
  }
}

customElements.define('smart-form', SmartForm);