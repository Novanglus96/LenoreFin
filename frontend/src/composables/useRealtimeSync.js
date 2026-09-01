import { ref, onMounted, onUnmounted } from "vue";
import { useQueryClient } from "@tanstack/vue-query";

// How long to wait before reconnecting, doubling up to a ceiling. The old
// fixed 3s was fine against a server that comes straight back and punishing
// against one that does not: a tab left open against a dead endpoint opened a
// socket every three seconds for as long as it was there.
const BASE_DELAY = 3000;
const MAX_DELAY = 60000;
// A connection has to survive this long to count as a success. Resetting the
// backoff on `open` alone means a server that accepts a socket and drops it a
// second later is retried every three seconds forever — the flapping case,
// which is the one that actually happens.
const STABLE_MS = 30000;

export function useRealtimeSync() {
  const queryClient = useQueryClient();
  const connected = ref(false);
  let ws = null;
  let reconnectTimer = null;
  let attempts = 0;
  let stopped = false;

  function detach(socket) {
    socket.onopen = null;
    socket.onmessage = null;
    socket.onclose = null;
    socket.onerror = null;
  }

  function scheduleReconnect() {
    // Clearing first is what keeps this to a single chain. `onclose` used to
    // assign over a pending timer without cancelling it, so two closes in
    // flight left an orphan running: each cycle could start a connect loop
    // alongside the one already going, and they multiply rather than replace.
    if (reconnectTimer) clearTimeout(reconnectTimer);
    const delay = Math.min(BASE_DELAY * 2 ** attempts, MAX_DELAY);
    attempts += 1;
    reconnectTimer = setTimeout(connect, delay);
  }

  function connect() {
    if (stopped) return;
    reconnectTimer = null;

    // Never more than one live socket. Without this a stray connect() while
    // another is still open orphans the first: nothing references it any more,
    // but it stays connected and keeps delivering invalidations.
    if (ws) {
      detach(ws);
      ws.close();
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(
      `${protocol}//${window.location.host}/ws/sync/`,
    );
    ws = socket;
    const openedAt = Date.now();

    socket.onopen = () => {
      connected.value = true;
    };

    socket.onmessage = event => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "invalidate" && Array.isArray(data.keys)) {
          data.keys.forEach(key =>
            queryClient.invalidateQueries({ queryKey: [key] }),
          );
        }
      } catch {
        // ignore malformed messages
      }
    };

    socket.onclose = () => {
      // A close from a socket already replaced says nothing about the current
      // one, and letting it schedule a reconnect is how one dead socket became
      // two live connect loops.
      if (socket !== ws) return;
      connected.value = false;
      if (Date.now() - openedAt >= STABLE_MS) attempts = 0;
      if (!stopped) scheduleReconnect();
    };

    // `socket`, not the outer `ws`. The old code closed whichever socket the
    // variable pointed at by the time the error fired, so a late error from a
    // discarded socket would kill its healthy replacement — and that close
    // then scheduled another reconnect on top of the one already pending.
    socket.onerror = () => socket.close();
  }

  onMounted(connect);

  onUnmounted(() => {
    stopped = true;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (ws) {
      detach(ws); // no reconnect on an intentional unmount
      ws.close();
      ws = null;
    }
  });

  return { connected };
}
