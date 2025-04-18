import { LitElement, html, css } from 'lit';
import { setLanguage, Language } from '../i18n/locales';

class LanguageSelector extends LitElement {
  static styles = css`
    select {
        padding: 5px;
        margin: 10px;
    }
  `;

  render() {
    return html`
        <select @change="${this.changeLanguage}">
            <option value="en">English</option>
            <option value="ua">Українська</option>
        </select>
    `;
  }

  changeLanguage(event: Event) {
    const select = event.target as HTMLSelectElement;
    setLanguage(select.value as Language);
    this.requestUpdate();
  }
}

customElements.define('language-selector', LanguageSelector);
