import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';
import '@vaadin/button';

class HeroSection extends LitElement {
  static override styles = css`
      @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap');
      :host {
        display: flex;
        flex-direction: column;
        text-align: center;
      }

      .title {
        font-family: "Roboto Mono", monospace;
        font-optical-sizing: auto;
        font-weight: 400;
        font-style: normal;
        font-size: 42px;
        color: #aa00bf;
        margin-bottom: 0px;
      }
    `;
  
  render() {
    return html`
      <section class="hero">
        <h1 class="title">${t.hero.title}</h1>
        <p>${t.hero.description}</p>
      </section>
    `;
  }

  startGeneration() {}
}

customElements.define('hero-section', HeroSection);
