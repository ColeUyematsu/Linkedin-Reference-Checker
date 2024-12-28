// Collapsible functionality
// Dropdown toggle functionality
function toggleDropdown(id) {
    const dropdown = document.getElementById(id);

    // Close all dropdowns except the one clicked
    document.querySelectorAll('.dropdown-content').forEach(drop => {
        if (drop.id !== id) drop.classList.remove('active'); // Hide others
    });

    // Toggle visibility for the selected dropdown
    dropdown.classList.toggle('active');
}

// Close dropdowns if the user clicks outside
window.addEventListener('click', function (e) {
    if (!e.target.matches('.dropdown-btn')) { // Only dropdown buttons should trigger toggle
        document.querySelectorAll('.dropdown-content').forEach(dropdown => {
            dropdown.classList.remove('active'); // Close all dropdowns
        });
    }
});
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
function searchEmployees() {
    const query = document.getElementById("searchInput").value;

    fetch(`/search?q=${query}`)
        .then(response => response.json())
        .then(results => {
            const searchResults = document.getElementById("searchResults");
            searchResults.innerHTML = ""; // Clear previous results

            if (results.length === 0) {
                searchResults.innerHTML = "<li class='list-group-item'>No results found</li>";
                return;
            }

            results.forEach(employee => {
                const listItem = document.createElement("li");
                listItem.classList.add("employee");

                // Create Employee Entry
                const employeeEntry = document.createElement("div");
                employeeEntry.classList.add("employee-entry");

                // Name as Dropdown Button
                const dropdownBtn = document.createElement("div");
                dropdownBtn.classList.add("employee-name", "dropdown-btn");
                dropdownBtn.textContent = employee.name;
                dropdownBtn.onclick = function () {
                    toggleDropdown(`dropdown${employee.id}`);
                };

                // Dropdown Content
                const dropdownContent = document.createElement("div");
                dropdownContent.classList.add("dropdown-content");
                dropdownContent.id = `dropdown${employee.id}`;
                dropdownContent.innerHTML = `
                    <p>${employee.experience}</p>
                    <form method="POST" action="/delete_employee/${employee.id}" style="margin-top: 10px;">
                        <button type="submit" class="soft-danger" onclick="return confirm('Are you sure you want to delete this employee?');">
                            Delete
                        </button>
                    </form>
                `;

                // Append elements
                employeeEntry.appendChild(dropdownBtn);
                employeeEntry.appendChild(dropdownContent);
                listItem.appendChild(employeeEntry);
                searchResults.appendChild(listItem);
            });
        })
        .catch(error => console.error("Error:", error));
}

// Function to delete employee directly from search results
function deleteEmployee(employeeId, element) {
    if (confirm("Are you sure you want to delete this employee?")) {
        fetch(`/delete_employee/${employeeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url; // Handle redirects
            } else {
                element.remove(); // Remove this result from the list
                alert("Employee deleted successfully!");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Failed to delete employee.");
        });
    }
}