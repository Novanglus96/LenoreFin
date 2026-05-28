import { ref } from "vue";
import apiClient from "./apiClient";

const isSupported = "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

export function usePushNotifications() {
  const isSubscribed = ref(false);
  const permissionDenied = ref(false);

  async function checkStatus() {
    if (!isSupported) return;
    try {
      const { data } = await apiClient.get("/administration/push/status");
      isSubscribed.value = data.subscribed ?? false;
    } catch {
      // non-fatal
    }
  }

  async function subscribe() {
    if (!isSupported) return;

    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
      permissionDenied.value = permission === "denied";
      return;
    }

    try {
      const { data } = await apiClient.get("/administration/push/vapid-public-key");
      const applicationServerKey = urlBase64ToUint8Array(data.public_key);

      const reg = await navigator.serviceWorker.ready;
      const pushSub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
      });

      const key = pushSub.getKey("p256dh");
      const auth = pushSub.getKey("auth");

      await apiClient.post("/administration/push/subscribe", {
        endpoint: pushSub.endpoint,
        p256dh: btoa(String.fromCharCode(...new Uint8Array(key))),
        auth: btoa(String.fromCharCode(...new Uint8Array(auth))),
      });

      isSubscribed.value = true;
    } catch (e) {
      console.error("Push subscription failed:", e);
    }
  }

  async function unsubscribe() {
    if (!isSupported) return;
    try {
      const reg = await navigator.serviceWorker.ready;
      const pushSub = await reg.pushManager.getSubscription();
      if (pushSub) await pushSub.unsubscribe();
      await apiClient.delete("/administration/push/unsubscribe");
      isSubscribed.value = false;
    } catch (e) {
      console.error("Push unsubscribe failed:", e);
    }
  }

  return { isSupported, isSubscribed, permissionDenied, checkStatus, subscribe, unsubscribe };
}
