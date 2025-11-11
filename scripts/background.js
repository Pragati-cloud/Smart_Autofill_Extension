chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "AUTOFILL_REQUEST") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (tab?.id) {
        chrome.tabs.sendMessage(
          tab.id,
          { action: "AUTOFILL", template: msg.template },
          (res) => sendResponse(res || { success: false })
        );
      } else {
        sendResponse({ success: false, error: "No active tab" });
      }
    });
    return true;
  }
});
