const API_BASE = '/api';

export async function getSystemStatus() {
  const res = await fetch(`${API_BASE}/status`);
  return res.json();
}

export async function getTrafficData() {
  const res = await fetch(`${API_BASE}/traffic`);
  return res.json();
}

export async function getDecisionData() {
  const res = await fetch(`${API_BASE}/decision`);
  return res.json();
}

export async function getSignals() {
  const res = await fetch(`${API_BASE}/signals`);
  return res.json();
}

export async function getEvents(limit = 50) {
  const res = await fetch(`${API_BASE}/events?limit=${limit}`);
  return res.json();
}

export async function clearEventLog() {
  const res = await fetch(`${API_BASE}/events/clear`, { method: 'POST' });
  return res.json();
}

export async function triggerDemoScenario(scenario) {
  const res = await fetch(`${API_BASE}/demo/${scenario}`, { method: 'POST' });
  return res.json();
}

export async function uploadDemoMedia(videoFile, audioFile) {
  const formData = new FormData();
  if (videoFile) formData.append('video', videoFile);
  if (audioFile) formData.append('audio', audioFile);

  const res = await fetch(`${API_BASE}/demo/upload`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function setManualSignal(north, south, east, west) {
  const res = await fetch(`${API_BASE}/signal/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ north, south, east, west }),
  });
  return res.json();
}
