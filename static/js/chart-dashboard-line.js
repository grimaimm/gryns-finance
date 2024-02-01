// document.addEventListener("DOMContentLoaded", function() {
//   var ctx = document.getElementById("chartjs-dashboard-line").getContext("2d");
//   var gradient = ctx.createLinearGradient(0, 0, 0, 225);
//   gradient.addColorStop(0, "rgba(215, 227, 244, 1)");
//   gradient.addColorStop(1, "rgba(215, 227, 244, 0)");
//   // Line chart
//   new Chart(document.getElementById("chartjs-dashboard-line"), {
//     type: "line",
//     data: {
//       labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
//       datasets: [{
//         label: "Sales ($)",
//         fill: true,
//         backgroundColor: gradient,
//         borderColor: window.theme.primary,
//         data: [
//           2115,
//           1562,
//           1584,
//           1892,
//           1587,
//           1923,
//           2566,
//           2448,
//           2805,
//           3438,
//           2917,
//           3327
//         ]
//       }]
//     },
//     options: {
//       maintainAspectRatio: false,
//       legend: {
//         display: false
//       },
//       tooltips: {
//         intersect: false
//       },
//       hover: {
//         intersect: true
//       },
//       plugins: {
//         filler: {
//           propagate: false
//         }
//       },
//       scales: {
//         xAxes: [{
//           reverse: true,
//           gridLines: {
//             color: "rgba(0,0,0,0.0)"
//           }
//         }],
//         yAxes: [{
//           ticks: {
//             stepSize: 1000
//           },
//           display: true,
//           borderDash: [3, 3],
//           gridLines: {
//             color: "rgba(0,0,0,0.0)"
//           }
//         }]
//       }
//     }
//   });
// });
document.addEventListener("DOMContentLoaded", function() {
  var currentYear = new Date().getFullYear();

  // Fungsi untuk mengambil data bulanan dari server
  function fetchMonthlyData(year) {
      fetch(`/monthly_data_line/${year}`)
          .then(response => response.json())
          .then(monthlyData => {
              var ctx = document.getElementById("chartjs-dashboard-line").getContext("2d");
              var gradient = ctx.createLinearGradient(0, 0, 0, 225);
              gradient.addColorStop(0, "rgba(215, 227, 244, 1)");
              gradient.addColorStop(1, "rgba(215, 227, 244, 0)");

              // Array untuk menyimpan nama bulan
              const monthNames = [
                  "Januari", "Februari", "Maret",
                  "April", "Mei", "Juni", "Juli",
                  "Agustus", "September", "Oktober",
                  "November", "Desember"
              ];

              // Line chart
              new Chart(ctx, {
                  type: "line",
                  data: {
                      labels: monthlyData.map(item => monthNames[item.month - 1]),
                      datasets: [{
                          label: "Pengeluaran",
                          fill: true,
                          backgroundColor: gradient,
                          borderColor: window.theme.primary,
                          data: monthlyData.map(item => item.total_pengeluaran)
                      }, {
                          label: "Pemasukan",
                          fill: true,
                          backgroundColor: gradient,
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
          })
          .catch(error => console.error('Error fetching monthly data:', error));
  }

  // Panggil fungsi fetchMonthlyData dengan tahun saat ini
  fetchMonthlyData(currentYear);
});
