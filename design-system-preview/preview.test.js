const test = require('node:test');
const assert = require('node:assert/strict');

const {
  nextTheme,
  nextAgentState,
  detectSecret,
  toggleSelection,
} = require('./preview.js');

test('theme toggle always alternates between dark and light', () => {
  assert.equal(nextTheme('dark'), 'light');
  assert.equal(nextTheme('light'), 'dark');
  assert.equal(nextTheme('unexpected'), 'dark');
});

test('agent demo advances through the declared state sequence and wraps', () => {
  assert.deepEqual(nextAgentState('idle'), {
    key: 'retrieving',
    label: 'در حال بررسی منابع رسمی',
  });
  assert.deepEqual(nextAgentState('complete'), {
    key: 'idle',
    label: 'آماده',
  });
});

test('secret detection warns for tokens but ignores ordinary technical text', () => {
  assert.equal(detectSecret('LIARA_API_TOKEN=liara_1234567890abcdef'), true);
  assert.equal(detectSecret('چطور متغیر محیطی را تنظیم کنم؟'), false);
});

test('citation selection closes when the active source is selected again', () => {
  assert.equal(toggleSelection(null, 'source-1'), 'source-1');
  assert.equal(toggleSelection('source-1', 'source-1'), null);
  assert.equal(toggleSelection('source-1', 'source-2'), 'source-2');
});
