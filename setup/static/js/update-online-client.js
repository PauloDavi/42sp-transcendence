class OnlineStatusClient extends BaseWebSocket {
  constructor() {
    super("online-status");
  }
}

const onlineStatus = new OnlineStatusClient();
