const detectionList = document.getElementById('detection_list');
const updateTime = document.getElementById('last_update_time');
const ctx = document.getElementById('detectionChart').getContext('2d');

let detectionData = {
    labels: ['產品 A', '瑕疵品 B'],
    counts: [0, 0]
};

const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: detectionData.labels,
        datasets: [{
            label: '數量',
            data: detectionData.counts,
            backgroundColor: ['rgba(54, 162, 235, 0.5)', 'rgba(255, 99, 132, 0.5)'],
            borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            if (Object.keys(data).length > 0) {
                updateTime.textContent = `更新時間：${new Date(data.timestamp * 1000).toLocaleTimeString()}`;
                
                let htmlContent = '';
                let productCount = 0;
                let defectCount = 0;

                data.detections.forEach(det => {
                    htmlContent += `<div>${det.class} (信心分數: ${det.confidence.toFixed(2)})</div>`;
                    if (det.class === 'product_A') {
                        productCount++;
                    } else if (det.class === 'defect_B') {
                        defectCount++;
                    }
                });

                detectionList.innerHTML = htmlContent;

                detectionData.counts[0] = productCount;
                detectionData.counts[1] = defectCount;
                chart.update();
            }
        });
}

// 每秒刷新一次數據
setInterval(fetchData, 1000);