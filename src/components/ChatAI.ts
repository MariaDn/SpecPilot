import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';

class ChatAI extends LitElement {
  render() {
    return html`
      <p>AI is refining your spec...</p>
      <!-- Chat-like interactions for prompt chaining -->
    `;
  }
}

customElements.define('chat-ai', ChatAI);
