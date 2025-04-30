import { LitElement, css } from 'lit';

export class ExportCss extends LitElement {
  static override styles = css`
    vaadin-button {
      cursor: pointer;
      --vaadin-button-primary-background: #5395fc;
      --vaadin-button-tertiary-text-color: #2aaefa;
    }

    vaadin-text-field {
      width: 100%;
      color: #ffffff;
      --vaadin-input-field-background: #272829;
      --vaadin-input-field-border-radius: 8px;
      --vaadin-input-field-border-color: #838d96;
      --vaadin-input-field-border-width: 1px;
    }

    vaadin-text-area {
      color: #ffffff;
      width: 100%;
      --vaadin-input-field-background: #272829;
      --vaadin-input-field-border-radius: 8px;
      --vaadin-input-field-border-color: #838d96;
      --vaadin-input-field-border-width: 1px;
      margin-bottom: 16px;
    }
    
    vaadin-checkbox {
      --vaadin-checkbox-size: 18px;
      --vaadin-checkbox-background-color: #272829;
      --vaadin-checkbox-border-radius: 4px;
      --vaadin-checkbox-border-color: #838d96;
      --vaadin-checkbox-checkmark-color: #5395fc;
      color: #e0e0e0;
      margin-right: 8px;
    }
  `;
}