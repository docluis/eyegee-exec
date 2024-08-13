"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import { useTheme } from "next-themes";
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Chip,
  Table,
  TableHeader,
  TableBody,
  TableColumn,
  TableRow,
  TableCell,
} from "@nextui-org/react";

const NodeInfoBox = ({ node }) => {
  const { theme } = useTheme();
  const getColor = (type) => {
    switch (type) {
      case "page":
        return theme == "light" ? "bg-pageColor-light" : "bg-pageColor-dark";
      case "interaction":
        return theme == "light"
          ? "bg-interactionColor-light"
          : "bg-interactionColor-dark";
      case "api":
        return theme == "light" ? "bg-apiColor-light" : "bg-apiColor-dark";
      default:
        return "bg-gray-500";
    }
  };

  const getNodeContent = (node) => {
    switch (node.type) {
      case "page":
        return (
          <>
            <h4 className="pb-0 pt-4 font-bold">Summary</h4>
            <p>{node.summary}</p>
            <h4 className="pb-0 pt-4 font-bold">Outbound Links</h4>
            <ul>
              {node.outlinks.map((link) => (
                <li key={link}>{link}</li>
              ))}
            </ul>
          </>
        );
      case "interaction":
        return (
          <>
            <h4 className="pb-0 pt-4 font-bold">Description</h4>
            <p>{node.description}</p>
            <h4 className="pb-0 pt-4 font-bold">Inputs</h4>
            <ul>
              {node.input_fields.map((input) => (
                <li key={input.name}>
                  {input.name} (type:{input.type})
                </li>
              ))}
            </ul>
            <h4 className="pb-0 pt-4 font-bold">Behavior</h4>
            <ReactMarkdown>{node.behaviour}</ReactMarkdown>
          </>
        );
      case "api":
        return (
          <>
            <h4 className="pb-0 pt-4 font-bold">Parameters</h4>
            {/* Table */}
            <Table className="pb-0 pt-4 w-full">
              <TableHeader
                columns={[
                  { key: "type", label: "TYPE" },
                  { key: "name", label: "NAME" },
                  { key: "values", label: "OBSERVED VALUES" },
                ]}
              >
                {(column) => (
                  <TableColumn key={column.key}>{column.label}</TableColumn>
                )}
              </TableHeader>
              <TableBody emptyContent={"No parameters Observed."}>
                {/* print the params */}
                {console.log(node.params)}
                {node.params.map((param) => (
                  <TableRow key={param.name}>
                    <TableCell>{param.type}</TableCell>
                    <TableCell>{param.name}</TableCell>
                    <TableCell>{param.observed_values.join(", ")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
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
    <Card className="w-[500px] h-[700px]">
      <CardHeader className="pb-0 pt-4 px-4 flex-row items-start gap-4">
        <Chip
          classNames={{
            base: `${getColor(node.type)} text-tiny uppercase font-bold`,
            content: theme == "light" ? "text-white" : "text-black",
          }}
        >
          {node.type}
        </Chip>
        <h2 className="font-bold text-large">{node.label}</h2>
      </CardHeader>

      <CardBody className="overflow-visible py-2">
        {/* <h4 className="pb-0 pt-4 font-bold">Summary</h4>
              <p>{node.summary}</p>
              <h4 className="pb-0 pt-4 font-bold">Outbound Links</h4>
              <ul>
                {node.outlinks.map((link) => (
                  <li key={link}>{link}</li>
                ))}
              </ul> */}
        {getNodeContent(node)}
      </CardBody>
    </Card>
    // </div>
  );
};

export default NodeInfoBox;
