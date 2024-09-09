var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}

function addInput() {
    var container = document.getElementById("url-container");
    var inputDiv = document.createElement("div");
    inputDiv.classList.add("url-input");

    var input = document.createElement("input");
    input.type = "text";
    input.name = "linkedin_urls";
    input.placeholder = "Employee LinkedIn URL";
    input.required = true;

    var deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.classList.add("delete-url");
    deleteButton.innerHTML = "Delete";
    deleteButton.onclick = function() {
        removeInput(this);
    };

    inputDiv.appendChild(input);
    inputDiv.appendChild(deleteButton);
    container.appendChild(inputDiv);
}

function removeInput(element) {
    var inputDiv = element.parentNode;
    inputDiv.remove();
}

function addInput() {
  var container = document.getElementById("url-container");
  var inputDiv = document.createElement("div");
  inputDiv.classList.add("url-input");

  var input = document.createElement("input");
  input.type = "text";
  input.name = "linkedin_urls";
  input.placeholder = "Employee LinkedIn URL";
  input.required = true;

  var deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.classList.add("delete-url");
  deleteButton.innerHTML = "Delete";
  deleteButton.onclick = function() {
      removeInput(this);
  };

  inputDiv.appendChild(input);
  inputDiv.appendChild(deleteButton);
  container.appendChild(inputDiv);
}

function removeInput(element) {
  var inputDiv = element.parentNode;
  inputDiv.remove();
}