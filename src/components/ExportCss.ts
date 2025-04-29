import { LitElement, css } from 'lit';

export class ExportCss extends LitElement {
  static override styles = css`
    vaadin-button {
      cursor: pointer;
      --vaadin-button-primary-background: #5395fc;
      --vaadin-button-tertiary-text-color: #2aaefa;
    }

    vaadin-text-field {
      width: 400px;
      color: #ffffff;
      --vaadin-input-field-background: #272829;
      --vaadin-input-field-border-radius: 8px;
      --vaadin-input-field-border-color: #838d96;
      --vaadin-input-field-border-width: 1px;
    }

    vaadin-text-area {
      color: #ffffff;
      --vaadin-input-field-background: #272829;
      --vaadin-input-field-border-radius: 8px;
      --vaadin-input-field-border-color: #838d96;
      --vaadin-input-field-border-width: 1px;
    }
  `;
}
