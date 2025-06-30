// Used for asking before exiting web
let shouldWarnOnLeave = false;
let madeChanges = false;

function enableLeaveWarning() {
    shouldWarnOnLeave = true;
}

window.addEventListener("beforeunload", function (event) {
    if (shouldWarnOnLeave && madeChanges) {
        shouldWarnOnLeave = false;
        const message = "Are you sure you want to leave this page? Unsaved changes may be lost.";
        event.returnValue = message;  // Necessary for displaying the prompt in some browsers
        return message;               // For older browsers
    }
});

function validateAndHighlightFieldsByIds(elementIds, changeMadeFromButton=false) {
    madeChanges = false;

  // Loop through each container ID in the array
  elementIds.forEach(containerId => {
    // Get the container element by its ID
    const container = document.getElementById('collapseCategory' + containerId);

    // Check if the container exists
    if (!container) {
      console.error(`Element with ID "${containerId}" does not exist.`);
      return;
    }

    // Get all input and select elements inside the container
    const elements = container.querySelectorAll('input, select');
    let allFilled = true;

    // Loop through the elements to check if they are filled
    elements.forEach(element => {
      // If the input type is 'checkbox' or 'radio', check if it's checked
      if (element.type === 'checkbox' || element.type === 'radio') {
        if (!element.checked) {
          allFilled = false;
        }
      }
      // For other types of inputs and selects, check if the value is not empty
      else if (element.value === '-' || element.value === null) {
        allFilled = false;
      }
    });

    const button = document.getElementById('button' + containerId);

    // Apply the class based on whether all fields are filled
    if (allFilled) {
      button.classList.remove('bg-warning-subtle');
      button.classList.add('bg-success-subtle');
    } else {
      button.classList.remove('bg-success-subtle');
      button.classList.add('bg-warning-subtle');
    }
  });

  // Update progress bar
    updateProgressBar();

    madeChanges = changeMadeFromButton;
}

function updateProgressBar(){
  // Update progress bar
  let assessmentForm = document.getElementById('assessment'); // create a variable called assessmentForm and assign it the form with the id of "assessment" (the form we are working with). where we can get any information stored inside the assessment form.

  let inputs = assessmentForm.querySelectorAll('select'); // “Inside the form I just got (assessmentForm), find all <select> dropdown elements.” --> This returns a NodeList (like an array) of all <select> elements inside the form — one for each metric.

  let filledCount = 0; // This is a counter. We’ll increase it for every filled <select>.
  let total = 0; // This is another counter to track how many <select> dropdowns exist in total (so we can later calculate a percentage).
  inputs.forEach(element => { // what is "forEach"? This is a JavaScript loop designed to go over every item in an array or NodeList. 
      // Check if the element is filled
      if (element.value && element.value.trim() !== '' && element.value.trim() !== '-') {  // Checks that the dropdown has some value selected and is not just a placeholder (like "-").
          filledCount++;          // If the dropdown has a value, we increase the filledCount by 1.
     }
     total++; // We increase the total count by 1 for every <select> we find, regardless of whether it’s filled or not. we need it to calculate the total percentage
  });

  let progressBar = document.getElementById('progress'); // This is the progress bar element we want to update. We’ll change its width and text to show how much of the form is filled out.
  progressBar.style.width = ((filledCount / total) * 100) +  "%"; // This calculates the percentage of filled dropdowns and sets the width of the progress bar accordingly. The width is set to a percentage value (e.g., "50%").
  progressBar.innerHTML = ((filledCount / total) * 100).toFixed(0) +  "%"; // This sets the text inside the progress bar to show the percentage of filled dropdowns. The toFixed(0) method rounds the number to 0 decimal places, so it shows a whole number (e.g., "50%").
}

function toggleVisibility(buttonId, elementId) {
    const button = document.getElementById(buttonId);
    const element = document.getElementById(elementId);

    // Toggle the hidden attribute
    if (element.hasAttribute('hidden')) {
        element.removeAttribute('hidden'); // Show the element
        button.textContent = '-'; // Change button text to -
    } else {
        element.setAttribute('hidden', 'true'); // Hide the element
        button.textContent = '+'; // Change button text to +
    }
}

function expandAllAccordions() {
  // Select all elements with class 'collapse' inside accordions
  const accordions = document.querySelectorAll('.accordion-collapse');

  accordions.forEach(accordion => {
    // Add the 'show' class to each accordion element to expand it
    accordion.classList.add('show');
  });
}

function collapseAllAccordions() {
  // Select all elements with class 'collapse' inside accordions
  const accordions = document.querySelectorAll('.accordion-collapse');

  accordions.forEach(accordion => {
    // Remove the 'show' class from each accordion element to collapse it
    accordion.classList.remove('show');
  });
}

// Function to update the remaining characters
function updateCharacterCount(fieldId, countId, maxLength) {
    const field = document.getElementById(fieldId);
    const counter = document.getElementById(countId);
    field.addEventListener('input', function() {
        const remaining = maxLength - field.value.length;
        counter.textContent = remaining + ' characters left';
    });
}

document.addEventListener("DOMContentLoaded", function (event) {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
});