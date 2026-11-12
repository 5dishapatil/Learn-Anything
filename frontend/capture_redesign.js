import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';

const outDir = path.resolve('..', 'docs', 'screenshots');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

// Find Chrome or Edge executable on Windows
const possiblePaths = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
];

const executablePath = possiblePaths.find((p) => fs.existsSync(p));

async function capture() {
  if (!executablePath) {
    console.error('No Chrome or Edge executable found');
    return;
  }

  console.log(`Using browser executable: ${executablePath}`);
  const browser = await chromium.launch({
    executablePath,
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  const page = await context.newPage();

  console.log('Navigating to http://127.0.0.1:5173...');
  await page.goto('http://127.0.0.1:5173', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);

  // 1. Home Dashboard
  await page.screenshot({ path: path.join(outDir, '01_redesigned_home.png'), fullPage: false });
  console.log('Saved 01_redesigned_home.png');

  // 2. Explore & Onboarding
  await page.click('text="Explore & Onboard"');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(outDir, '02_redesigned_explore.png'), fullPage: false });
  console.log('Saved 02_redesigned_explore.png');

  // 3. Scholar Road Workspace
  await page.click('text="Scholar Road"');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '03_redesigned_scholar_reader.png'), fullPage: false });
  console.log('Saved 03_redesigned_scholar_reader.png');

  // 4. Builder Road Workspace
  await page.click('text="Builder Road"');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '04_redesigned_builder_road.png'), fullPage: false });
  console.log('Saved 04_redesigned_builder_road.png');

  // 5. Settings & AI Telemetry
  await page.click('text="Settings & AI"');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '05_redesigned_settings_ai.png'), fullPage: false });
  console.log('Saved 05_redesigned_settings_ai.png');

  await browser.close();
  console.log('All screenshots captured successfully in docs/screenshots/');
}

capture().catch(console.error);
