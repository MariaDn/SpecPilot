import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';

class SmartForm extends LitElement {
  render() {
    return html`
      <form @submit="${this.generateSpec}">
          <h2>${t.form.title}</h2>
          <label for="projectName">${t.form.projectName}</label>
          <input type="text" id="projectName" name="projectName" required>
          <label for="description">${t.form.description}</label>
          <textarea id="description" name="description" required></textarea>
          <button type="submit">${t.form.generateButton}</button>
      </form>
    `;
  }

  generateSpec(event: Event) {
      event.preventDefault();
  }
}

customElements.define('smart-form', SmartForm);
