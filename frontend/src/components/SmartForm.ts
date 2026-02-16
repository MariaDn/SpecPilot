import { LitElement, html, css, nothing } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { t } from '../i18n/locales';
import { ExportCss } from './ExportCss';
import './ExportPanel';
import './CollapsibleSection';
import '@vaadin/button';
import '@vaadin/text-area';
import '@vaadin/tabs';
import '@vaadin/upload';
import '@vaadin/text-field';

@customElement('smart-form')
export class SmartForm extends LitElement {
  static override styles = [
    ExportCss.styles,
    css`
      :host { 
        display: block; 
        width: 100%;
        --lumo-body-text-color: #f0f0f0;
        --lumo-secondary-text-color: #bbbbbb;
        --lumo-primary-text-color: #58a6ff;
        --lumo-contrast-10pct: rgba(255, 255, 255, 0.05); 
      }
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

      vaadin-tabs {
        background: #252525;
        border-radius: 8px;
        margin-bottom: 10px;
        color: white;
      }
      
      vaadin-upload::part(label) {
        color: #ffffff !important;
        font-size: 14px;
        margin-bottom: 8px;
      }

      vaadin-upload-file::part(start-button) {
        display: none !important;
      }

      vaadin-upload::part(upload-button) {
        display: none !important;
      }

      span[slot="drop-label"] {
        color: #888888 !important;
      }

      .upload-card {
        background: #1a1a1a;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 12px;
      }
    `
  ];

  @state() geminiResponse: string = '';
  @state() isGenerating = false;
  @state() private errorMessage: string = '';
  @state() private isFormInvalid = false;
  @state() private wasValidated = false;
  @state() private chatHistory: any[] = [];
  @state() private activeTab = 0;
  @state() private selectedProjectId = '';
  @state() private navQuery = '';
  @state() private existingProjects: string[] = [];
  @state() private progress = 0;
  @state() private currentStatus = '';

  render() {
    return html`
      <vaadin-tabs @selected-changed="${(e: any) => this.activeTab = e.detail.value}">
        <vaadin-tab>📝 ${t.questionnaire.generate_btn}</vaadin-tab>
        <vaadin-tab>🔍 ${t.questionnaire.navigation_btn}</vaadin-tab>
      </vaadin-tabs>

      <div class="flex">
        <div class="form-block left-form">
          ${this.activeTab === 0 
            ? this.renderGeneratorForm() 
            : this.renderNavigationForm()}
        </div>

        <div class="form-block">
          <vaadin-text-area class="preview-area" .value="${this.geminiResponse}" readonly></vaadin-text-area>
          <export-panel .content="${this.geminiResponse}"></export-panel>
        </div>
      </div>
    `;
  }

