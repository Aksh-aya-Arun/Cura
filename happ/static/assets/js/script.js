document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("entry-modal");
    const addButton = document.getElementById("add-entry-btn");
    const closeButton = document.querySelector(".close");
    const entryForm = document.getElementById("entry-form");
    const journalContainer = document.querySelector(".journal-entries");
    const noRecordsSection = document.getElementById("no-records-section");

    // ✅ Ensure the modal is hidden on page load
    modal.style.display = "none";  

    // ✅ Open Modal when "+" button is clicked
    addButton.addEventListener("click", function() {
        modal.style.display = "flex";
    });

    // ✅ Close Modal when clicking "X"
    closeButton.addEventListener("click", function() {
        modal.style.display = "none";
    });

    // ✅ Close Modal when clicking outside of content
    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // ✅ Handle form submission & add new entry to journal list
    entryForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevents page reload

        // Get user input
        const entryDate = document.getElementById("entry-date").value;
        const entryDetails = document.getElementById("entry-details").value;

        if (!entryDate || !entryDetails) {
            alert("Please fill out both fields.");
            return;
        }

        // ✅ Convert Date to DD/MM/YYYY format
        const dateObj = new Date(entryDate);
        const formattedDate = ('0' + dateObj.getDate()).slice(-2) + '/' +
                              ('0' + (dateObj.getMonth() + 1)).slice(-2) + '/' +
                              dateObj.getFullYear();

        // Create new entry div
        const newEntry = document.createElement("div");
        newEntry.classList.add("entry");
        newEntry.innerHTML = `
            <h3>${formattedDate}</h3>
            <p>${entryDetails}</p>
        `;

        // Append new entry to the journal container
        journalContainer.appendChild(newEntry);

        // Hide "No Records" section if it's visible
        if (noRecordsSection) {
            noRecordsSection.style.display = "none";
        }

        // Clear form fields
        entryForm.reset();

        // Close modal after adding entry
        modal.style.display = "none";
    });
});
