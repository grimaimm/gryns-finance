$(document).ready(function() {
  // Disable submit button initially
  $("form#myForm button[type='submit']").prop("disabled", true);

  // Enable submit button when all form fields are filled
  $("form#myForm input, form#myForm select").on("change keyup", function() {
      var formFilled = true;

      // Check if all input and select fields have values
      $("form#myForm input, form#myForm select").each(function() {
          if ($(this).val() === "" || $(this).val() === null) {
              formFilled = false;
              return false;  // Break out of the loop if any field is empty
          }
      });

      // Enable or disable the submit button based on formFilled
      $("form#myForm button[type='submit']").prop("disabled", !formFilled);
  });
});