# Smart_Autofill_Extension
Smart Autofill is an AI-assisted Chrome extension that parses user details from uploaded PDFs (like resumes), stores them locally, and automatically fills out web forms including Google Forms and other online applications.

Perfect 👏 Since you’ve got your extension now working end-to-end parsing PDFs, saving data, and autofilling forms (even Google Forms) here’s a **clean, professional `README.md`** you can put on GitHub.

---

## 🧠 Smart Autofill Chrome Extension

**Smart Autofill** is an AI-assisted Chrome extension that parses user details from uploaded PDFs (like resumes), stores them locally, and automatically fills out web forms — including Google Forms and other online applications.

---

### 🚀 Features

* 🧾 **AI-based PDF Parsing:** Upload a resume or document; it’s analyzed by an AI backend to extract key fields.
* ⚙️ **Smart Autofill:** Auto-fills detected form fields such as name, email, phone, company, and role.
* ✍️ **Custom Fields:** Add your own key–value fields for extra information.
* 💾 **Persistent Storage:** Saves data in Chrome storage so it’s retained across sessions.
* 📋 **Supports Google Forms:** Detects Google Form structure and fills text/textarea fields accurately.
* 🔄 **Manual + Auto Script Injection:** Ensures content scripts load even on pre-opened pages.

---

### Demo 

!(Screenshot 2025-11-11 222005.png)
!(Screenshot 2025-11-11 222014.png)

---

### 📂 Project Structure

```
Smart-Autofill/
│
├── manifest.json
│
├── popup/
│   ├── index.html          # Extension popup UI
│   ├── input.css           # Tailwind input (if used)
│   ├── output.css          # Compiled Tailwind CSS
│   └── popup.js            # Handles UI, PDF upload, and messaging
│
└── scripts/
    ├── background.js       # Service worker (logs, setup)
    └── content.js          # Injected into pages to perform autofill
```

---

### 🧩 manifest.json

Key configuration:

```json
{
  "manifest_version": 3,
  "name": "Autofill Extension",
  "version": "1.0",
  "description": "An extension to autofill forms",
  "permissions": [
    "storage",
    "activeTab",
    "scripting",
    "tabs"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "action": {
    "default_popup": "popup/index.html"
  },
  "background": {
    "service_worker": "scripts/background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>","https://docs.google.com/forms/*"],
      "js": ["scripts/content.js"],
      "all_frames": true
    }
  ],
  "options_page": "options/options.html"
}

```

---

### ⚙️ Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Pragati-cloud/Smart_Autofill_Extension.git
   cd AUTOFILL_EXTENSION
   ```

2. **Load the extension**

   * Open Chrome → go to `chrome://extensions/`
   * Turn on **Developer Mode**
   * Click **Load unpacked**
   * Select the project folder

3. **Verify**

   * Click the 🧩 Extension icon → Pin “Smart Autofill”
   * Open it and try uploading your PDF

4. **Backend (AI Parser)**

   * Backend runs locally at:

     ```
     http://127.0.0.1:8000/upload
     ```
   * Receives the uploaded file, extracts fields, and returns a JSON response like:

     ```json
     {
       "name": "Pragati Mishra",
       "email": "pragatimis2004@gmail.com",
       "phone": "+91XXXXXXXX",
       "company": "",
       "role": ""
     }
     ```

---

### 🧠 How It Works

1. **Upload Resume:** PDF sent to backend for AI-based parsing.
2. **Field Detection:** Extracted data is shown in popup form fields.
3. **Save / Edit:** Modify or add fields manually.
4. **Autofill:** Click **Autofill** — it injects `content.js` and fills forms on the current tab.

---

### 🧩 Supported Sites

* ✅ Google Forms
* ✅ Job application forms
* ✅ Contact and registration forms
* ✅ Generic HTML forms with input/textarea fields

---

### 🐞 Debugging Tips

* If popup shows `ERR_FILE_NOT_FOUND` → check `manifest.json` path for popup.
* If “Receiving end does not exist” → ensure you’ve injected `content.js` manually (already handled in the updated `popup.js`).
* Check console logs (Popup → Inspect → Console) for runtime errors.

---

### 🧰 Tech Stack

| Component          | Technology                              |
| ------------------ | --------------------------------------- |
| Frontend           | HTML, CSS (Tailwind), JavaScript        |
| Extension Platform | Chrome Manifest v3                      |
| Storage            | `chrome.storage.local`                  |
| Backend (optional) | FastAPI / Flask with AI Parser          |
| AI Model           | Resume field extraction using LLM / NLP |

---

### 📜 License

License © 2025 — Pragati Mishra
