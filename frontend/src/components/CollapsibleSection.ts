import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

@customElement('collapsible-section')
export class CollapsibleSection extends LitElement {
  @property({ type: String }) title = '';
  @state() private isOpen = false;

  static styles = css`
    .section { 
      border: 1px solid #444; 
      border-radius: 8px; 
      margin-bottom: 12px; 
      overflow: hidden; 
      background: #1e1e1e;
    }
    
    .header { 
      /* Колір темно-сірий, як у ваших textarea */
      background: #2c2c2c; 
      color: #ffffff; 
      padding: 15px; 
      cursor: pointer; 
      display: flex; 
      justify-content: space-between; 
      align-items: center;
      font-weight: 600; 
      font-size: 1rem;
      transition: background 0.2s;
    }
    
    .header:hover { 
      background: #363636; 
    }
    
    .content { 
      padding: 20px; 
      display: none; 
      background: #1e1e1e; 
      border-top: 1px solid #444;
      color: #eeeeee;
    }
    
    .content.open { 
      display: block; 
    }
    
    .arrow { 
      font-size: 0.8rem;
      transition: transform 0.3s; 
    }
    
    .arrow.open { 
      transform: rotate(180deg); 
    }
  `;

  render() {
    return html`
      <div class="section">
        <div class="header" @click="${() => this.isOpen = !this.isOpen}">
          <span>${this.title}</span>
          <span class="arrow ${this.isOpen ? 'open' : ''}">▼</span>
        </div>
        <div class="content ${this.isOpen ? 'open' : ''}">
          <slot></slot>
        </div>
      </div>
    `;
  }
}