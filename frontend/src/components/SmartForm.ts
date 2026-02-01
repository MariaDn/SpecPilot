import { LitElement, html, css, nothing } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { t } from '../i18n/locales'; // Правильний імпорт вашого об'єкта локалізації
import { ExportCss } from './ExportCss';
import './ExportPanel';
import './CollapsibleSection';
import '@vaadin/button';
import '@vaadin/text-area';

@customElement('smart-form')
export class SmartForm extends LitElement {
  static override styles = [
    ExportCss.styles,
    css`
      :host { display: block; width: 100%; }
      .flex { 
        display: flex; 
        gap: 30px; 
        flex-wrap: wrap; 
        align-items: flex-start; 
        padding-top: 20px;
      }
      .form-block { display: flex; flex-direction: column; flex: 1 1 500px; min-width: 350px; }
      .left-form { 
        gap: 10px; 
        max-height: 85vh; 
        overflow-y: auto; 
        padding-right: 15px;
        padding-top: 8px; 
      }
      
      h2 { 
        text-align: center; 
        color: #ffffff; 
        background: #007bff; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 24px;ʼ
        min-height: 24px;
      }
      
      .input-group { margin-bottom: 15px; display: flex; flex-direction: column; }
      label { margin-bottom: 5px; font-weight: 600; font-size: 0.85rem; color: #eeeeee; }
      
      input, select, textarea { 
        padding: 12px; border: 1px solid #444; border-radius: 6px; font-size: 0.95rem;
        background: #2c2c2c; color: #fff; transition: border-color 0.2s;
      }

      form.validated input:invalid, 
      form.validated select:invalid, 
      form.validated textarea:invalid {
        border-color: #ff4d4f;
        background-color: #3a2424;
      }

      input:required::after {
        content: " *";
        color: #ff4d4f;
      }

      input:focus { border-color: #007bff; outline: none; }

      textarea { min-height: 80px; resize: vertical; }

      .error-container {
        background-color: #ff4d4f20; border: 1px solid #ff4d4f; color: #ff4d4f;
        padding: 15px; border-radius: 8px; margin: 15px 0; display: flex; gap: 10px;
        animation: fadeIn 0.3s ease;
      }

      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      
      .preview-area { 
        min-height: 550px; 
        width: 100%; 
        font-family: 'Courier New', 
        monospace;
        margin-top: 0; }

      .sticky-actions { 
        position: sticky; bottom: 0; background: #1a1a1a; 
        padding: 20px 0; z-index: 10; border-top: 1px solid #333;
      }
    `
  ];

  @state() geminiResponse: string = '';
  @state() isGenerating = false;
  @state() private errorMessage: string = '';
  @state() private isFormInvalid = false;
  @state() private wasValidated = false;

