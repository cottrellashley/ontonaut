/**
 * Ontonaut Code Editor Widget
 * A clean, marimo-style code editor with custom execution backends
 */

// Simple syntax highlighter for Python
function highlightPython(code) {
  // Escape HTML first
  let html = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Comments (do first to avoid highlighting within comments)
  html = html.replace(/(#.*$)/gm, '<span class="syntax-comment">$1</span>');

  // Strings (triple quotes, then single/double)
  html = html.replace(/("""[\s\S]*?"""|'''[\s\S]*?''')/g, '<span class="syntax-string">$1</span>');
  html = html.replace(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, '<span class="syntax-string">$1</span>');

  // Keywords
  const keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally',
                   'with', 'as', 'import', 'from', 'return', 'yield', 'break', 'continue', 'pass',
                   'raise', 'assert', 'del', 'global', 'nonlocal', 'lambda', 'and', 'or', 'not',
                   'is', 'in', 'True', 'False', 'None', 'async', 'await'];
  const keywordPattern = new RegExp(`\\b(${keywords.join('|')})\\b`, 'g');
  html = html.replace(keywordPattern, '<span class="syntax-keyword">$1</span>');

  // Numbers
  html = html.replace(/\b(\d+\.?\d*|\.\d+)\b/g, '<span class="syntax-number">$1</span>');

  // Function definitions
  html = html.replace(/\b(def)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g,
    '<span class="syntax-keyword">$1</span> <span class="syntax-function">$2</span>');

  // Decorators
  html = html.replace(/^(\s*)(@[a-zA-Z_][a-zA-Z0-9_]*)/gm,
    '$1<span class="syntax-decorator">$2</span>');

  return html;
}

function highlightJavaScript(code) {
  let html = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Comments
  html = html.replace(/(\/\/.*$)/gm, '<span class="syntax-comment">$1</span>');
  html = html.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="syntax-comment">$1</span>');

  // Strings
  html = html.replace(/(`(?:[^`\\]|\\.)*`|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, '<span class="syntax-string">$1</span>');

  // Keywords
  const keywords = ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'do',
                   'switch', 'case', 'break', 'continue', 'return', 'try', 'catch', 'finally',
                   'throw', 'new', 'class', 'extends', 'import', 'export', 'default', 'async', 'await'];
  const keywordPattern = new RegExp(`\\b(${keywords.join('|')})\\b`, 'g');
  html = html.replace(keywordPattern, '<span class="syntax-keyword">$1</span>');

  // Numbers
  html = html.replace(/\b(\d+\.?\d*|\.\d+)\b/g, '<span class="syntax-number">$1</span>');

  return html;
}

function highlightJSON(code) {
  let html = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Strings (keys and values)
  html = html.replace(/"([^"]+)"(\s*):/g, '<span class="syntax-key">"$1"</span>$2:');
  html = html.replace(/:\s*"([^"]*)"/g, ': <span class="syntax-string">"$1"</span>');

  // Numbers
  html = html.replace(/:\s*(-?\d+\.?\d*)/g, ': <span class="syntax-number">$1</span>');

  // Booleans and null
  html = html.replace(/\b(true|false|null)\b/g, '<span class="syntax-keyword">$1</span>');

  return html;
}

function highlightCode(code, language) {
  const lang = language.toLowerCase();
  if (lang === 'python' || lang === 'py') {
    return highlightPython(code);
  } else if (lang === 'javascript' || lang === 'js') {
    return highlightJavaScript(code);
  } else if (lang === 'json') {
    return highlightJSON(code);
  }
  // Default: just escape HTML
  return code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function render({ model, el }) {
  // Create the main container
  const container = document.createElement("div");
  container.className = "ontonaut-container";

  // Create the editor section
  const editorSection = document.createElement("div");
  editorSection.className = "ontonaut-editor-section";

  // Create contenteditable div for syntax highlighting
  const editorDiv = document.createElement("div");
  editorDiv.className = "ontonaut-editor";
  editorDiv.contentEditable = !model.get("read_only");
  editorDiv.spellcheck = false;
  editorDiv.innerHTML = highlightCode(model.get("code"), model.get("language"));

  if (!model.get("code")) {
    editorDiv.setAttribute("data-placeholder", model.get("placeholder"));
  }

  // Track plain text content
  let currentCode = model.get("code");

  // Update highlighting on input
  let highlightTimer = null;
  let isHighlighting = false;

  const getCursorPosition = () => {
    const selection = window.getSelection();
    if (selection.rangeCount === 0) return 0;

    const range = selection.getRangeAt(0);
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(editorDiv);
    preCaretRange.setEnd(range.endContainer, range.endOffset);
    return preCaretRange.toString().length;
  };

  const setCursorPosition = (position) => {
    const selection = window.getSelection();
    const range = document.createRange();

    let charCount = 0;
    const nodeStack = [editorDiv];
    let node;
    let foundPosition = false;

    while (!foundPosition && (node = nodeStack.pop())) {
      if (node.nodeType === Node.TEXT_NODE) {
        const nextCharCount = charCount + node.length;
        if (position <= nextCharCount) {
          range.setStart(node, position - charCount);
          range.collapse(true);
          foundPosition = true;
        }
        charCount = nextCharCount;
      } else {
        for (let i = node.childNodes.length - 1; i >= 0; i--) {
          nodeStack.push(node.childNodes[i]);
        }
      }
    }

    if (foundPosition) {
      selection.removeAllRanges();
      selection.addRange(range);
    }
  };

  const applyHighlighting = () => {
    if (isHighlighting) return;
    isHighlighting = true;

    const cursorPos = getCursorPosition();
    const newCode = editorDiv.textContent || "";

    if (newCode !== currentCode) {
      currentCode = newCode;
      editorDiv.innerHTML = highlightCode(newCode, model.get("language"));

      // Restore cursor
      requestAnimationFrame(() => {
        setCursorPosition(cursorPos);
        isHighlighting = false;
      });

      // Update model
      model.set("code", newCode);
      model.save_changes();

      // Update placeholder
      if (newCode) {
        editorDiv.removeAttribute("data-placeholder");
      } else {
        editorDiv.setAttribute("data-placeholder", model.get("placeholder"));
      }
    } else {
      isHighlighting = false;
    }
  };

  const scheduleHighlighting = () => {
    // Update model immediately for responsiveness
    const newCode = editorDiv.textContent || "";
    if (newCode !== currentCode) {
      currentCode = newCode;
      model.set("code", newCode);
      model.save_changes();
    }

    // Debounce highlighting update
    clearTimeout(highlightTimer);
    highlightTimer = setTimeout(applyHighlighting, 300);
  };

  editorDiv.addEventListener("input", scheduleHighlighting);
  editorDiv.addEventListener("blur", () => {
    clearTimeout(highlightTimer);
    applyHighlighting();
  });

  // Add line numbers if enabled
  if (model.get("line_numbers")) {
    const lineNumbersContainer = document.createElement("div");
    lineNumbersContainer.className = "ontonaut-line-numbers";
    editorSection.appendChild(lineNumbersContainer);

    const updateLineNumbers = () => {
      const lines = (editorDiv.textContent || "").split("\n").length;
      lineNumbersContainer.innerHTML = Array.from(
        { length: lines },
        (_, i) => `<div class="line-number">${i + 1}</div>`
      ).join("");
    };

    updateLineNumbers();
    editorDiv.addEventListener("input", updateLineNumbers);
  }

  editorSection.appendChild(editorDiv);

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
    model.send({ type: "execute", code: editorDiv.textContent || "" });
  };
  toolbar.appendChild(runButton);

  // Clear button
  const clearButton = document.createElement("button");
  clearButton.className = "ontonaut-clear-button";
  clearButton.textContent = "Clear";
  clearButton.onclick = () => {
    editorDiv.textContent = "";
    currentCode = "";
    model.set("code", "");
    model.save_changes();
    editorDiv.setAttribute("data-placeholder", model.get("placeholder"));
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

  // Handle keyboard shortcuts
  editorDiv.addEventListener("keydown", (e) => {
    // Cmd/Ctrl + Enter to run
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      runButton.click();
    }

    // Tab key for indentation
    if (e.key === "Tab") {
      e.preventDefault();
      document.execCommand("insertText", false, "    ");
    }
  });

  // Listen for changes from Python
  model.on("change:code", () => {
    const newCode = model.get("code");
    if ((editorDiv.textContent || "") !== newCode) {
      currentCode = newCode;
      editorDiv.innerHTML = highlightCode(newCode, model.get("language"));
      if (newCode) {
        editorDiv.removeAttribute("data-placeholder");
      } else {
        editorDiv.setAttribute("data-placeholder", model.get("placeholder"));
      }
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
    editorDiv.innerHTML = highlightCode(currentCode, model.get("language"));
  });

  model.on("change:theme", () => {
    container.setAttribute("data-theme", model.get("theme"));
  });

  model.on("change:read_only", () => {
    editorDiv.contentEditable = !model.get("read_only");
  });

  // Set initial theme
  container.setAttribute("data-theme", model.get("theme"));

  // Hide output initially if empty
  if (!model.get("output") && !model.get("error")) {
    outputSection.style.display = "none";
  }
}

export default { render };
