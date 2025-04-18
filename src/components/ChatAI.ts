import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';

class ChatAI extends LitElement {
  render() {
    return html`
      <div class="chat-ai">
          <p>AI is refining your spec...</p>
          <!-- Chat-like interactions for prompt chaining -->
      </div>
    `;
  }
}

customElements.define('chat-ai', ChatAI);