  render() {
    return html`
      <div class="flex">
        <div class="form-block left-form">
          
          <form id="main-form" class="${this.wasValidated ? 'validated' : ''}" @input="${this._handleInput}">
            <collapsible-section title="${t.questionnaire.sections.s1}">
              <div class="input-group">
                <label>${t.questionnaire.fields.full_name}</label>
                <input type="text" name="project_info.basic_data.full_name" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.short_code}</label>
                <input type="text" name="project_info.basic_data.short_code">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.category}</label>
                <select name="project_info.basic_data.category" required>
                  <option value="Державний">Державний</option>
                  <option value="Комерційний">Комерційний</option>
                </select>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.customer}</label>
                <input type="text" name="project_info.basic_data.customer_org" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.doc_type}</label>
                <input type="text" name="project_info.development_basis.document_type" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.doc_details}</label>
                <input type="text" name="project_info.development_basis.document_details" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.start_date}</label>
                <input type="date" name="project_info.timeline.start_date" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.end_date}</label>
                <input type="date" name="project_info.timeline.end_date" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.lifecycle_type}</label>
                <input type="text" name="project_info.lifecycle.type" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.audience}</label>
                <textarea name="project_info.goals.audience" required></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.problem}</label>
                <textarea name="project_info.goals.problem_statement" required></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.outcome}</label>
                <textarea name="project_info.goals.outcome" required></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s2}">
              <div class="input-group">
                <label>${t.questionnaire.fields.biz_owner}</label>
                <input type="text" name="stakeholders.business_owner" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.tech_owner}</label>
                <input type="text" name="stakeholders.technical_owner" required>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.end_users}</label>
                <textarea name="stakeholders.end_users_description" required></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.user_roles}</label>
                <textarea name="stakeholders.user_roles_description"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s3}">
              <div class="input-group">
                <label>${t.questionnaire.fields.current_state}</label>
                <textarea name="automation_object.current_state_description"></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.biz_processes}</label>
                <textarea name="automation_object.business_processes"></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.work_mode}</label>
                <input type="text" name="automation_object.operating_conditions.work_mode">
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s4}">
              <div class="input-group">
                <label>${t.questionnaire.fields.use_cases}</label>
                <textarea name="functional_requirements.use_cases_raw"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s5}">
              <div class="input-group">
                <label>${t.questionnaire.fields.arch_style}</label>
                <input type="text" name="architecture_requirements.style">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.deployment}</label>
                <input type="text" name="architecture_requirements.infrastructure.deployment_model">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.db_types}</label>
                <input type="text" name="architecture_requirements.data_architecture.db_types">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.integrations}</label>
                <textarea name="architecture_requirements.integrations.patterns"></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.adr}</label>
                <textarea name="architecture_requirements.adr_raw"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s6}">
              <div class="input-group">
                <label>${t.questionnaire.fields.performance}</label>
                <input type="text" name="non_functional_requirements.performance">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.scalability}</label>
                <input type="text" name="non_functional_requirements.scalability">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.security}</label>
                <textarea name="non_functional_requirements.security.raw_requirements"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s7}">
              <div class="input-group">
                <label>${t.questionnaire.fields.tech_stack}</label>
                <textarea name="tech_stack.software_description"></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.external_systems}</label>
                <textarea name="tech_stack.integrations_list"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s8}">
              <div class="input-group">
                <label>${t.questionnaire.fields.acceptance}</label>
                <textarea name="acceptance.procedure_and_criteria"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s9}">
              <div class="input-group">
                <label>${t.questionnaire.fields.doc_list}</label>
                <textarea name="documentation.required_documents"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s10}">
              <div class="input-group">
                <label>${t.questionnaire.fields.kmu_criticality}</label>
                <select name="compliance.kmu_205_compliance.criticality">
                  <option value="КІІ">КІІ</option>
                  <option value="Звичайна">Звичайна</option>
                </select>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.localization}</label>
                <input type="text" name="compliance.data_localization">
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.iso_standards}</label>
                <textarea name="compliance.international_standards"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s11}">
              <div class="input-group">
                <label>${t.questionnaire.fields.constraints}</label>
                <textarea name="constraints.technical_and_budgetary"></textarea>
              </div>
              <div class="input-group">
                <label>${t.questionnaire.fields.assumptions}</label>
                <textarea name="constraints.project_assumptions"></textarea>
              </div>
            </collapsible-section>

            <collapsible-section title="${t.questionnaire.sections.s12}">
              <div class="input-group">
                <label>${t.questionnaire.fields.pm_contacts}</label>
                <input type="text" name="additional_info.pm_contacts">
              </div>
            </collapsible-section>
          </form>

          <div class="sticky-actions">
            ${this.errorMessage 
              ? html`<div class="error-container"><span>⚠️</span><div>${this.errorMessage}</div></div>` 
              : nothing}
            <vaadin-button 
              theme="primary" 
              @click="${this.generateSpec}" 
              ?disabled="${this.isGenerating || this.isFormInvalid}" 
              style="width: 100%;">
              ${this.isGenerating ? t.questionnaire.generating : t.questionnaire.generate_btn}
            </vaadin-button>
          </div>
        </div>

        <div class="form-block">
          <vaadin-text-area class="preview-area" .value="${this.geminiResponse}" readonly></vaadin-text-area>
          <export-panel .content="${this.geminiResponse}"></export-panel>
        </div>
      </div>
    `;
  }

  async generateSpec() {
    const form = this.shadowRoot?.querySelector('#main-form') as HTMLFormElement;
    this.wasValidated = true;

    if (!form.checkValidity()) {
      this.errorMessage = t.form.validationError;
      this.isFormInvalid = true;
      
      this._expandInvalidSections(form);
      
      setTimeout(() => {
        form.reportValidity();
      }, 150);
      
      return;
    }

    this.isGenerating = true;
    this.errorMessage = '';

    const formData = new FormData(form);
    const questionnaire: any = {};

    formData.forEach((value, key) => {
      const keys = key.split('.');
      keys.reduce((acc, part, index) => {
        if (index === keys.length - 1) acc[part] = value;
        else acc[part] = acc[part] || {};
        return acc[part];
      }, questionnaire);
    });

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: "generate_tz", questionnaire: questionnaire }),
      });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();
      this.geminiResponse = data.generated_text;
    } catch (error: any) {
      this.errorMessage = error.message;
    } finally {
      this.isGenerating = false;
    }
  }

  private _handleInput() {
    const form = this.shadowRoot?.querySelector('#main-form') as HTMLFormElement;
    if (form) {
      this.isFormInvalid = !form.checkValidity();
      if (!this.isFormInvalid) {
        this.errorMessage = '';
      }
    }
  }

  private _expandInvalidSections(form: HTMLFormElement) {
    const invalidFields = form.querySelectorAll(':invalid');
    invalidFields.forEach(field => {
      const section = field.closest('collapsible-section') as any;
      if (section) {
        section.isOpen = true;
      }
    });
  }
}