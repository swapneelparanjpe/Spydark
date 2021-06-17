
//* ACTIVE-INACTIVE LINKS  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
var link_status_ctx = document.getElementById("donut")
if (link_status_ctx) {  
	var donutChart = new Chart(link_status_ctx, {
		type: 'doughnut',
		data: {
			labels: ["Active Links", "Inactive Links"],
			datasets: [{
				data: [a, ia],
				backgroundColor: ['#4e73df', '#1cc88a'],
				hoverBackgroundColor: ['#2e59d9', '#17a673'],
				hoverBorderColor: "rgba(255, 255, 0)",
			}],
		},
		options: {
			maintainAspectRatio: false,
			tooltips: {
				backgroundColor: "rgb(255,255,255)",
				bodyFontColor: "#121212",
				borderWidth: 1,
				xPadding: 15,
				yPadding: 15,
				displayColors: true,
				caretPadding: 10,
			},
			legend: {
				position: 'right',
				labels: {
					fontColor: '#dedede',
					fontSize: 18,
				}
			},
			cutoutPercentage: 70,
		},
	});
}
//* <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

//* LINK MAP >>>>>>>>>>>>>>>>>>>>>>>>>>>>>

if (document.getElementById("treeChart")) {

	var margin = {top: 20, right: 120, bottom: 20, left: 200},
		width = 1750 - margin.right - margin.left,
		height = 3000 - margin.top - margin.bottom;
		
	var i = 0,
		duration = 750,
		root;

	var tree = d3.layout.tree()
		.size([height, width]);

	var diagonal = d3.svg.diagonal()
		.projection(function(d) { return [d.y, d.x]; });

	var svg = d3.select(".page-content").append("svg")
		.attr("width", width + margin.right + margin.left)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	root = treeData;
	root.x0 = height / 2;
	root.y0 = 0;
	
	update(root);

	d3.select(self.frameElement).style("height", "500px");

	function update(source) {

		// Compute the new tree layout.
		var nodes = tree.nodes(root).reverse(),
			links = tree.links(nodes);

		// Normalize for fixed-depth.
		nodes.forEach(function(d) { d.y = d.depth * 480; });

		// Update the nodes…
		var node = svg.selectAll("g.node")
			.data(nodes, function(d) { return d.id || (d.id = ++i); });

		// Enter any new nodes at the parent's previous position.
		var nodeEnter = node.enter().append("g")
			.attr("class", "node")
			.attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
			.on("click", click);

		nodeEnter.append("circle")
			.attr("r", 1e-6)
			.attr("id", function(d){return "node" + d.id})
			.style("fill", function(d) { return d._children ? "lightsteelblue" : "#dedede"; })
			.on("mouseover", function(d) {
				var pathway = d.name.link(d.name);
				while (d.parent) {
					d3.selectAll("#node"+d.id).style("fill", "red");//color the node
					if (d.parent){
						d3.selectAll("#link"+d.parent.id + "-" + d.id).style("stroke", "red");//color the path
						pathway = pathway + String.fromCodePoint(0x2B05) + d.parent.name.link(d.parent.name)
					}
					d = d.parent;
				}
				d3.selectAll("#node"+d.id).style("fill", "red");//color the node
				document.getElementById('textMssg').innerHTML = pathway;			
			})
			.on("mouseout", function(d) {
				while (d.parent) {
					d3.selectAll("#node"+d.id).style("fill", "#dedede");//color the node
					if (d.parent)
						d3.selectAll("#link"+d.parent.id + "-" + d.id).style("stroke", "#ccc");//color the path
					d = d.parent;
				}
				d3.selectAll("#node"+d.id).style("fill", "#dedede");//color the node
			});

		nodeEnter.append("text")
			.attr("x", function(d) { return d.children || d._children ? -13 : 13; })
			.attr("dy", ".35em")
			.attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
			.text(function(d) { return d.name; })
			.style("fill-opacity", 1e-6);

		// Transition nodes to their new position.
		var nodeUpdate = node.transition()
			.duration(duration)
			.attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

		nodeUpdate.select("circle")
			.attr("r", 10)
			.style("fill", function(d) { return d._children ? "lightsteelblue" : "#dedede"; });

		nodeUpdate.select("text")
			.style("fill-opacity", 1);

		// Transition exiting nodes to the parent's new position.
		var nodeExit = node.exit().transition()
			.duration(duration)
			.attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
			.remove();

		nodeExit.select("circle")
			.attr("r", 1e-6);

		nodeExit.select("text")
			.style("fill-opacity", 1e-6);

		// Update the links…
		var link = svg.selectAll("path.link")
			.data(links, function(d) { return d.target.id; });

		// Enter any new links at the parent's previous position.
		link.enter().insert("path", "g")
			.attr("class", "link")
			.attr("id", function(d){ return ("link" + d.source.id + "-" + d.target.id)})//unique id
			.attr("d", function(d) {
				var o = {x: source.x0, y: source.y0};
				return diagonal({source: o, target: o});
			});

		// Transition links to their new position.
		link.transition()
			.duration(duration)
			.attr("d", diagonal);

		// Transition exiting nodes to the parent's new position.
		link.exit().transition()
			.duration(duration)
			.attr("d", function(d) {
				var o = {x: source.x, y: source.y};
				return diagonal({source: o, target: o});
			})
			.remove();

		// Stash the old positions for transition.
		nodes.forEach(function(d) {
			d.x0 = d.x;
			d.y0 = d.y;
		});
	}

	// Toggle children on click.
	function click(d) {
		if (d.children) {
			d._children = d.children;
			d.children = null;
		} else {
			d.children = d._children;
			d._children = null;
		}
		update(d);
	}
}
//* <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


