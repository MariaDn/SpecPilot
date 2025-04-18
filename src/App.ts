import { LitElement, html, css } from 'lit';
import './components/HeroSection';
import './components/SmartForm';
import './components/ChatAI';
import './components/EditorArea';
import './components/ExportPanel';
import './components/LanguageSelector';

class App extends LitElement {
  render() {
    return html`
      <language-selector></language-selector>
      <hero-section></hero-section>
      <smart-form></smart-form>
      <chat-ai></chat-ai>
      <editor-area></editor-area>
      <export-panel></export-panel>
    `;
  }
}

customElements.define('app-root', App);

