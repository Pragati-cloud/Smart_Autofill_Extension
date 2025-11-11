chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action !== "AUTOFILL") return;

  const { template } = msg;

  function fillField(el, val) {
    if (!el) return;
    el.focus();
    el.value = val;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  // ---- GOOGLE FORMS ----
  function fillGoogleForms() {
    const items = document.querySelectorAll("div[role='listitem']");
    let filled = 0;

    template.forEach(({ attr, val }) => {
      items.forEach((item) => {
        const label =
          item.querySelector("div[role='heading']") ||
          item.querySelector("span") ||
          item.querySelector("label");

        const input =
          item.querySelector("input[type='text']") ||
          item.querySelector("textarea");

        if (label && input && label.innerText.toLowerCase().includes(attr.toLowerCase())) {
          fillField(input, val);
          filled++;
        }
      });
    });
    return filled > 0;
  }

  // ---- NORMAL FORMS ----
  function fillNormalForms() {
    let filled = 0;
    template.forEach(({ attr, val }) => {
      const selector = `
        input[name*="${attr}"],
        input[id*="${attr}"],
        input[placeholder*="${attr}"],
        textarea[name*="${attr}"],
        textarea[placeholder*="${attr}"]
      `;
      const field = document.querySelector(selector);
      if (field) {
        fillField(field, val);
        filled++;
      }
    });
    return filled > 0;
  }

  // ---- Retry Logic for Dynamic Forms ----
  let attempts = 0;
  const maxAttempts = 15;

  const interval = setInterval(() => {
    let success = false;

    if (window.location.hostname.includes("docs.google.com"))
      success = fillGoogleForms();
    else success = fillNormalForms();

    attempts++;

    if (success || attempts >= maxAttempts) {
      clearInterval(interval);
      sendResponse({ success });
    }
  }, 700);

  // Keep listener alive
  return true;
});
