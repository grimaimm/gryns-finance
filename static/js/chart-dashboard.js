document.addEventListener("DOMContentLoaded", function() {
  var currentYear = new Date().getFullYear();
  
  const monthNames = [
    "Januari", "Februari", "Maret",
    "April", "Mei", "Juni", "Juli",
    "Agustus", "September", "Oktober",
    "November", "Desember"
];

  function fetchMonthlyData(year) {
    fetch(`/monthly_data/${year}`)
      .then(response => response.json())
      .then(monthlyData => {
        // Line chart
        var lineCtx = document.getElementById("chartjs-dashboard-line").getContext("2d");
        var gradientLine = lineCtx.createLinearGradient(0, 0, 0, 225);
        gradientLine.addColorStop(0, "rgba(215, 227, 244, 1)");
        gradientLine.addColorStop(1, "rgba(215, 227, 244, 0)");

        new Chart(lineCtx, {
          type: "line",
          data: {
            labels: monthlyData.map(item => monthNames[item.month - 1]),
            datasets: [{
              label: "Pengeluaran",
              fill: true,
              backgroundColor: gradientLine,
              borderColor: window.theme.primary,
              data: monthlyData.map(item => item.total_pengeluaran)
            }, {
              label: "Pemasukan",
              fill: true,
              backgroundColor: gradientLine,
              borderColor: window.theme.success,
              data: monthlyData.map(item => item.total_pemasukan)
            }]
          },
          options: {
            maintainAspectRatio: false,
            legend: {
              display: true
            },
            tooltips: {
              intersect: false,
              callbacks: {
                label: function(tooltipItem, data) {
                  var label = data.datasets[tooltipItem.datasetIndex].label || '';

                  if (label) {
                    label += ': ';
                  }

                  label += 'Rp' + numeral(tooltipItem.yLabel).format('0,0');

                  return label;
                }
              }
            },
            hover: {
              intersect: true
            },
            plugins: {
              filler: {
                propagate: false
              }
            },
            scales: {
              xAxes: [{
                gridLines: {
                  color: "rgba(0,0,0,0.1)"
                }
              }]
            }
          }
        });

        // Bar chart
        var barCtx = document.getElementById("chartjs-dashboard-bar").getContext("2d");
        var gradientBar = barCtx.createLinearGradient(0, 0, 0, 225);
        gradientBar.addColorStop(0, "rgba(215, 227, 244, 1)");
        gradientBar.addColorStop(1, "rgba(215, 227, 244, 0)");

        new Chart(barCtx, {
          type: "bar",
          data: {
            labels: monthlyData.map(item => monthNames[item.month - 1]),
            datasets: [{
              label: "Pengeluaran",
              backgroundColor: window.theme.primary,
              data: monthlyData.map(item => item.total_pengeluaran)
            }, {
              label: "Pemasukan",
              backgroundColor: window.theme.success,
              data: monthlyData.map(item => item.total_pemasukan)
            }]
          },
          options: {
            maintainAspectRatio: false,
            legend: {
              display: true
            },
            tooltips: {
              intersect: false,
              callbacks: {
                label: function(tooltipItem, data) {
                  var label = data.datasets[tooltipItem.datasetIndex].label || '';

                  if (label) {
                    label += ': ';
                  }

                  label += 'Rp' + numeral(tooltipItem.yLabel).format('0,0');

                  return label;
                }
              }
            },
            scales: {
              xAxes: [{
                gridLines: {
                  display: false
                }
              }]
            }
          }
        });
      })
      .catch(error => console.error('Error fetching monthly data:', error));
  }

  // Panggil fungsi fetchMonthlyData dengan tahun saat ini
  fetchMonthlyData(currentYear);
});
