/**
 * Ontonaut Code Editor Widget
 * A clean, marimo-style code editor with custom execution backends
 */

import { EditorView, keymap, lineNumbers, highlightActiveLineGutter, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, highlightActiveLine } from "https://esm.sh/@codemirror/view@6.23.0";
import { EditorState } from "https://esm.sh/@codemirror/state@6.4.0";
import { defaultKeymap, history, historyKeymap } from "https://esm.sh/@codemirror/commands@6.3.3";
import { syntaxHighlighting, defaultHighlightStyle, bracketMatching } from "https://esm.sh/@codemirror/language@6.10.0";
import { python } from "https://esm.sh/@codemirror/lang-python@6.1.4";
import { javascript } from "https://esm.sh/@codemirror/lang-javascript@6.2.1";
import { json } from "https://esm.sh/@codemirror/lang-json@6.0.1";
import { oneDark } from "https://esm.sh/@codemirror/theme-one-dark@6.1.2";

function render({ model, el }) {
  // Create the main container
  const container = document.createElement("div");
  container.className = "ontonaut-container";

  // Create the editor section
  const editorSection = document.createElement("div");
  editorSection.className = "ontonaut-editor-section";

  // Get language extension
  const getLanguageExtension = (lang) => {
    const langMap = {
      python: python(),
      javascript: javascript(),
      json: json(),
    };
    return langMap[lang.toLowerCase()] || python();
  };

  // Create CodeMirror editor
  let editorView;
  const createEditor = (theme) => {
    const extensions = [
      lineNumbers(),
      highlightActiveLineGutter(),
      highlightSpecialChars(),
      history(),
      drawSelection(),
      dropCursor(),
      EditorState.allowMultipleSelections.of(true),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      bracketMatching(),
      rectangularSelection(),
      highlightActiveLine(),
      keymap.of([
        ...defaultKeymap,
        ...historyKeymap,
      ]),
      getLanguageExtension(model.get("language")),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          const newCode = update.state.doc.toString();
          model.set("code", newCode);
          model.save_changes();
        }
      }),
      EditorView.editable.of(!model.get("read_only")),
    ];

    if (theme === "dark") {
      extensions.push(oneDark);
    }

    const state = EditorState.create({
      doc: model.get("code"),
      extensions,
    });

    editorView = new EditorView({
      state,
      parent: editorSection,
    });
  };

  createEditor(model.get("theme"));

  // Create the toolbar
  const toolbar = document.createElement("div");
  toolbar.className = "ontonaut-toolbar";

  // Language indicator
  const langIndicator = document.createElement("span");
  langIndicator.className = "ontonaut-language";
  langIndicator.textContent = model.get("language");
  toolbar.appendChild(langIndicator);

  // Run button
  const runButton = document.createElement("button");
  runButton.className = "ontonaut-run-button";
  runButton.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M4 2v12l10-6z"/>
    </svg>
    <span>Run</span>
  `;
  runButton.onclick = () => {
    const code = editorView.state.doc.toString();
    model.send({ type: "execute", code });
  };
  toolbar.appendChild(runButton);

  // Clear button
  const clearButton = document.createElement("button");
  clearButton.className = "ontonaut-clear-button";
  clearButton.textContent = "Clear";
  clearButton.onclick = () => {
    editorView.dispatch({
      changes: { from: 0, to: editorView.state.doc.length, insert: "" }
    });
    model.set("code", "");
    model.save_changes();
  };
  toolbar.appendChild(clearButton);

  // Create the output section
  const outputSection = document.createElement("div");
  outputSection.className = "ontonaut-output-section";

  const outputLabel = document.createElement("div");
  outputLabel.className = "ontonaut-output-label";
  outputLabel.textContent = "Output";

  const outputContent = document.createElement("pre");
  outputContent.className = "ontonaut-output";
  outputContent.textContent = model.get("output") || "";

  const errorContent = document.createElement("pre");
  errorContent.className = "ontonaut-error";
  errorContent.textContent = model.get("error") || "";

  outputSection.appendChild(outputLabel);
  outputSection.appendChild(outputContent);
  outputSection.appendChild(errorContent);

  // Assemble the widget
  container.appendChild(toolbar);
  container.appendChild(editorSection);
  container.appendChild(outputSection);
  el.appendChild(container);

  // Add keyboard shortcut for Cmd/Ctrl + Enter to run
  const runKeymap = EditorView.domEventHandlers({
    keydown: (e, view) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        runButton.click();
        return true;
      }
      return false;
    }
  });
  editorView.dispatch({
    effects: EditorState.appendConfig.of(runKeymap)
  });

  // Listen for changes from Python
  model.on("change:code", () => {
    const currentCode = editorView.state.doc.toString();
    const newCode = model.get("code");
    if (currentCode !== newCode) {
      editorView.dispatch({
        changes: { from: 0, to: editorView.state.doc.length, insert: newCode }
      });
    }
  });

  model.on("change:output", () => {
    outputContent.textContent = model.get("output");
    if (model.get("output")) {
      outputSection.style.display = "block";
    }
  });

  model.on("change:error", () => {
    errorContent.textContent = model.get("error");
    if (model.get("error")) {
      outputSection.style.display = "block";
    } else {
      errorContent.textContent = "";
    }
  });

  model.on("change:language", () => {
    langIndicator.textContent = model.get("language");
    // Recreate editor with new language
    const code = editorView.state.doc.toString();
    editorView.destroy();
    editorSection.innerHTML = "";
    createEditor(model.get("theme"));
    editorView.dispatch({
      changes: { from: 0, to: 0, insert: code }
    });
    // Re-apply keyboard shortcut
    editorView.dispatch({
      effects: EditorState.appendConfig.of(runKeymap)
    });
  });

  model.on("change:theme", () => {
    container.setAttribute("data-theme", model.get("theme"));
    // Recreate editor with new theme
    const code = editorView.state.doc.toString();
    editorView.destroy();
    editorSection.innerHTML = "";
    createEditor(model.get("theme"));
    editorView.dispatch({
      changes: { from: 0, to: 0, insert: code }
    });
    // Re-apply keyboard shortcut
    editorView.dispatch({
      effects: EditorState.appendConfig.of(runKeymap)
    });
  });

  model.on("change:read_only", () => {
    editorView.dispatch({
      effects: EditorView.editable.reconfigure(EditorView.editable.of(!model.get("read_only")))
    });
  });

  // Set initial theme
  container.setAttribute("data-theme", model.get("theme"));

  // Hide output initially if empty
  if (!model.get("output") && !model.get("error")) {
    outputSection.style.display = "none";
  }
}

export default { render };
