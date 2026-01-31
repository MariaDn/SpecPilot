import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { t } from '../i18n/locales';

@customElement('ai-status-indicator')
export class AIStatusIndicator extends LitElement {
  @state() private status: 'loading' | 'online' | 'offline' = 'loading';
  private get statusMessage() {
    switch (this.status) {
      case 'online': return t.ai_status.online;
      case 'offline': return t.ai_status.offline;
      default: return t.ai_status.loading;
    }
  }

  static styles = css`
    :host {
      display: inline-flex;
      align-items: center;
      font-family: sans-serif;
      font-size: 14px;
      gap: 8px;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background-color: #ccc;
    }
    .online { background-color: #4caf50; box-shadow: 0 0 8px #4caf50; }
    .offline { background-color: #f44336; box-shadow: 0 0 8px #f44336; }
    .loading { background-color: #ffeb3b; animation: pulse 1.5s infinite; }

    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.4; }
      100% { opacity: 1; }
    }
  `;

  async connectedCallback() {
    super.connectedCallback();
    await this.checkAIHealth();
  }

  async checkAIHealth() {
    this.status = 'loading';
    try {
      const response = await fetch('http://localhost:8000/api/health/ai');
      if (!response.ok) throw new Error();
      const data = await response.json();

      if (data.status === 'healthy') {
        this.status = 'online';
      } else {
        throw new Error();
      }
    } catch (error) {
      this.status = 'offline';
    }
  }

  render() {
    return html`
      <div class="dot ${this.status}"></div>
      <span>${this.statusMessage}</span>
    `;
  }
}