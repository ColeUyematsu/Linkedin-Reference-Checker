// Collapsible functionality
var coll = document.getElementsByClassName("collapsible");
for (var i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        content.style.display = (content.style.display === "block") ? "none" : "block";
    });
}

// Add new input field with consistent "Delete" button styling
function addInput() {
    // Container for input and delete button
    var container = document.getElementById("url-container");
    var inputDiv = document.createElement("div");
    inputDiv.classList.add("url-input"); // Use 'url-input' for consistent spacing and layout

    // Create input field
    var input = document.createElement("input");
    input.type = "text";
    input.name = "linkedin_urls";
    input.placeholder = "Employee LinkedIn URL";
    input.required = true;

    // Create "Delete" button
    var deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.classList.add("soft-danger"); // Ensure consistent red style
    deleteButton.innerHTML = "Delete";
    deleteButton.onclick = function () {
        removeInput(this);
    };

    // Append input and button to the container
    inputDiv.appendChild(input);
    inputDiv.appendChild(deleteButton);
    container.appendChild(inputDiv);
}

// Remove the input field when "Delete" is clicked
function removeInput(element) {
    var inputDiv = element.parentNode;
    inputDiv.remove();
}