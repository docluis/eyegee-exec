import React, { useRef, useState, useEffect } from "react";
import * as d3 from "d3";
import NodeInfoBox from "./NodeInfoBox.js";

const ForceGraph = ({ nodesData, linksData }) => {
  const svgRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    const width = 928;
    const height = 680;

    const color = d3.scaleOrdinal(d3.schemeCategory10);

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
      ) // Increased link distance
      .force("charge", d3.forceManyBody().strength(-2000)) // Adjusted charge strength
      .force("x", d3.forceX())
      .force("y", d3.forceY());

    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("style", "max-width: 100%; height: auto;");

    svg.selectAll("*").remove(); // Clear existing elements

    const link = svg
      .append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke-width", (d) => Math.sqrt(d.value));

    const node = svg
      .append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", 15)
      .attr("fill", (d) => {
        if (d.type === "page") return "lightblue";
        if (d.type === "api") return "red";
        if (d.type === "interaction") return "purple";
        return color(d.group); // Default color
      })
      .on("click", (event, d) => setSelectedNode(d)); // Highlight on click

    // node.append("title").text((d) => d.label);

    const text = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .attr("dy", 0)
      .attr("dx", 20)
      .text((d) => d.label) // Adding name as text
      .style("fill", "black")
      .attr("font-size", "14px");

    node.call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );

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
  }, [nodesData, linksData]); // Run the effect only when nodesData or linksData changes

  return (
    <>
      <svg ref={svgRef}></svg>
      {selectedNode && <NodeInfoBox node={selectedNode} />}
    </>
  );
};

export default ForceGraph;
