window.formatDuration = function(seconds) {
    if (!seconds) return "00:00";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

window.formatEnergy = function(wh) {
    if (!wh) return "0.00 Wh";
    return `${wh.toFixed(2)} Wh`;
};

window.formatDate = function(isoString) {
    if (!isoString) return "-";
    const date = new Date(isoString);
    return date.toLocaleString();
};
