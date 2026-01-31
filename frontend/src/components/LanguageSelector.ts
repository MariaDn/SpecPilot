import { LitElement, html, css } from 'lit';
import { setLanguage, Language, currentLanguage } from '../i18n/locales';
import { customElement } from 'lit/decorators';
// import '@vaadin/select';

@customElement('language-selector')
class LanguageSelector extends LitElement {
  static styles = css`
    select {
      padding: 5px;
      margin: 10px;
    }

    .custom-select {
      background-color: #1e1e1e;
      color: #ffffff;
      padding: 8px;
      border: 1px solid #ffffff;
      border-radius: 8px;
      font-size: 14px;
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      cursor: pointer;
    }
  `;

  render() {
    return html`
      <select class="custom-select" @change="${this.changeLanguage}">
        <option value="en" ?selected=${currentLanguage === 'en'}>
          English
        </option>
        <option value="ua" ?selected=${currentLanguage === 'ua'}>
          Українська
        </option>
      </select>
    `;
  }

  changeLanguage(event: Event) {
    const select = event.target as HTMLSelectElement;
    setLanguage(select.value as Language);
    this.requestUpdate();
  }
}
