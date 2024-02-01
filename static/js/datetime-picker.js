// document.addEventListener("DOMContentLoaded", function() {
//   var date = new Date(Date.now() - 5 * 24 * 60 * 60 * 1000);
//   var defaultDate = date.getUTCFullYear() + "-" + (date.getUTCMonth() + 1) + "-" + date.getUTCDate();
//   document.getElementById("datetimepicker-dashboard").flatpickr({
//     inline: true,
//     prevArrow: "<span title=\"Previous month\">&laquo;</span>",
//     nextArrow: "<span title=\"Next month\">&raquo;</span>",
//     defaultDate: defaultDate
//   });
// });

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("datetimepicker-dashboard").flatpickr({
    inline: true,
    prevArrow: "<span title=\"Previous month\">&laquo;</span>",
    nextArrow: "<span title=\"Next month\">&raquo;</span>",
    defaultDate: "today"  // Set default date to today
  });
});