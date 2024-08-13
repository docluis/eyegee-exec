import React from "react";
import ReactMarkdown from "react-markdown";
import { useTheme } from "next-themes";
import { Card, CardHeader, CardBody, CardFooter, Chip } from "@nextui-org/react";

const NodeInfoBox = ({ node }) => {
  const { theme } = useTheme();
  const getNodeContent = (node) => {
    switch (node.type) {
      case "page":
        return (
          <Card className="w-[500px] h-[700px]">
            <CardHeader className="pb-0 pt-4 px-4 flex-row items-start gap-4">
              <Chip className="text-tiny uppercase font-bold" color="mycolor">Page</Chip>
              <h2 className="font-bold text-large">{node.label}</h2>
            </CardHeader>

            <CardBody className="overflow-visible py-2">
              <h4 className="pb-0 pt-4 font-bold">Summary</h4>
              <p>{node.summary}</p>
              <h4 className="pb-0 pt-4 font-bold">Outbound Links</h4>
              <ul>
                {node.outlinks.map((link) => (
                  <li key={link}>{link}</li>
                ))}
              </ul>
            </CardBody>
          </Card>
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
                <li key={input.name}>
                  {input.name} (type:{input.type})
                </li>
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
            <h3>Parameters</h3>
            <ul>
              {node.params.map((param) => (
                <li key={param.name}>
                  {param.name} (type:{param.type}){/* observed values */}
                  <ul>
                    {param.observed_values.map((value) => (
                      <li key={value}>{value}</li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
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
    // <div
    //   style={{
    //     padding: "10px",
    //     border: `1px solid ${theme == "light" ? "black" : "white"}`,
    //     // make is scrollable
    //     backgroundColor: theme == "light" ? "white" : "black",
    //     overflow: "auto",
    //     height: 700,
    //     width: 500,
    //   }}
    // >
    getNodeContent(node)
    // </div>
  );
};

export default NodeInfoBox;
