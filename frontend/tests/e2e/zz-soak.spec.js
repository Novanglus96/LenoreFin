import { test } from "@playwright/test";
import { login } from "./auth.js";
import fs from "fs";

const OUT = process.env.SOAK_LOG;

test("forecast soak", async ({ page }) => {
  test.setTimeout(90 * 60 * 1000);
  await page.addInitScript(() => {
    window.__ws = 0; window.__wsLive = 0; window.__timers = 0;
    const RealWS = window.WebSocket;
    window.WebSocket = function (...a) {
      window.__ws++;
      const s = new RealWS(...a);
      s.addEventListener("open", () => window.__wsLive++);
      s.addEventListener("close", () => window.__wsLive--);
      return s;
    };
    window.WebSocket.prototype = RealWS.prototype;
    Object.assign(window.WebSocket, RealWS);
    const rST = window.setTimeout;
    window.setTimeout = function (...a) { window.__timers++; return rST.apply(this, a); };
  });

  let reqs = 0;
  page.on("request", () => reqs++);
  const errs = [];
  page.on("console", m => m.type() === "error" && errs.push(m.text()));

  await login(page);
  await page.goto("/forecast");
  fs.writeFileSync(OUT, "start " + new Date().toISOString() + "\n");

  for (let i = 0; i < 80; i++) {
    let line;
    try {
      const t0 = Date.now();
      const s = await page.evaluate(() => ({
        ws: window.__ws, live: window.__wsLive, timers: window.__timers,
        heap: performance.memory ? performance.memory.usedJSHeapSize : 0,
        nodes: document.getElementsByTagName("*").length,
      }));
      line = `t=${i}min heap=${(s.heap / 1048576).toFixed(1)}MB nodes=${s.nodes} ws=${s.ws} live=${s.live} timers=${s.timers} reqs=${reqs} errs=${errs.length} evalRTT=${Date.now() - t0}ms`;
    } catch (e) {
      line = `t=${i}min EVAL FAILED (main thread blocked?) ${String(e).slice(0, 120)}`;
    }
    fs.appendFileSync(OUT, line + "\n");
    await page.waitForTimeout(60_000);
  }
});