  renderGeneratorForm() {
    return html`
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
              <option value="Державний">Державний / Public Sector</option>
              <option value="Комерційний">Комерційний / Commercial</option>
            </select>
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.customer}</label>
            <input type="text" name="project_info.basic_data.customer_org" required>
          </div>
          
          <div class="input-group">
            <label>${t.questionnaire.fields.developer}</label>
            <input type="text" name="project_info.basic_data.developer_org">
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.funding}</label>
            <input type="text" name="project_info.basic_data.funding_source">
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
            <label>${t.questionnaire.fields.approver}</label>
            <input type="text" name="project_info.development_basis.approver">
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.related_docs}</label>
            <textarea name="project_info.development_basis.input_docs"></textarea>
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
            <label>${t.questionnaire.fields.milestones}</label>
            <textarea name="project_info.timeline.milestones"></textarea>
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.lifecycle_type}</label>
            <select name="project_info.lifecycle.type" required>
              <option value="Створення з нуля (Greenfield)">Greenfield</option>
              <option value="Модернізація (Brownfield)">Brownfield</option>
              <option value="Розвиток/Масштабування">Scale/Evolution</option>
            </select>
          </div>

          <div style="border-left: 3px solid #eee; padding-left: 10px; margin-top: 10px;">
             <div class="input-group">
               <label>${t.questionnaire.fields.legacy_name}</label>
               <input type="text" name="project_info.legacy_system.name">
             </div>
             <div class="input-group">
               <label>${t.questionnaire.fields.legacy_stack}</label>
               <input type="text" name="project_info.legacy_system.stack">
             </div>
             <div class="input-group">
               <label>${t.questionnaire.fields.legacy_problems}</label>
               <textarea name="project_info.legacy_system.problems"></textarea>
             </div>
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
          
          <div class="input-group">
            <label>${t.form.budget}</label>
            <input type="text" name="project_info.goals.budget">
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
            <label>${t.questionnaire.fields.domain_experts}</label>
            <input type="text" name="stakeholders.domain_experts">
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
            <label>${t.questionnaire.fields.org_structure}</label>
            <textarea name="automation_object.org_structure"></textarea>
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.biz_processes}</label>
            <textarea name="automation_object.business_processes"></textarea>
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.work_mode}</label>
            <input type="text" name="automation_object.operating_conditions.work_mode">
          </div>
          
          <div class="input-group">
            <label>${t.questionnaire.fields.climate}</label>
            <input type="text" name="automation_object.operating_conditions.climate">
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.locations}</label>
            <input type="text" name="automation_object.operating_conditions.geo_location">
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.workstations}</label>
            <input type="text" name="automation_object.operating_conditions.workplaces_count">
          </div>
        </collapsible-section>

        <collapsible-section title="${t.questionnaire.sections.s4}">
          <div class="input-group">
            <label>${t.questionnaire.fields.use_cases}</label>
            <textarea name="functional_requirements.use_cases_raw" style="min-height: 150px;"></textarea>
          </div>
        </collapsible-section>

        <collapsible-section title="${t.questionnaire.sections.s5}">
          <div class="input-group">
            <label>${t.questionnaire.fields.arch_style}</label>
            <select name="architecture_requirements.style">
               <option value="Microservices">Microservices</option>
               <option value="Monolithic">Monolithic</option>
               <option value="Service-Based">Service-Based</option>
               <option value="TBD">TBD (AI Suggestion)</option>
            </select>
          </div>
          
          <div class="input-group">
            <label>${t.questionnaire.fields.arch_reason}</label>
            <textarea name="architecture_requirements.justification"></textarea>
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.deployment}</label>
            <input type="text" name="architecture_requirements.infrastructure.deployment_model">
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.cloud_provider}</label>
            <input type="text" name="architecture_requirements.infrastructure.cloud_provider">
          </div>
          
          <div class="input-group">
             <label>${t.questionnaire.fields.containerization}</label>
             <input type="text" name="architecture_requirements.infrastructure.containerization">
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.db_types}</label>
            <input type="text" name="architecture_requirements.data_architecture.db_types">
          </div>
          
          <div class="input-group">
            <label>${t.questionnaire.fields.db_pattern}</label>
            <input type="text" name="architecture_requirements.data_architecture.db_pattern">
          </div>

          <div class="input-group">
             <label>${t.questionnaire.fields.backup} (Volume & Backup)</label>
             <textarea name="architecture_requirements.data_architecture.volume_and_backup"></textarea>
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.integrations}</label>
            <textarea name="architecture_requirements.integrations.patterns"></textarea>
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.integrations} (Details)</label>
            <input type="text" name="architecture_requirements.integrations.details">
          </div>

          <div class="input-group" style="border-top: 1px dashed #ccc; padding-top: 10px;">
            <label><strong>${t.questionnaire.fields.qa_priorities}</strong></label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <input type="text" name="architecture_requirements.qa_priorities.critical" placeholder="Priority 1 (Critical)">
                <input type="text" name="architecture_requirements.qa_priorities.high" placeholder="Priority 2 (High)">
            </div>
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
            <label>${t.questionnaire.fields.availability}</label>
            <input type="text" name="non_functional_requirements.availability">
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.security}</label>
            <textarea name="non_functional_requirements.security.raw_requirements"></textarea>
          </div>
        </collapsible-section>

        <collapsible-section title="${t.questionnaire.sections.s7}">
          <div class="input-group">
            <label>Frontend Stack</label>
            <input type="text" name="tech_stack.frontend" placeholder="React, Vue...">
          </div>
          <div class="input-group">
            <label>Backend Stack</label>
            <input type="text" name="tech_stack.backend" placeholder="Python, Java...">
          </div>
          <div class="input-group">
            <label>Infrastructure Stack</label>
            <input type="text" name="tech_stack.infrastructure" placeholder="K8s, Terraform...">
          </div>

          <div class="input-group">
            <label>${t.questionnaire.fields.tech_stack} (General)</label>
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
          
          <div class="input-group">
            <label>${t.questionnaire.fields.trial_duration}</label>
            <input type="text" name="acceptance.trial_duration">
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.responsible_person}</label>
            <input type="text" name="acceptance.responsible_person">
          </div>

          <div class="input-group">
             <label>${t.questionnaire.fields.warranty}</label>
             <textarea name="acceptance.warranty_and_support"></textarea>
          </div>
        </collapsible-section>

        <collapsible-section title="${t.questionnaire.sections.s9}">
          <div class="input-group">
            <label>${t.questionnaire.fields.doc_list}</label>
            <textarea name="documentation.required_documents"></textarea>
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.doc_lang}</label>
            <select name="documentation.language">
                <option value="UA">UA</option>
                <option value="EN">EN</option>
                <option value="UA+EN">UA+EN</option>
            </select>
          </div>
        </collapsible-section>

        <collapsible-section title="${t.questionnaire.sections.s10}">
          <div class="input-group">
            <label>${t.questionnaire.fields.kmu_criticality}</label>
            <select name="compliance.kmu_205_compliance.criticality">
              <option value="КІІ">КІІ / CII</option>
              <option value="Звичайна">Звичайна / Standard</option>
            </select>
          </div>
          <div class="input-group">
            <label>${t.questionnaire.fields.localization}</label>
            <input type="text" name="compliance.data_localization">
          </div>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div class="input-group">
                <label>RPO</label>
                <input type="text" name="compliance.rpo" placeholder="< 15 min">
            </div>
            <div class="input-group">
                <label>RTO</label>
                <input type="text" name="compliance.rto" placeholder="< 2 hours">
            </div>
          </div>
          
          <div class="input-group">
            <label>${t.questionnaire.fields.geo_replication}</label>
            <select name="compliance.geo_replication">
                <option value="Ні">Ні / No</option>
                <option value="Так">Так / Yes</option>
            </select>
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
          
          <div class="input-group">
            <label>${t.questionnaire.fields.special_requirements}</label>
            <input type="text" name="additional_info.special_requirements">
          </div>
        </collapsible-section>
      </form>

      <div class="sticky-actions">
        ${this.isGenerating 
          ? html`
              <div style="margin-bottom: 10px; color: var(--lumo-primary-text-color); font-size: 0.9rem;">
                ${this.currentStatus} (${this.progress}%)
              </div>
              <div style="width: 100%; height: 4px; background: #333; margin-bottom: 15px; border-radius: 2px; overflow: hidden;">
                <div style="width: ${this.progress}%; height: 100%; background: var(--lumo-primary-text-color); transition: width 0.3s;"></div>
              </div>
            ` 
          : nothing}

        ${this.errorMessage 
          ? html`<div class="error-container"><span>⚠️</span><div>${this.errorMessage}</div></div>` 
          : nothing}

        <vaadin-button 
          theme="primary" 
          @click="${this.generateFullSpec}" 
          ?disabled="${this.isGenerating || this.isFormInvalid}" 
          style="width: 100%;">
          ${this.isGenerating ? t.questionnaire.generating : t.questionnaire.generate_btn}
        </vaadin-button>
      </div>
    `;
  }

