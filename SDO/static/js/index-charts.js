window.chartColors = {
    green: '#75c181',
    gray: '#a9b5c9',
    text: '#252930',
    border: '#e7e9ed'
};

function fetchBillData() {
    return fetch('/bills_data/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }
            return response.json();
        })
        .then(data => data)
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function createLineChart(data) {
    var ctx = document.getElementById('canvas-linechart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Total Bills',
                    fill: false,
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
                    data: data.total_bills,
                },
                {
                    label: 'Paid Bills',
                    borderDash: [3, 5],
                    backgroundColor: window.chartColors.gray,
                    borderColor: window.chartColors.gray,
                    data: data.paid_bills,
                    fill: false,
                }
            ]
        }
    });
}

function createBarChart(data) {
    var ctx = document.getElementById('canvas-barchart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Bills',
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
                    data: [data.total_bills, data.paid_bills],
                }
            ]
        }
    });
}

window.addEventListener('load', function() {
    fetchBillData().then(data => {
        createLineChart(data);
        createBarChart(data);
    });
});
