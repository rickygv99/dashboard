// UI functions

function openFilterSettings() {
  document.getElementById("filterSettings").style.width = "250px";
  document.getElementById("content").style.marginLeft = "250px";
}

function closeFilterSettings() {
  document.getElementById("filterSettings").style.width = "0";
  document.getElementById("content").style.marginLeft = "0";
}


var data = JSON.parse(document.getElementById("data").textContent);
sortVotingRate(true);

var visibleData = [];
for (let data_dao of data) {
  visibleData.push(data_dao["name"]);
}

const onchainData = ["Compound"];


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


var dateSlider = document.getElementById("dateRangeSlider");
var dateRange = dateSlider.value;
dateSlider.onchange = function() {
  dateRange = this.value;
  drawGraphs();
}

var offchainToggle = document.getElementById("offchainToggle")
offchainToggle.addEventListener("click", function() {
  for (let data_dao of data) {
    if (onchainData.includes(data_dao["name"]) == false) {
      if (this.checked) {
        if (visibleData.includes(data_dao["name"]) == false) {
          visibleData.push(data_dao["name"])
        }
      } else {
        visibleData = visibleData.filter(val => val !== data_dao["name"]);
      }
      var checkbox = document.getElementById("checkbox_" + data_dao["name"]);
      checkbox.checked = this.checked
    }
  }
  drawGraphs();
});
var onchainToggle = document.getElementById("onchainToggle")
onchainToggle.addEventListener("click", function() {
  for (let data_dao of data) {
    if (onchainData.includes(data_dao["name"])) {
      if (this.checked) {
        if (visibleData.includes(data_dao["name"]) == false) {
          visibleData.push(data_dao["name"])
        }
      } else {
        visibleData = visibleData.filter(val => val !== data_dao["name"]);
      }
      var checkbox = document.getElementById("checkbox_" + data_dao["name"]);
      checkbox.checked = this.checked
    }
  }
  drawGraphs();
});


// Sorting functions

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


// Graphing functions

const GRAPH_WIDTH = 500;
const GRAPH_HEIGHT = 500;
const CHART_LEFT = 140;
const LABEL_FONT_SIZE = 8;

function transpose(data) {
  // https://stackoverflow.com/questions/17428587/transposing-a-2d-array-in-javascript
  return data[0].map((col, i) =>
    data.map((row) => row[i])
  );
}

function graphVotingRateAllTime(data_avr_all_time) {
  new google.visualization.BarChart(
    document.getElementById("chart_div_avr_all_time")
  ).draw(
    google.visualization.arrayToDataTable(data_avr_all_time),
    {
      title: "Voting Rates (All-Time)",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "Average voting rate (%)",
        scaleType: 'log',
        viewWindow: {
          max: 100,
        },
      },
      vAxis: {
        textStyle: {
          fontSize: LABEL_FONT_SIZE,
        },
      },
      legend: { position: "none" },
    }
  );
}

function graphVotingRateOverTime(data_avr_over_time) {
  let data_format = google.visualization.arrayToDataTable(transpose(data_avr_over_time));
  let formatter = new google.visualization.NumberFormat({ pattern: '#%', fractionDigits: 5 });
  formatter.format(data_format, 0);

  new google.visualization.LineChart(
    document.getElementById("chart_div_avr_over_time")
  ).draw(
    data_format,
    {
      title: "Voting Rate Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "Time (in days prior)",
        minValue: 0,
      },
      vAxis: {
        title: "Average voting rate (%)",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
    }
  );
}

function graphInverseGiniAllTime(data_inverse_gini_all_time) {
  new google.visualization.BarChart(
    document.getElementById("chart_div_inverse_gini_all_time")
  ).draw(
    google.visualization.arrayToDataTable(data_inverse_gini_all_time),
    {
      title: "Inverse Gini Coef. for Participation (All-Time)",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "Average Inverse Gini Coef.",
        scaleType: 'log',
        viewWindow: {
          max: 1,
        },
      },
      vAxis: {
        textStyle: {
          fontSize: LABEL_FONT_SIZE,
        },
      },
      legend: { position: "none" },
    }
  );
}

