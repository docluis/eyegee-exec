import "./App.css";
import React, { useEffect, useState, useCallback } from "react";

// import from Graph.js
import ForceGraph from "./ForceGraph";

import "@xyflow/react/dist/style.css";

const App = () => {
  const [message, setMessage] = useState("");
  const [graph, setGraph] = useState({ nodes: [], links: [] });

  useEffect(() => {
    fetch("http://localhost:9778/graph")
      .then((response) => response.json())
      .then((data) => {
        let nodes = data.nodes;
        let links = data.links;

        setGraph({
          nodes: nodes,
          links: links,
        });
      })
      .catch((error) => {
        setMessage("Error fetching data from backend");
        console.error("Error fetching data: ", error);
      });
  }, []);

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <h1>Eyegee-Exec Graph</h1>
      {/* <ForceGraph nodesData={graph.nodes} linksData={graph.links} /> */}
      <ForceGraph nodesData={graph.nodes} linksData={graph.links} />
      {/* alert if error messages */}

      {message && <alert>{message}</alert>}
    </div>
  );
};

export default App;
