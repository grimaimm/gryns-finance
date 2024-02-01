document.addEventListener("DOMContentLoaded", function() {
  // Pie chart
  new Chart(document.getElementById("chartjs-dashboard-pie"), {
    type: "pie",
    data: {
      labels: ["Chrome", "Firefox", "IE"],
      datasets: [{
        data: [4306, 3801, 1689],
        backgroundColor: [
          window.theme.primary,
          window.theme.warning,
          window.theme.danger
        ],
        borderWidth: 5
      }]
    },
    options: {
      responsive: !window.MSInputMethodContext,
      maintainAspectRatio: false,
      legend: {
        display: false
      },
      cutoutPercentage: 75
    }
  });
});