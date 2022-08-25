const GRAPH_WIDTH = 380;
const GRAPH_HEIGHT = 380;


function openFilterSettings() {
  document.getElementById("filterSettings").style.width = "250px";
  document.getElementById("content").style.marginLeft = "250px";
}

function closeFilterSettings() {
  document.getElementById("filterSettings").style.width = "0";
  document.getElementById("content").style.marginLeft = "0";
}


var data = JSON.parse(document.getElementById("data").textContent);

var visibleData = [];
for (let data_dao of data) {
  visibleData.push(data_dao["name"]);
}


function createFilterSettings() {
  var checkboxesDivElement = document.getElementById("filterCheckboxes");
  for (let data_dao of data) {
    let filterCheckbox = document.createElement("input");
    filterCheckbox.type = "checkbox";
    filterCheckbox.id = "checkbox_" + data_dao["name"];
    filterCheckbox.name = data_dao["name"];
    filterCheckbox.value = data_dao["name"];
    if (visibleData.includes(data_dao["name"])) {
      filterCheckbox.checked = true;
    } else {
      filterCheckbox.checked = false;
    }
    filterCheckbox.addEventListener("click", function() {
      if (visibleData.includes(this.value)) {
        visibleData = visibleData.filter(val => val !== this.value);
      } else {
        visibleData.push(this.value);
      }
      drawGraphs();
    });

    let filterCheckboxLabel = document.createElement("label");
    filterCheckboxLabel.htmlFor = "checkbox_" + data_dao["name"];
    filterCheckboxLabel.appendChild(document.createTextNode(data_dao["name"]));

    checkboxesDivElement.appendChild(filterCheckbox);
    checkboxesDivElement.appendChild(filterCheckboxLabel);
    checkboxesDivElement.appendChild(document.createElement("br"));
    checkboxesDivElement.appendChild(document.createElement("br"));
  }
}

window.onload=createFilterSettings();


function toggleDropdown() {
  document.getElementById("sortDropdownContent").classList.toggle("show");
}

window.onclick = function(event) {
  if (!event.target.matches(".sortButton")) {
    var dropdowns = document.getElementsByClassName("sortDropdownContent");
    for (let k = 0; k < dropdowns.length; k++) {
      if (dropdowns[k].classList.contains("show")) {
        dropdowns[k].classList.remove("show");
      }
    }
  }
}


function sortAlphabetically(reverse) {
  let names = [];
  for (let data_dao of data) {
    names.push(data_dao["name"]);
  }

  if (reverse) {
    names = names.sort().reverse();
  } else {
    names.sort();
  }

  let dataSorted = []
  while (names.length > 0) {
    let next_name = names.shift();
    for (let data_dao of data) {
      if (data_dao["name"] === next_name) {
        dataSorted.push(data_dao);
        break;
      }
    }
  }

  data = [];
  for (let data_dao of dataSorted) {
    data.push(data_dao);
  }
}

function sortVotingRate(increasing) {
  let dataSorted = []
  while (data.length > 0) {
    let vr = data[0]["average_voting_rate_all_time"];
    let vr_index = 0;
    for (let k = 0; k < data.length; k++) {
      if (increasing && data[k]["average_voting_rate_all_time"] < vr) {
        vr = data[k]["average_voting_rate_all_time"];
        vr_index = k;
      } else if (!increasing && data[k]["average_voting_rate_all_time"] > vr) {
        vr = data[k]["average_voting_rate_all_time"];
        vr_index = k;
      }
    }
    dataSorted.push(data[vr_index]);
    data.splice(vr_index, 1);
  }

  data = [];
  for (let data_dao of dataSorted) {
    data.push(data_dao);
  }
}

function sortAZ() {
  sortAlphabetically(false);
  drawGraphs();
}

function sortZA() {
  sortAlphabetically(true);
  drawGraphs();
}

function sortIncreasingVotingRate() {
  sortVotingRate(true);
  drawGraphs();
}

function sortDecreasingVotingRate() {
  sortVotingRate(false);
  drawGraphs();
}


