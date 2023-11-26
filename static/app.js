async function searchItems() {
    const query = document.getElementById("search-query").value;
    const response = await fetch("/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query }),
    });

    if (response.ok) {
        const data = await response.json();
        displayResults(data);
    } else {
        alert("Error: " + await response.text());
    }
}

function displayResults(data) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    if (data.length === 0) {
        resultsDiv.innerHTML = "<p>No results found.</p>";
        return;
    }

    const table = document.createElement("table");
    const headerRow = document.createElement("tr");

    const nameHeader = document.createElement("th");
    nameHeader.textContent = "Name";
    headerRow.appendChild(nameHeader);

    const imageHeader = document.createElement("th");
    imageHeader.textContent = "Image";
    headerRow.appendChild(imageHeader);

    table.appendChild(headerRow);

    for (const item of data) {
        const row = document.createElement("tr");
        row.addEventListener("click", () => fetchItemData(item.asin));

        const nameCell = document.createElement("td");
        nameCell.textContent = item.title;
        row.appendChild(nameCell);

        const imageCell = document.createElement("td");
        const image = document.createElement("img");
        image.src = item.image_url;
        image.width = 64;
        image.height = 64;
        imageCell.appendChild(image);
        row.appendChild(imageCell);

        table.appendChild(row);
    }

    resultsDiv.appendChild(table);
}

async function fetchItemData(asin) {
    document.getElementById("loader").style.display = "block"; // Show the loader when fetching item details

    const response = await fetch(`/item/${asin}`);
    if (response.ok) {
        const data = await response.json();
        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";

        const table = document.createElement("table");
        const headerRow = document.createElement("tr");

        ["Item", "Rating", "Amazon.com", "Amazon.co.uk", "Amazon.de", "Amazon.ca"].forEach((title) => {
            const th = document.createElement("th");
            th.textContent = title;
            headerRow.appendChild(th);
        });

        table.appendChild(headerRow);

        const row = document.createElement("tr");

        const itemName = data["Amazon.com"]?.Item || "N/A";
        const itemRating = data["Amazon.com"]?.Rating || "N/A";

        const rowData = [itemName, itemRating];

        rowData.forEach((value) => {
            const td = document.createElement("td");
            td.textContent = value;
            row.appendChild(td);
        });

        ["Amazon.com", "Amazon.co.uk", "Amazon.de", "Amazon.ca"].forEach((site) => {
            const td = document.createElement("td");
            if (data[site]?.Price) {
                const link = document.createElement("a");
                link.href = data[site]?.url;
                link.target = "_blank";
                link.textContent = data[site]?.Price;
                td.appendChild(link);
            } else {
                td.textContent = "N/A";
            }
            row.appendChild(td);
        });

        table.appendChild(row);
        resultsDiv.appendChild(table);
        
    } else {
        alert("Error: " + await response.text());
    }

    document.getElementById("loader").style.display = "none"; // Hide the loader when the data is loaded
}

// Add this function to your app.js file
async function showPastSearches() {
    const response = await fetch("/past-searches");
    const data = await response.json();
  
    const table = document.createElement("table");
    table.setAttribute("class", "search-history-table");
  
    const header = table.createTHead();
    const headerRow = header.insertRow(0);
    ["Num", "Query", "Time", "Item Name", "Amazon.com", "Amazon.co.uk", "Amazon.de", "Amazon.ca"].forEach((title, index) => {
      const cell = headerRow.insertCell(index);
      cell.innerHTML = title;
    });
  
    const body = table.createTBody();
    data.forEach(rowData => {
      const row = body.insertRow();
      rowData.forEach((value, index) => {
        const cell = row.insertCell(index);
        cell.innerHTML = value || "N/A";
      });
    });
  
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";
    resultsDiv.appendChild(table);
  }
  
  // Add this event listener at the end of your app.js file
  document.getElementById("past-searches-link").addEventListener("click", (e) => {
    e.preventDefault();
    showPastSearches();
  });
  
