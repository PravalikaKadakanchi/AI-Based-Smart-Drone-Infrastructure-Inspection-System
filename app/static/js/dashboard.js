document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("runInspectionBtn");
  const statusText = document.getElementById("statusText");

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    statusText.textContent = "Running inspection...";

    try {
      const res = await fetch("/api/inspect", { method: "POST" });
      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();
      renderResult(data);
      statusText.textContent = `Last inspection: ${data.inspection_id}`;
    } catch (err) {
      statusText.textContent = `Error: ${err.message}`;
    } finally {
      btn.disabled = false;
    }
  });

  function renderResult(data) {
    document.getElementById("capturedImage").src = data.annotated_image_base64;

    document.getElementById("tLat").textContent = data.gps.lat.toFixed(6);
    document.getElementById("tLon").textContent = data.gps.lon.toFixed(6);
    document.getElementById("tAlt").textContent = `${data.gps.alt_m} m`;
    document.getElementById("tBattery").textContent = `${data.battery_percent}%`;
    document.getElementById("tMode").textContent = data.flight_mode;

    document.getElementById("cDetected").textContent = data.crack_detected ? "Yes" : "No";
    document.getElementById("cCount").textContent = data.crack_count;
    document.getElementById("cCoverage").textContent = `${data.coverage_percent}%`;

    const badge = document.getElementById("severityBadge");
    badge.textContent = `${data.severity.zone} ZONE — ${data.severity.label}`;
    badge.style.background = data.severity.color;
    badge.style.color = "#101010";

    document.getElementById("recommendationText").textContent =
      `${data.severity.recommendation} Action window: ${data.severity.action_window}.`;

    const reportStatus = document.getElementById("reportStatus");
    const reportLink = document.getElementById("reportLink");
    if (data.report_generated) {
      reportStatus.textContent = data.email_sent
        ? "Report generated and emailed successfully."
        : "Report generated (email not sent — SMTP not configured).";
      reportLink.href = `/reports/${data.inspection_id}.pdf`;
      reportLink.style.display = "inline-block";
    } else {
      reportStatus.textContent = "Report generation failed.";
      reportLink.style.display = "none";
    }
  }
});
