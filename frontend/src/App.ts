import { LitElement, html, css } from "lit";
import { customElement, state } from 'lit/decorators.js';
import "./components/HeroSection";
import "./components/SmartForm";
import "./components/EditorArea";
import "./components/LanguageSelector";
import "./components/AIStatusIndicator";

@customElement('app-root')
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
      min-height: 95vh;
    }

    @media screen and (min-width: 960px) {
      :host {
        max-width: 1200px;
      }

    language-selector {
      position: absolute;
      top: 30px;
      right: 10px;
    }

    ai-status-indicator {
      position: absolute;
      top: 30px;
      left: 20px;
    }
  `;

  render() {
    return html`
      <ai-status-indicator></ai-status-indicator> <language-selector></language-selector>
      <hero-section></hero-section>
      <smart-form></smart-form>
    `;
  }
}
