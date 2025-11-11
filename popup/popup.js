document.addEventListener("DOMContentLoaded", () => {
  const pdfInput = document.getElementById("pdfUpload");
  const autofillBtn = document.getElementById("autofill");
  const statusBox = document.getElementById("statusBox");
  const addFieldBtn = document.getElementById("addField");
  const customFieldsDiv = document.getElementById("customFields");

  const BASE_URL = "http://127.0.0.1:8000";
  const inputs = {
    name: document.getElementById("name"),
    email: document.getElementById("email"),
    phone: document.getElementById("phone"),
    company: document.getElementById("company"),
    role: document.getElementById("role"),
  };

  function setStatus(msg) {
    statusBox.innerText = msg;
  }

  // ========== Storage Handling ==========
  function saveToStorage() {
    const data = {};
    for (let key in inputs) data[key] = inputs[key].value;

    // Include custom fields
    const customFields = [];
    customFieldsDiv.querySelectorAll(".custom-field").forEach((row) => {
      const attr = row.querySelector(".attr").value;
      const val = row.querySelector(".val").value;
      if (attr && val) customFields.push({ attr, val });
    });
    data.custom = customFields;

    chrome.storage.local.set({ autofillData: data });
  }

  

  function loadFromStorage() {
    chrome.storage.local.get(["autofillData"], (result) => {
      const data = result.autofillData || {};
      for (let key in inputs) if (data[key]) inputs[key].value = data[key];
      if (data.custom) data.custom.forEach(addCustomFieldFromData);
    });
  }

  // ========== Custom Field Logic ==========
  function addCustomFieldFromData({ attr, val }) {
    const div = document.createElement("div");
    div.classList.add("custom-field");
    div.innerHTML = `
      <input type="text" class="attr" placeholder="Field name" value="${attr}" />
      <input type="text" class="val" placeholder="Value" value="${val}" />
      <button class="remove">✕</button>
    `;
    div.querySelector(".remove").addEventListener("click", () => {
      div.remove();
      saveToStorage();
    });
    div.querySelectorAll("input").forEach((i) => i.addEventListener("input", saveToStorage));
    customFieldsDiv.appendChild(div);
  }

  addFieldBtn.addEventListener("click", () => {
    addCustomFieldFromData({ attr: "", val: "" });
  });

  // Save whenever a base field changes
  Object.values(inputs).forEach((input) => {
    input.addEventListener("input", saveToStorage);
  });

  loadFromStorage();

  // ========== PDF Upload ==========
  async function uploadPDF(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE_URL}/upload-pdf`, { method: "POST", body: formData });
    const data = await res.json();
    return data.raw_text;
  }

  async function analyzeText(rawText) {
    const formData = new FormData();
    formData.append("raw_text", rawText);
    formData.append("use_ai", "true");
    const res = await fetch(`${BASE_URL}/analyze-raw-text`, { method: "POST", body: formData });
    const data = await res.json();
    return data.parsed_data;
  }

  pdfInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setStatus("Parsing PDF...");
    const rawText = await uploadPDF(file);
    setStatus("Analyzing with AI...");
    const parsed = await analyzeText(rawText);

    for (let key in parsed) {
      if (inputs[key]) inputs[key].value = parsed[key];
    }
    saveToStorage();
    setStatus("Done ✅");
  });

 // ========== Autofill ==========
autofillBtn.addEventListener("click", async () => {
  const template = [];

  // Fixed fields
  for (let key in inputs) {
    if (inputs[key].value) template.push({ attr: key, val: inputs[key].value });
  }

  // Custom fields
  customFieldsDiv.querySelectorAll(".custom-field").forEach((row) => {
    const attr = row.querySelector(".attr").value;
    const val = row.querySelector(".val").value;
    if (attr && val) template.push({ attr, val });
  });

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // ✅ Inject content script manually (important fix)
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["scripts/content.js"]
  });

  // ✅ Then send message to page
  chrome.tabs.sendMessage(tab.id, { action: "AUTOFILL", template }, (res) => {
    if (chrome.runtime.lastError) {
      console.warn(chrome.runtime.lastError);
      setStatus("No response from page ❌");
      return;
    }
    setStatus(res?.success ? "Autofilled ✅" : "Could not fill ❌");
  });
});
});