  renderNavigationForm() {
    return html`
      <collapsible-section title=${t.navigation.uploadTitle} isOpen>
        <div class="input-group">
          <label>${t.navigation.projectIdLabel}</label>
          <input 
            type="text" 
            .value="${this.selectedProjectId}" 
            @input="${(e: any) => { 
              this.selectedProjectId = e.target.value; 
              this.updateValidation(); 
            }}"
            placeholder="${t.navigation.projectIdPlaceholder}"
          >
        </div>

        <vaadin-upload
          id="project-upload"
          no-auto
          max-files="1"
          accept=".docx"
          .target="${`http://localhost:8000/api/upload?project_id=${encodeURIComponent(this.selectedProjectId)}`}"
          @files-changed="${(e: any) => {
            this.hasFile = e.target.files.length > 0;
            this.updateValidation();
          }}"
        >
          <span slot="drop-label">${t.navigation.dropLabel}</span>
        </vaadin-upload>

        <vaadin-button
          theme="primary"
          ?disabled="${!this.canUpload}"
          @click="${this.handleManualUpload}"
          style="width: 100%; margin-top: 20px; cursor: ${this.canUpload ? 'pointer' : 'not-allowed'};"
        >
          ${t.navigation.uploadBtn}
        </vaadin-button>
      </collapsible-section>

      <collapsible-section title=${t.navigation.assistantTitle} isOpen>
        <div class="input-group">
          <label>${t.navigation.selectProjectLabel}</label>
          <select 
            .value="${this.selectedProjectId}" 
            @change="${(e: any) => this.selectedProjectId = e.target.value}"
          >
            <option value="" disabled selected>${t.navigation.selectProjectPlaceholder}</option>
            ${this.existingProjects.map(p => html`<option value="${p}">${p}</option>`)}
          </select>
        </div>

        <div class="input-group">
          <label>${t.navigation.assistantQueryLabel}</label>
          <vaadin-text-area 
            placeholder=${t.navigation.assistantPlaceholder} 
            @value-changed="${(e: any) => this.navQuery = e.detail.value}">
          </vaadin-text-area>
        </div>
        <vaadin-button theme="primary" @click="${this.runNavigation}" ?disabled="${this.isGenerating}" style="width: 100%;">
          ${this.isGenerating ? t.navigation.assistantSearching : t.navigation.assistantBtn}
        </vaadin-button>
      </collapsible-section>
    `;
  }

  private updateValidation() {
    this.canUpload = this.selectedProjectId.trim().length > 0 && this.hasFile;
  }

  private handleManualUpload() {
    const upload = (this as unknown as HTMLElement).shadowRoot?.querySelector('#project-upload') as any;
    if (upload) {
      upload.uploadFiles();
    }
  }

  async generateFullSpec() {
    const form = this.shadowRoot?.querySelector('#main-form') as HTMLFormElement;
    if (!form) {
        console.error("Form not found");
        return;
    }

    this.wasValidated = true;

    if (!form.checkValidity()) {
      this.errorMessage = t.form.validationError;
      this._expandInvalidSections(form);
      return;
    }

    this.isGenerating = true;
    this.errorMessage = '';
    this.geminiResponse = '';
    this.progress = 0;

    const questionnaire = this._serializeForm(form);
    
    const sectionGroups = [
      { ids: ["1"], label: "1. Загальні відомості" },
      { ids: ["2"], label: "2. Робочий процес та стек" },
      { ids: ["3"], label: "3. Вимоги до системи (FR/NFR)" },
      { ids: ["4"], label: "4. Склад та зміст робіт" },
      { ids: ["5"], label: "5. Контроль та приймання" },
      { ids: ["6"], label: "6. Введення в експлуатацію" },
      { ids: ["7"], label: "7. Документування" },
      { ids: ["8"], label: "8. Джерела розробки" },
      { ids: ["9"], label: "9. Порядок змін" },
      { ids: ["10"], label: "10. Додатки" }
    ];

    try {
      let accumulatedSections: any[] = [];

      for (let i = 0; i < sectionGroups.length; i++) {
        const group = sectionGroups[i];
        this.currentStatus = `Генерація: ${group.label} (${i + 1}/${sectionGroups.length})`;
        this.requestUpdate();
        
        const response = await fetch('http://localhost:8000/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            mode: "generate_tz", 
            messages: [],
            context: { 
              questionnaire,
              target_sections: group.ids
            } 
          }),
        });

        if (!response.ok) throw new Error(`Server error на кроці ${i + 1}`);
        
        const data = await response.json();

        if (data.status === 'error') {
          throw new Error(`AI Error: ${data.message}`);
        }
        if (!data.output || !data.output.document) {
          if (data.status === 'partial_error' && data.raw_output) {
             console.warn("Parsing failed, showing raw output");
             this.geminiResponse += `\nПомилка форматування. Сирий текст:\n${data.raw_output}`;
             return; 
          }
          throw new Error("Некоректна відповідь від AI (відсутнє поле document)");
        }

        const newSections = data.output.document.sections;
        const validSections = newSections.filter((s: any) => 
          !s.content.includes("Розділ не був згенерований моделлю")
        );
        if (validSections.length > 0) {
          accumulatedSections.push(...validSections);
        } else {
          accumulatedSections.push(...newSections);
        }

        this.geminiResponse = accumulatedSections
          .map((s: any) => `## ${s.name}\n${s.content}`)
          .join('\n\n');
        
        this.progress = Math.round(((i + 1) / sectionGroups.length) * 100);
      }
    } catch (error: any) {
      this.errorMessage = error.message;
    } finally {
      this.isGenerating = false;
      this.currentStatus = '';
    }
  }

  async runNavigation() {
    if (!this.navQuery) return;
    this.isGenerating = true;

    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mode: "qa_navigation", 
          messages: [
            { role: "user", content: [{ type: "text", text: this.navQuery }] }
          ],
          context: { 
            task_metadata: { project_id: this.selectedProjectId },
            questionnaire: {}
          } 
        }),
      });
      const data = await response.json();
      if (data.output && data.output.answer) {
          this.geminiResponse = data.output.answer.text;
      } else if (data.output && data.output.document) {
          this.geminiResponse = JSON.stringify(data.output.document);
      } else {
          this.geminiResponse = "Отримано некоректну відповідь від сервера.";
      }

    } catch (e) {
      this.errorMessage = "Помилка пошуку в pgvector";
    } finally {
      this.isGenerating = false;
    }
  }

  async fetchProjects() {
    try {
      const res = await fetch('http://localhost:8000/api/projects');
      const data = await res.json();
      this.existingProjects = data.projects;
    } catch (e) {
      console.error("Error while loading list of projects");
    }
  }

  private _serializeForm(form: HTMLFormElement) {
    const formData = new FormData(form);
    const obj: any = {};
    formData.forEach((value, key) => {
      const keys = key.split('.');
      keys.reduce((acc, part, i) => acc[part] = i === keys.length - 1 ? value : (acc[part] || {}), obj);
    });
    return obj;
  }

  updated(changedProperties: Map<string, any>) {
    if (changedProperties.has('activeTab') && this.activeTab === 1) {
      this.fetchProjects();
    }
  }

  private _handleInput() {
    const form = (this as unknown as HTMLElement).shadowRoot?.querySelector('#main-form') as HTMLFormElement;
    this.isFormInvalid = form ? !form.checkValidity() : false;
  }

  private _expandInvalidSections(form: HTMLFormElement) {
    form.querySelectorAll(':invalid').forEach(f => (f.closest('collapsible-section') as any).isOpen = true);
  }
}