function graphInverseGiniOverTime(data_inverse_gini_over_time) {
  new google.visualization.LineChart(
    document.getElementById("chart_div_inverse_gini_over_time")
  ).draw(
    google.visualization.arrayToDataTable(transpose(data_inverse_gini_over_time)),
    {
      title: "Inverse Gini Coef. for Participation Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "Time (in days prior)",
        minValue: 0,
      },
      vAxis: {
        title: "Average Inverse Gini Coef.",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
    }
  );
}

function graphPriceOverTime(data_price_over_time) {
  new google.visualization.LineChart(
    document.getElementById("chart_div_price_over_time")
  ).draw(
    google.visualization.arrayToDataTable(transpose(data_price_over_time)),
    {
      title: "Token Prices Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "Time (in days prior)",
        minValue: 0,
      },
      vAxis: {
        title: "Average price (USD)",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
    }
  );
}

function graphVolumeOverTime(data_volume_over_time) {
  new google.visualization.LineChart(
    document.getElementById("chart_div_volume_over_time")
  ).draw(
    google.visualization.arrayToDataTable(transpose(data_volume_over_time)),
    {
      title: "Token Volumes Over Time",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "Time (in days prior)",
        minValue: 0,
      },
      vAxis: {
        title: "Average volume",
        scaleType: 'log',
      },
      legend: { position: "bottom" },
    }
  );
}

function graphPrincipalComponents(data_components) {
  new google.visualization.ScatterChart(
    document.getElementById("chart_principal_components")
  ).draw(
    google.visualization.arrayToDataTable(data_components),
    {
      title: "Principal Components (n=2)",
      width: GRAPH_WIDTH,
      height: GRAPH_HEIGHT,
      chartArea: {
        left: CHART_LEFT,
      },
      hAxis: {
        title: "n1",
      },
      vAxis: {
        title: "n2",
      },
      legend: "none",
    }
  );
}

function drawGraphs() {
  var data_avr_all_time = [["Name", "Average voting rate", {role: "style"}]];
  var data_inverse_gini_all_time = [["Name", "Average Gini coefficient", {role: "style"}]];
  var over_time_header = ["Time (in days prior)"];
  let options = document.getElementById("dateRange").options;
  for (let option of options) {
    over_time_header.push(String(option.value));
    if (String(option.value) === String(dateRange)) {
      break;
    }
  }
  var data_avr_over_time = [over_time_header];
  var data_inverse_gini_over_time = [over_time_header];
  var data_price_over_time = [over_time_header];
  var data_volume_over_time = [over_time_header];
  var data_components = [["nf1", "nf2", {role: "annotation"}]];

  for (let data_dao of data) {
    if (visibleData.includes(data_dao["name"]) == false) {
      continue;
    }

    let bar_color = "blue";
    if (onchainData.includes(data_dao["name"])) {
      bar_color = "red";
    }

    data_avr_all_time.push([data_dao["name"], data_dao["average_voting_rate_all_time"], bar_color]);
    data_inverse_gini_all_time.push([data_dao["name"], data_dao["average_inverse_gini_all_time"], bar_color]);

    data_avr_over_time_dao = [data_dao["name"]];
    data_inverse_gini_over_time_dao = [data_dao["name"]];
    data_price_over_time_dao = [data_dao["name"]];
    data_volume_over_time_dao = [data_dao["name"]];

    // We use the same number of periods for each of graphs
    let num_total_periods = data_dao["average_voting_rates"].length
    let num_periods = over_time_header.length - 1

    for (let i = num_total_periods - num_periods; i < num_total_periods; i++) {
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

  graphVotingRateAllTime(data_avr_all_time);
  graphVotingRateOverTime(data_avr_over_time);
  graphInverseGiniAllTime(data_inverse_gini_all_time);
  graphInverseGiniOverTime(data_inverse_gini_over_time);
  graphPriceOverTime(data_price_over_time);
  graphVolumeOverTime(data_volume_over_time);
  graphPrincipalComponents(data_components);
}

// Load the Visualization API and the corechart package.
google.charts.load("current", { packages: ["corechart", "bar"] });

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawGraphs);