//* LINK STATUS OVER PERIOD OF TIME  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
var activity_period_ctx = document.getElementById("line_chart")
if (activity_period_ctx) {
	var weekNums = [];
	for (var i = -activity.length + 1; i <= 0; i++)
		weekNums.push(i);

	var lineChart = new Chart(activity_period_ctx, {
		type: 'line',
		data: {
			labels: weekNums,
			datasets: [{
				lineTension: 0,
				backgroundColor: "rgba(78, 115, 223, 0.05)",
				borderColor: "#3700b3",
				pointRadius: 2,
				pointBackgroundColor: "rgba(78, 115, 223, 1)",
				pointBorderWidth: 2,
				pointBorderColor: "rgba(78, 115, 223, 1)",
				pointHoverRadius: 3,
				pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
				pointHoverBorderColor: "rgba(78, 115, 223, 1)",
				pointHitRadius: 10,
				data: activity,
			}],
		},
		options: {
			legend: {
				display: false
			},
			maintainAspectRatio: false,
			bounds: {
				min: 0,
				max: 1,
			},
			tooltips: {
				displayColors: false,
				callbacks: {
                    label: function(tooltipItems) { 
                        if (tooltipItems.yLabel == 0) {
							return "Inactive"
						} else {
							return "Active"
						}
                    },
				
                }
			},
			scales: {
				yAxes: [{
					scaleLabel: {
						display: true,
						labelString: "Status",
					},
					ticks: {
						// Include a dollar sign in the ticks
						callback: value => {
							if (value == 0){
								return 'Inactive'
							} else if (value == 1) {
								return 'Active'
							} 
						}
					}
				}],
				xAxes: [{
					scaleLabel: {
						display: true,
						labelString: "Week number",
					},
				}],
			}
		},
	});
}
//* <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


//* LINK STATUS OF ALL LINKS OVER PERIOD OF TIME  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
var activity_all_ctx = document.getElementById("bar_chart")
console.log(">>>", activity)
if (activity_all_ctx) {
	var weekNums = [];
	for (var i = -active_links_period.length + 1; i <= 0; i++)
		weekNums.push(i);

	var lineChart = new Chart(activity_all_ctx, {
		type: 'bar',
		data: {
			labels: weekNums,
			datasets: [{
				label: 'No. of Active links',
				data: active_links_period,
				backgroundColor: '#4e73df'
			 }, {
				label: 'No. of Inactive links',
				data: inactive_links_period,
				backgroundColor: '#1cc88a'
			 }],
		},
		options: {
			scales: {
				y: {
					beginAtZero: true
				},
				xAxes: [{
					gridLines: {
						color: "#404040",
					},
					scaleLabel: {
						display: true,
						labelString: 'Week number'
					  },
				   stacked: true
				}],
				yAxes: [{
					gridLines: {
						color: "#404040",
					},
					scaleLabel: {
						display: true,
						labelString: 'Number of links'
					  },
				   stacked: true
				}]
			 }
		},

	});
}
//* <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


