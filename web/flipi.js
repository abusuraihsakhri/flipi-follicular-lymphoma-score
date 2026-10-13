/* Classical FLIPI (Solal-Céligny et al., Blood 2004;104:1258–1265).
   Zero-dependency calculation shared by the GitHub Pages UI and Node tests. */
(function (root) {
  "use strict";

  const HISTORICAL_SURVIVAL = Object.freeze({
    Low: Object.freeze({ fiveYear: 91, tenYear: 71 }),
    Intermediate: Object.freeze({ fiveYear: 78, tenYear: 51 }),
    High: Object.freeze({ fiveYear: 53, tenYear: 36 })
  });

  function integer(name, value, min, max) {
    if (!Number.isInteger(value) || value < min || (max !== undefined && value > max)) {
      throw new RangeError(name + " must be an integer" +
        (max === undefined ? " ≥ " + min : " between " + min + " and " + max) + ".");
    }
  }

  function nonNegativeFinite(name, value) {
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
      throw new RangeError(name + " must be a finite non-negative number.");
    }
  }

  function calculateFlipi({ age, stage, hemoglobin, ldhRatio, nodalSites }) {
    integer("Age", age, 0);
    integer("Ann Arbor stage", stage, 1, 4);
    integer("Involved nodal areas", nodalSites, 0);
    nonNegativeFinite("Hemoglobin", hemoglobin);
    nonNegativeFinite("LDH/ULN ratio", ldhRatio);

    const factors = [
      { label: "Age > 60 years", positive: age > 60 },
      { label: "Ann Arbor stage III–IV", positive: stage >= 3 },
      { label: "Hemoglobin < 12 g/dL", positive: hemoglobin < 12 },
      { label: "LDH > laboratory ULN", positive: ldhRatio > 1 },
      { label: "More than 4 involved nodal areas", positive: nodalSites > 4 }
    ];
    const score = factors.filter(factor => factor.positive).length;
    const riskGroup = score <= 1 ? "Low" : score === 2 ? "Intermediate" : "High";
    return { score, riskGroup, factors, survival: HISTORICAL_SURVIVAL[riskGroup] };
  }

  const api = Object.freeze({ calculateFlipi, HISTORICAL_SURVIVAL });
  root.FLIPI = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;

  if (typeof document === "undefined") return;

  function initialize() {
    const form = document.getElementById("flipi-form");
    if (!form) return;
    const result = document.getElementById("result");
    const error = document.getElementById("error");
    const download = document.getElementById("download");
    let lastSummary = "";

    function field(id, integerField) {
      const element = document.getElementById(id);
      const raw = element.value.trim();
      if (raw === "") throw new RangeError("All five inputs are required.");
      const value = Number(raw);
      if (!Number.isFinite(value) || (integerField && !Number.isInteger(value))) {
        throw new RangeError("Please enter valid, finite numeric values.");
      }
      return value;
    }

    function display(data) {
      document.getElementById("score").textContent = data.score + " / 5";
      document.getElementById("risk").textContent = data.riskGroup + " risk";
      document.getElementById("survival-5").textContent = data.survival.fiveYear + "%";
      document.getElementById("survival-10").textContent = data.survival.tenYear + "%";
      const list = document.getElementById("factors");
      list.replaceChildren();
      data.factors.forEach(factor => {
        const item = document.createElement("li");
        const label = document.createElement("span");
        const points = document.createElement("strong");
        label.textContent = factor.label;
        points.textContent = factor.positive ? "+1" : "0";
        points.className = factor.positive ? "positive" : "neutral";
        item.append(label, points);
        list.append(item);
      });
      lastSummary = [
        "Classical FLIPI — Follicular Lymphoma International Prognostic Index",
        "Score: " + data.score + "/5 | Risk group: " + data.riskGroup,
        ...data.factors.map(factor => (factor.positive ? "1" : "0") + " — " + factor.label),
        "Historical original-cohort 5-year overall survival: " + data.survival.fiveYear + "%",
        "Historical original-cohort 10-year overall survival: " + data.survival.tenYear + "%",
        "These historical group-level estimates are not individual predictions.",
        "FLIPI does not determine treatment need or choice.",
        "Solal-Céligny et al. Blood 2004;104:1258–1265. doi:10.1182/blood-2003-12-4434."
      ].join("\n");
      download.disabled = false;
      result.hidden = false;
    }

    form.addEventListener("submit", event => {
      event.preventDefault();
      error.hidden = true;
      result.hidden = true;
      download.disabled = true;
      lastSummary = "";
      try {
        display(calculateFlipi({
          age: field("age", true),
          stage: field("stage", true),
          hemoglobin: field("hemoglobin", false),
          ldhRatio: field("ldh-ratio", false),
          nodalSites: field("nodal-sites", true)
        }));
      } catch (err) {
        error.textContent = err.message;
        error.hidden = false;
      }
    });

    form.addEventListener("reset", () => {
      error.hidden = true;
      result.hidden = true;
      lastSummary = "";
      download.disabled = true;
    });

    download.addEventListener("click", () => {
      if (!lastSummary) return;
      const url = URL.createObjectURL(new Blob([lastSummary + "\n"], { type: "text/plain;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = "flipi-summary.txt";
      link.click();
      URL.revokeObjectURL(url);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
