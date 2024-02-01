document.addEventListener("DOMContentLoaded", function() {
  // Get the elements you want to manipulate
  const editProfileButton = document.querySelector('.button-1');
  const formElements = document.querySelectorAll('.card-body input');
  const buttonGroup = document.querySelector('.button-grp');

  // Disable the form elements initially
  formElements.forEach(element => {
    element.setAttribute('disabled', 'true');
  });

  // Hide the button group initially
  buttonGroup.style.display = 'none';

  // Add click event listener to the "Edit Profile" button
  editProfileButton.addEventListener('click', function() {
    // Enable the form elements
    formElements.forEach(element => {
      element.removeAttribute('disabled');
    });

    // Show the button group
    buttonGroup.style.display = 'block'; // Assuming your button group is a flex container
  });
});