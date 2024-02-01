// document.addEventListener("DOMContentLoaded", function() {
//   // Bar chart
//   new Chart(document.getElementById("chartjs-dashboard-bar"), {
//     type: "bar",
//     data: {
//       labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
//       datasets: [{
//         label: "This year",
//         backgroundColor: window.theme.primary,
//         borderColor: window.theme.primary,
//         hoverBackgroundColor: window.theme.primary,
//         hoverBorderColor: window.theme.primary,
//         data: [54, 67, 41, 55, 62, 45, 55, 73, 60, 76, 48, 79],
//         barPercentage: .75,
//         categoryPercentage: .5
//       }]
//     },
//     options: {
//       maintainAspectRatio: false,
//       legend: {
//         display: false
//       },
//       scales: {
//         yAxes: [{
//           gridLines: {
//             display: false
//           },
//           stacked: false,
//           ticks: {
//             stepSize: 20
//           }
//         }],
//         xAxes: [{
//           stacked: false,
//           gridLines: {
//             color: "transparent"
//           }
//         }]
//       }
//     }
//   });
// });

// document.addEventListener("DOMContentLoaded", function() {
//   // Fungsi untuk mengambil data bulanan dari server
//   function fetchMonthlyData(year) {
//       fetch(`/monthly_data/${year}`)
//           .then(response => response.json())
//           .then(monthlyData => {
//               var ctx = document.getElementById("chartjs-dashboard-bar").getContext("2d");

//               // Bar chart
//               new Chart(ctx, {
//                   type: "bar",
//                   data: {
//                       labels: monthlyData.map(item => item.month),
//                       datasets: [{
//                           label: "Pengeluaran",
//                           backgroundColor: window.theme.primary,
//                           data: monthlyData.map(item => item.total_pengeluaran)
//                       }, {
//                           label: "Pemasukan",
//                           backgroundColor: window.theme.success,
//                           data: monthlyData.map(item => item.total_pemasukan)
//                       }]
//                   },
//                   options: {
//                       maintainAspectRatio: false,
//                       legend: {
//                           display: true
//                       },
//                       scales: {
//                           xAxes: [{
//                               gridLines: {
//                                   display: false
//                               }
//                           }]
//                       }
//                   }
//               });
//           })
//           .catch(error => console.error('Error fetching monthly data:', error));
//   }

//   // Panggil fungsi fetchMonthlyData dengan tahun saat ini
//   fetchMonthlyData(new Date().getFullYear());
// });



// document.addEventListener("DOMContentLoaded", function() {
//   // Fungsi untuk mengambil data bulanan dari server
//   function fetchMonthlyData(year) {
//       fetch(`/monthly_data_bar/${year}`)
//           .then(response => response.json())
//           .then(monthlyData => {
//               var ctx = document.getElementById("chartjs-dashboard-bar").getContext("2d");

//               // Konversi angka bulan menjadi nama bulan
//               const monthNames = [
//                   "Januari", "Februari", "Maret",
//                   "April", "Mei", "Juni", "Juli",
//                   "Agustus", "September", "Oktober",
//                   "November", "Desember"
//               ];

//               // Bar chart
//               new Chart(ctx, {
//                   type: "bar",
//                   data: {
//                       labels: monthlyData.map(item => monthNames[item.month - 1]),
//                       datasets: [{
//                           label: "Pengeluaran",
//                           backgroundColor: window.theme.primary,
//                           data: monthlyData.map(item => item.total_pengeluaran)
//                       }, {
//                           label: "Pemasukan",
//                           backgroundColor: window.theme.success,
//                           data: monthlyData.map(item => item.total_pemasukan)
//                       }]
//                   },
//                   options: {
//                       maintainAspectRatio: false,
//                       legend: {
//                           display: true
//                       },
//                       scales: {
//                           xAxes: [{
//                               gridLines: {
//                                   display: false
//                               }
//                           }]
//                       }
//                   }
//               });
//           })
//           .catch(error => console.error('Error fetching monthly data:', error));
//   }

//   // Panggil fungsi fetchMonthlyData dengan tahun saat ini
//   fetchMonthlyData(new Date().getFullYear());
// });



document.addEventListener("DOMContentLoaded", function() {
    var currentYear = new Date().getFullYear();
  
    // Fungsi untuk mengambil data bulanan dari server
    function fetchMonthlyData(year) {
        fetch(`/monthly_data_line/${year}`)
            .then(response => response.json())
            .then(monthlyData => {
                var ctx = document.getElementById("chartjs-dashboard-bar").getContext("2d");
  
                // Array untuk menyimpan nama bulan
                const monthNames = [
                    "Januari", "Februari", "Maret",
                    "April", "Mei", "Juni", "Juli",
                    "Agustus", "September", "Oktober",
                    "November", "Desember"
                ];
  
                // Bar chart
                new Chart(ctx, {
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
                        scales: {
                            xAxes: [{
                                gridLines: {
                                    display: false
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true,
                                    callback: function(value, index, values) {
                                        return 'Rp' + numeral(value).format('0,0');
                                    }
                                },
                                gridLines: {
                                    display: true
                                }
                            }]
                        },
                        tooltips: {
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
                        }
                    }
                });
            })
            .catch(error => console.error('Error fetching monthly data:', error));
    }
  
    // Panggil fungsi fetchMonthlyData dengan tahun saat ini
    fetchMonthlyData(currentYear);
  });
  