import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';
import '@vaadin/button';

class HeroSection extends LitElement {
  static override styles = css`
      :host {
        display: flex;
        flex-direction: column;
        text-align: center;
      }
    `;
  
  render() {
    return html`
      <section class="hero">
        <h1>${t.hero.title}</h1>
        <p>${t.hero.description}</p>
      </section>
    `;
  }

  startGeneration() {}
}

customElements.define('hero-section', HeroSection);
