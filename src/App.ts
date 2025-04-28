import { LitElement, html, css } from 'lit';
import { state } from 'lit/decorators';
import './components/HeroSection';
import './components/SmartForm';
import './components/ChatAI';
import './components/EditorArea';
import './components/ExportPanel';
import './components/LanguageSelector';

class App extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin: auto;
      max-width: 640px;
      padding: 20px;
      background-color: #00000010;
      margin-top: 10px;
      box-sizing: border-box;
      border-radius: 10px;
      position: relative;
    }

    language-selector {
      position: absolute;
      bottom: 10px;
      right: 10px;
    }
  `;

  render() {
    return html`
      <language-selector></language-selector>
      <hero-section></hero-section>
      <smart-form></smart-form>
      <chat-ai></chat-ai>
      <export-panel></export-panel>
    `;
  }
}

customElements.define('app-root', App);
