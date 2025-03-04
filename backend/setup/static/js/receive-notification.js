class NotificationClient extends BaseWebSocket {
  constructor() {
    super("notifications");
    this.setupMessageHandler();
  }

  setupMessageHandler() {
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.action === "redirect") {
        setTimeout(() => {
          window.location.href = data.url;
        }, data.delay || 0);
      } else if (data.message) {
        showToast(
          data.title,
          data.message,
          data.action,
          data.extra_data,
          `bg-${data.tag}`,
          ["success", "danger"].includes(data.tag) ? "text-white" : "text-dark"
        );
      }
    };
  }
}

function getCookie(name) {
  const cookies = document.cookie.split("; ");
  for (let cookie of cookies) {
    let [key, value] = cookie.split("=");
    if (key === name) {
      return decodeURIComponent(value);
    }
  }
  return null;
}

function handleReject(url) {
  fetch(url, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  }).catch((error) => {
    console.error("Erro:", error);
  });
}

function showToast(
  title,
  message,
  action,
  extraData,
  bgClass = "bg-primary",
  colorClass = "text-white"
) {
  const toastContainer = document.getElementById("toasts");

  const toastElement = document.createElement("div");
  toastElement.className = `toast fade show ${bgClass} ${colorClass}`;
  toastElement.setAttribute("role", "alert");
  toastElement.setAttribute("aria-live", "assertive");
  toastElement.setAttribute("data-bs-autohide", "false");

  let actions = "";
  if (action === "match") {
    actions = `
      <div class="mt-2 pt-2 border-top d-flex flex-row">
        <a href="${extraData.accept_url}" class="me-2 ms-auto btn btn-sm btn-success">${extraData.accept_text}</a>
        <button onclick="handleReject('${extraData.reject_url}')" class="btn btn-sm btn-danger" data-bs-dismiss="toast" aria-label="Close">${extraData.reject_text}</button>
      </div>
    `;
  }

  toastElement.innerHTML = `
      <div class="toast-header">
        <strong class="me-auto">${title}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${message}
        ${actions}
      </div>
    `;

  toastContainer.appendChild(toastElement);

  const bsToast = new bootstrap.Toast(toastElement);
  bsToast.show();
}

const notifications = new NotificationClient();
