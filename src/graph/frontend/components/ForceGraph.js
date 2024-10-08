import React, { useRef, useState, useEffect } from "react";
import * as d3 from "d3";
import { useTheme } from "next-themes";

const ForceGraph = ({ nodesData, linksData, setSelectedNode }) => {
  const { theme } = useTheme();
  const svgRef = useRef();

  useEffect(() => {
    const width = 1400;
    const height = 700;

    const links = linksData.map((d) => ({ ...d }));
    const nodes = nodesData.map((d) => ({ ...d }));

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-600))
      .force(
        "x",
        d3
          .forceX()
          .strength(0.1)
          .x(width * -0.2)
      )
      .force("y", d3.forceY());

    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("style", "max-width: 100%; height: auto;");

    svg.selectAll("*").remove();

    const zoomGroup = svg.append("g");

    const link = zoomGroup
      .append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke-width", (d) => Math.sqrt(d.value));

    const node = zoomGroup
      .append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", 15)
      .attr("fill", (d) => getColorNode(d, theme)) // Set initial color
      .on("click", (event, d) => setSelectedNode(d));

    const text = zoomGroup
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .attr("dy", 0)
      .attr("dx", 20)
      .text((d) => d.label)
      .style("fill", theme == "light" ? "black" : "white")
      .attr("font-size", "14px");

    node.call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );

    const zoom = d3
      .zoom()
      .scaleExtent([0.1, 4]) // Zoom scale limits
      .on("zoom", (event) => {
        zoomGroup.attr("transform", event.transform);
      });

    svg.call(zoom);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

      text.attr("x", (d) => d.x).attr("y", (d) => d.y);
    });

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return () => simulation.stop();
  }, [nodesData, linksData]);

  // Separate useEffect to handle theme changes
  useEffect(() => {
    const customColors = {
      page: theme === "dark" ? "#99C7FB" : "#006FEE",
      interaction: theme === "dark" ? "#C9A9E9" : "#7828C8",
      api: theme === "dark" ? "#FAA0BF" : "#F31260",
    };

    // Select all nodes and update their fill color based on theme
    d3.select(svgRef.current)
      .selectAll("circle")
      .attr("fill", (d) => getColorNode(d, theme));

    // Update text color
    d3.select(svgRef.current)
      .selectAll("text")
      .style("fill", theme === "light" ? "black" : "white");
  }, [theme]);

  // Helper function to get node color based on type and theme
  const getColorNode = (node, theme) => {
    if (node.type === "page") return theme === "dark" ? "#99C7FB" : "#006FEE";
    if (node.type === "api") return theme === "dark" ? "#FAA0BF" : "#F31260";
    if (node.type === "interaction")
      return theme === "dark" ? "#C9A9E9" : "#7828C8";
    return d3.schemeCategory10[node.group % 10]; // Default color
  };

  return <svg ref={svgRef}></svg>;
};

export default ForceGraph;