function drawGraphs() {
  var data_avr_all_time = [["Name", "Average voting rate", {role: "style"}]];
  var data_inverse_gini_all_time = [["Name", "Average Gini coefficient", {role: "style"}]];
  var data_avr_over_time = [["Time (in days)", "30", "60", "90", "120", "150"]];
  var data_inverse_gini_over_time = [["Time (in days)", "30", "60", "90", "120", "150"]];
  var data_price_over_time = [["Time (in days)", "30", "60", "90", "120", "150"]];
  var data_volume_over_time = [["Time (in days)", "30", "60", "90", "120", "150"]];
  var data_components = [["nf1", "nf2", {role: "annotation"}]];

  for (let data_dao of data) {
    if (visibleData.includes(data_dao["name"]) == false) {
      continue;
    }

    if (data_dao["name"] !== "Compound") {
      data_avr_all_time.push([data_dao["name"], data_dao["average_voting_rate_all_time"], "blue"]);
    } else {
      data_avr_all_time.push([data_dao["name"], data_dao["average_voting_rate_all_time"], "red"]);
    }
    if (data_dao["name"] !== "Compound") {
      data_inverse_gini_all_time.push([data_dao["name"], data_dao["average_inverse_gini_all_time"], "blue"]);
    } else {
      data_inverse_gini_all_time.push([data_dao["name"], data_dao["average_inverse_gini_all_time"], "red"]);
    }

    data_avr_over_time_dao = [data_dao["name"]];
    data_inverse_gini_over_time_dao = [data_dao["name"]];
    data_price_over_time_dao = [data_dao["name"]];
    data_volume_over_time_dao = [data_dao["name"]];

    // We use the same number of periods for each of graphs
    let num_periods = data_dao["average_voting_rates"].length

    for (let i = 0; i < num_periods; i++) {
      data_avr_over_time_dao.push(data_dao["average_voting_rates"][i]);
      data_inverse_gini_over_time_dao.push(data_dao["average_inverse_ginis"][i]);
      if (i < data_dao["average_prices"].length) {
        data_price_over_time_dao.push(data_dao["average_prices"][i]);
      }
      if (i < data_dao["average_volumes"].length) {
        data_volume_over_time_dao.push(data_dao["average_volumes"][i]);
      }
    }
    data_avr_over_time.push(data_avr_over_time_dao);
    data_inverse_gini_over_time.push(data_inverse_gini_over_time_dao);

    // Not all DAOs have available market data
    if (data_price_over_time_dao.length - 1 == num_periods) {
      data_price_over_time.push(data_price_over_time_dao);
    }
    if (data_volume_over_time_dao.length - 1 == num_periods) {
      data_volume_over_time.push(data_volume_over_time_dao);
    }
    if (data_dao["components"].length == 2) {
      let components = []
      for (let j = 0; j < 2; j++) {
        components.push(data_dao["components"][j])
      }
      components.push(data_dao["name"])
      data_components.push(components);
    }
  }

  new google.visualization.BarChart(
    document.getElementById("chart_div_avr_all_time")
  ).draw(
    google.visualization.arrayToDataTable(data_avr_all_time),
    {
      title: "Average Voting Rates (All-Time)",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "Average voting rate (%)",
        minValue: 0,
        scaleType: 'log',
      },
      legend: { position: "none" },
    }
  );

  // Transpose data
  // https://stackoverflow.com/questions/17428587/transposing-a-2d-array-in-javascript
  data_avr_over_time = data_avr_over_time[0].map((col, i) =>
    data_avr_over_time.map((row) => row[i])
  );

  new google.visualization.LineChart(
    document.getElementById("chart_div_avr_over_time")
  ).draw(
    google.visualization.arrayToDataTable(data_avr_over_time),
    {
      title: "Voting Rate Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "Time (in days)",
        minValue: 0,
      },
      vAxis: {
        title: "Average voting rate (%)",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
      curveType: "function",
    }
  );

  new google.visualization.BarChart(
    document.getElementById("chart_div_inverse_gini_all_time")
  ).draw(
    google.visualization.arrayToDataTable(data_inverse_gini_all_time),
    {
      title: "Average Inverse Gini Coefficient for Participation (All-Time)",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "Average Inverse Gini Coefficient",
        minValue: 0,
        scaleType: 'log',
      },
      legend: { position: "none" },
    }
  );

  // Transpose data
  // https://stackoverflow.com/questions/17428587/transposing-a-2d-array-in-javascript
  data_inverse_gini_over_time = data_inverse_gini_over_time[0].map((col, i) =>
    data_inverse_gini_over_time.map((row) => row[i])
  );

  new google.visualization.LineChart(
    document.getElementById("chart_div_inverse_gini_over_time")
  ).draw(
    google.visualization.arrayToDataTable(data_inverse_gini_over_time),
    {
      title: "Inverse Gini Coefficient for Participation Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "Time (in days)",
        minValue: 0,
      },
      vAxis: {
        title: "Inverse Gini Coefficient",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
      curveType: "function",
    }
  );

  // Transpose data
  // https://stackoverflow.com/questions/17428587/transposing-a-2d-array-in-javascript
  data_price_over_time = data_price_over_time[0].map((col, i) =>
    data_price_over_time.map((row) => row[i])
  );

  new google.visualization.LineChart(
    document.getElementById("chart_div_price_over_time")
  ).draw(
    google.visualization.arrayToDataTable(data_price_over_time),
    {
      title: "Token Prices Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "Time (in days)",
        minValue: 0,
      },
      vAxis: {
        title: "Average price (USD)",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
      curveType: "function",
    }
  );

  // Transpose data
  // https://stackoverflow.com/questions/17428587/transposing-a-2d-array-in-javascript
  data_volume_over_time = data_volume_over_time[0].map((col, i) =>
    data_volume_over_time.map((row) => row[i])
  );

  new google.visualization.LineChart(
    document.getElementById("chart_div_volume_over_time")
  ).draw(
    google.visualization.arrayToDataTable(data_volume_over_time),
    {
      title: "Token Volumes Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "Time (in days)",
        minValue: 0,
      },
      vAxis: {
        title: "Average volume",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
      curveType: "function",
    }
  );

  new google.visualization.ScatterChart(
    document.getElementById("chart_principal_components")
  ).draw(
    google.visualization.arrayToDataTable(data_components),
    {
      title: "Principal Components (n=2)",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      hAxis: {
        title: "n1",
      },
      vAxis: {
        title: "n2",
      },
      legend: "none",
    }
  )
}

// Load the Visualization API and the corechart package.
google.charts.load("current", { packages: ["corechart", "bar"] });

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawGraphs);
