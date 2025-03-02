class BaseWebSocket {
  constructor(path) {
    this.wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    this.url = `${this.wsScheme}://${window.location.host}/ws/${path}/`;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 3000;
    this.setupVisibilityHandler();
    this.connect();
  }

  connect() {
    this.socket = new WebSocket(this.url);
    this.setupBaseHandlers();
  }

  setupVisibilityHandler() {
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        this.reconnectAttempts = 0;
        if (this.socket.readyState === WebSocket.CLOSED) {
          console.log("Usuário voltou para a página. Tentando reconectar...");
          this.connect();
        }
      }
    });
  }

  setupBaseHandlers() {
    this.socket.onopen = () => {
      console.log(`WebSocket conectado ao ${this.url}`);
      this.reconnectAttempts = 0;
    };

    this.socket.onerror = (error) => {
      console.error(`Erro no WebSocket ao conectar ao ${this.url}: `, error);
    };

    this.socket.onclose = () => {
      console.log(`WebSocket desconectado do ${this.url}`);

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        console.log(
          `Tentando reconectar em ${this.reconnectInterval / 1000} segundos...`
        );
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, this.reconnectInterval);
      } else {
        console.log("Número máximo de tentativas de reconexão atingido");
      }
    };
  }
}
