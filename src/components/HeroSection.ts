import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';
import '@vaadin/button';

class HeroSection extends LitElement {
  render() {
    return html`
      <section class="hero">
        <h1>Welcome to SpecPilot</h1>
        <p>Quickly generate high-quality specifications for your projects.</p>
        <vaadin-button theme="primary" @click="${this.startGeneration}">
          Let’s generate your spec
        </vaadin-button>
      </section>
    `;
  }

  startGeneration() {}
}

customElements.define('hero-section', HeroSection);
