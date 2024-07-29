import React from "react";
import ReactMarkdown from "react-markdown";

const NodeInfoBox = ({ node }) => {
  const getNodeContent = (node) => {
    switch (node.type) {
      case "page":
        return (
          <div>
            <h3>{node.label} (Page)</h3>
            <h4>Summary</h4>
            <p>{node.summary}</p>
            <h4>Outbound Links</h4>
            <ul>
              {node.outlinks.map((link) => (
                <li key={link}>{link}</li>
              ))}
            </ul>
          </div>
        );
      case "interaction":
        return (
          <>
            <h3>{node.label} (Interaction)</h3>
            <h3>Description</h3>
            <p>{node.description}</p>
            <h3>Inputs</h3>
            <ul>
              {node.input_fields.map((input) => (
                <li key={input.name}>{input.name} (type:{input.type})</li>
              ))}
            </ul>
            <h3>Behavior</h3>
            <ReactMarkdown>{node.behaviour}</ReactMarkdown>
          </>
        );
      case "api":
        return (
          <>
            <h3>{node.label} (API)</h3>
            <p>
              This is an API node. Information about the API can be provided
              here.
            </p>
          </>
        );
      default:
        return (
          <>
            <h3>{node.label}</h3>
            <p>Additional information about the node can go here.</p>
          </>
        );
    }
  };
  return (
    <div
      style={{
        position: "absolute",
        top: 10,
        right: 10,
        width: 500,
        background: "white",
        padding: "10px",
        border: "1px solid black",
      }}
    >
      {getNodeContent(node)}
    </div>
  );
};

export default NodeInfoBox;
