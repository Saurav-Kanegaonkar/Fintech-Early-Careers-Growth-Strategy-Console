const fs = require("fs/promises");
const path = require("path");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const imageDir = path.join(root, "docs", "images");
const port = process.env.PORT || "4173";

async function capture() {
  await fs.mkdir(imageDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 }, deviceScaleFactor: 1 });
  const messages = [];

  page.on("console", (message) => messages.push(`${message.type()}: ${message.text()}`));
  page.on("pageerror", (error) => messages.push(`pageerror: ${error.message}`));

  await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(imageDir, "growth-cockpit.png"), fullPage: false });

  await page.click('[data-view="cohorts"]');
  await page.waitForTimeout(250);
  await page.screenshot({ path: path.join(imageDir, "cohort-priority.png"), fullPage: false });

  await page.click('[data-view="experiments"]');
  await page.waitForTimeout(250);
  await page.screenshot({ path: path.join(imageDir, "experiment-lab.png"), fullPage: false });

  await page.click('[data-view="readiness"]');
  await page.waitForTimeout(250);
  await page.screenshot({ path: path.join(imageDir, "readiness-queue.png"), fullPage: false });

  const title = await page.textContent("h1");
  const experimentCount = await page.locator(".experiment-card").count();
  const readinessCount = await page.locator(".readiness-card").count();
  await browser.close();

  console.log(JSON.stringify({
    title,
    experimentCount,
    readinessCount,
    messages,
    screenshots: [
      "growth-cockpit.png",
      "cohort-priority.png",
      "experiment-lab.png",
      "readiness-queue.png",
    ],
  }, null, 2));
}

capture().catch((error) => {
  console.error(error);
  process.exit(1);
});
