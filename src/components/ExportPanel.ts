import { LitElement, html, css } from 'lit';
import { t } from '../i18n/locales';
import '@vaadin/button';
import { ExportCss } from './ExportCss';
import { HTMLInputElement, HTMLTextAreaElement } from 'typescript';

class ExportPanel extends LitElement {
  static override styles = [
    ExportCss.styles,
    css`
    :host {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-top: 16px;
    }
  `];

  render() {
    return html`
      <vaadin-button theme="tertiary" @click="${this.exportPDF}"
        >${t.export.saveAsPDF}</vaadin-button
      >
      <vaadin-button theme="tertiary" @click="${this.exportMarkdown}"
        >${t.export.saveAsMarkdown}</vaadin-button
      >
      <vaadin-button theme="tertiary" @click="${this.exportLink}"
        >${t.export.copyLink}</vaadin-button
      >
    `;
  }

  exportPDF() {
    // Get the content from the text area (specification)
    const textAreaElement = this.parentElement?.querySelector('vaadin-text-area') as HTMLTextAreaElement;
    if (!textAreaElement) {
      console.error('Text area element not found');
      return;
    }
    
    const content = textAreaElement.value;
    const projectName = (document.querySelector('#name') as HTMLInputElement)?.value || 'SpecPilot';
    
    // Create a hidden element with formatted content
    const element = document.createElement('div');
    element.innerHTML = `
      <h1>${projectName} - Technical Specification</h1>
      <div style="white-space: pre-wrap; font-family: Arial, sans-serif;">${content}</div>
    `;
    element.style.position = 'absolute';
    element.style.left = '-9999px';
    document.body.appendChild(element);
    
    // Use browser's print functionality to create PDF
    const printWindow = window.open('', '_blank');
    
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>${projectName} - Technical Specification</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
              }
              h1 {
                color: #333;
                border-bottom: 1px solid #ccc;
                padding-bottom: 10px;
              }
              pre {
                white-space: pre-wrap;
                background: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
              }
            </style>
          </head>
          <body>
            <h1>${projectName} - Technical Specification</h1>
            <div style="white-space: pre-wrap;">${content}</div>
            <script>
              window.onload = function() {
                window.print();
                window.addEventListener('afterprint', function() {
                  window.close();
                });
              }
            </script>
          </body>
        </html>
      `);
      printWindow.document.close();
    } else {
      alert('Please allow popups to download the PDF specification');
    }
    
    // Clean up
    document.body.removeChild(element);
  }

  exportMarkdown() {
    // Implementation for Markdown export
    const textAreaElement = this.parentElement?.querySelector('vaadin-text-area');
    if (!textAreaElement) return;
    
    const content = textAreaElement.value;
    const projectName = document.querySelector('#name')?.value || 'SpecPilot';
    
    // Create a simple markdown conversion
    const markdown = `# ${projectName} - Technical Specification\n\n${content}`;
    
    // Create a download link
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(markdown));
    element.setAttribute('download', `${projectName.replace(/\s+/g, '-')}-spec.md`);
    element.style.display = 'none';
    
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

  exportLink() {
    // For simplicity, we'll create a shareable link by copying to clipboard
    const textAreaElement = this.parentElement?.querySelector('vaadin-text-area');
    if (!textAreaElement) return;
    
    // In a real application, this would save to a database and generate a unique URL
    // For now, we'll just copy the content to clipboard
    navigator.clipboard.writeText(textAreaElement.value)
      .then(() => {
        alert('Specification text copied to clipboard!');
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  }
}

customElements.define('export-panel', ExportPanel);