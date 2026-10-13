"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { calculateFlipi } = require("./flipi.js");

const base = { age: 60, stage: 2, hemoglobin: 12, ldhRatio: 1, nodalSites: 4 };
const calc = changes => calculateFlipi({ ...base, ...changes });

test("the five original cutoffs are strict and independent", () => {
  assert.equal(calc({}).score, 0);
  assert.equal(calc({ age: 61 }).score, 1);
  assert.equal(calc({ age: 60 }).score, 0);
  assert.equal(calc({ stage: 3 }).score, 1);
  assert.equal(calc({ stage: 4 }).score, 1);
  assert.equal(calc({ stage: 2 }).score, 0);
  assert.equal(calc({ hemoglobin: 11.99 }).score, 1);
  assert.equal(calc({ hemoglobin: 12 }).score, 0);
  assert.equal(calc({ ldhRatio: 1.0001 }).score, 1);
  assert.equal(calc({ ldhRatio: 1 }).score, 0);
  assert.equal(calc({ nodalSites: 5 }).score, 1);
  assert.equal(calc({ nodalSites: 4 }).score, 0);
});

test("risk groups and historical overall survival", () => {
  assert.deepEqual(calc({}).survival, { fiveYear: 91, tenYear: 71 });
  const intermediate = calc({ age: 61, stage: 3 });
  assert.equal(intermediate.score, 2);
  assert.equal(intermediate.riskGroup, "Intermediate");
  assert.deepEqual(intermediate.survival, { fiveYear: 78, tenYear: 51 });
  const high = calc({ age: 61, stage: 4, hemoglobin: 10, ldhRatio: 2, nodalSites: 8 });
  assert.equal(high.score, 5);
  assert.equal(high.riskGroup, "High");
  assert.deepEqual(high.survival, { fiveYear: 53, tenYear: 36 });
});

test("reject invalid stages, negative, missing, non-integers and nonfinite inputs", () => {
  for (const changes of [
    { stage: 0 }, { stage: 5 }, { stage: 1.5 },
    { age: -1 }, { age: 60.5 }, { age: true }, { age: undefined },
    { hemoglobin: -1 }, { hemoglobin: NaN }, { hemoglobin: Infinity },
    { ldhRatio: -0.01 }, { ldhRatio: Infinity }, { ldhRatio: null },
    { nodalSites: -1 }, { nodalSites: 4.5 }
  ]) {
    assert.throws(() => calc(changes), RangeError);
  }
});

test("browser assets use relative paths and no simulated clinical output", () => {
  const page = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
  const entry = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  assert.match(page, /src="\.\/flipi\.js"/);
  assert.match(page, /id="flipi-form"/);
  assert.match(page, /id="result"/);
  assert.doesNotMatch(page, /\/api\/audit|DOSSIER-SIM|HMAC_SHA256_/);
  assert.match(entry, /\.\/web\//);
});
