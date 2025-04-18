import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';

class HeroSection extends LitElement {
  render() {
    return html`
      <section class="hero">
        <h1>Welcome to SpecPilot</h1>
        <p>Quickly generate high-quality specifications for your projects.</p>
        <button @click="${this.startGeneration}">Let’s generate your spec</button>
      </section>
    `;
  }

  startGeneration() {
  }
}

customElements.define('hero-section', HeroSection);

