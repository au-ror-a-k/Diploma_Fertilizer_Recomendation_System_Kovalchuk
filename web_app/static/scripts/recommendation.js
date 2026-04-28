function showToast(message, type = 'error') {
    const colors = { error: '#c0392b', success: '#27ae60', warning: '#d4a017' };
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function downloadCSV() {
    const element = document.getElementById('metadata');
    if (!element) {
        showToast("There are no data for downloading");
        return;
    }

    let data;
    try {
        data = JSON.parse(element.dataset.recommendation);
    } catch {
        showToast("Error in recommendation reading");
        return;
    }

    if (!data || data.length === 0) {
        showToast("No data for downloading", "warning");
        return;
    }

    var csv = 'Zone Name,Elements to address,Potential yield increase,Fertilizer,Amount (kg/ha)\n';

    data.forEach(zone => {
        if (zone.best && zone.best.length > 0) {
            zone.best.forEach(fert => {
                csv += [
                    zone.zone_name,
                    zone.elements,
                    zone.percentage_increase,
                    fert.fertilizer,
                    fert.amount
                ].join(",") + "\n";
            });
        } else {
            csv += [zone.zone_name, "—", "—", "No changes needed", ""].join(",") + "\n";
        }
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Fertilizer_recommendation.csv';
    a.click();
    URL.revokeObjectURL(url);

    showToast("CSV file downloaded", "success");
}

const return_button = document.getElementById("return_nutton");
if (return_button) {
    return_button.addEventListener('click', function () {
        window.location.href = "/diploma/fertilizer_recommendation/your_fields_page";
    });
}