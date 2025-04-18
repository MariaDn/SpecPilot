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
  `;

  render() {
    return html`
      <select @change="${this.changeLanguage}">
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
