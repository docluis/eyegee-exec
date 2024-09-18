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
  Code,
  Button,
} from "@nextui-org/react";
import { md_components } from "./md_components";
import { XIcon } from "./icons";

const NodeInfoBox = ({ selectedNode, setSelectedNode }) => {
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

  const getNodeContent = (selectedNode) => {
    console.log(selectedNode);
    switch (selectedNode.type) {
      case "page":
        return (
          <>
            <h4 className="pb-0 pt-4 font-bold">Summary</h4>
            <p>{selectedNode.summary}</p>
            <h4 className="pb-0 pt-4 font-bold">Outbound Links</h4>
            {/* <ul>
              {selectedNode.outlinks.map((link) => (
                <li key={link}>{link}</li>
              ))}
            </ul> */}
            {/* list the outgoing links as buttons with setSelectedNode */}
            {/* TODO: seperate internal and external links */}
            <div className="flex flex-wrap gap-2"> 
              {selectedNode.outlinks.map((link) => (
                <Button
                  key={link}
                  variant="ghost"
                  onClick={() => {}} // TODO: setSelectedNode with the link
                >
                  {link}
                </Button>
              ))}
            </div>
          </>
        );
      case "interaction":
        return (
          <>
            <h4 className="pb-0 pt-4 font-bold">Description</h4>
            <p>{selectedNode.description}</p>
            {/* <h4 className="pb-0 pt-4 font-bold">Inputs</h4>
            <ul>
              {selectedNode.input_fields.map((input) => (
                <li key={input.name}>
                  {input.name} (type:{input.type})
                </li>
              ))}
            </ul> */}
            <h4 className="pb-0 pt-4 font-bold">Test Report</h4>
            {/* make it scrollable, make height dynamic */}
            <Card className="w-full h-[500px] overflow-auto">
              {/* add line distance */}
              <CardBody className="pb-0 pt-4 px-8 w-full">
                <ReactMarkdown components={md_components}>
                  {selectedNode.test_report}
                </ReactMarkdown>
              </CardBody>
            </Card>
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
                {console.log(selectedNode.params)}
                {selectedNode.params.map((param) => (
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
            <h3>{selectedNode.label}</h3>
            <p>Node Does Not Exist</p>
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
      <CardHeader className="pb-0 pt-4 px-4 flex-row justify-between">
        <Chip
          classNames={{
            base: `${getColor(selectedNode.type)} text-tiny uppercase font-bold`,
            content: theme == "light" ? "text-white" : "text-black",
          }}
        >
          {selectedNode.type}
        </Chip>
        <h2 className="font-bold text-large">{selectedNode.label}</h2>
        {/* icon to close aka set selected node="" */}
        <Button
          isIconOnly
          variant="light"
          onClick={() => setSelectedNode(null)}
        >
          <XIcon />
        </Button>
      </CardHeader>

      <CardBody className="overflow-visible py-2">
        {/* <h4 className="pb-0 pt-4 font-bold">Summary</h4>
              <p>{selectedNode.summary}</p>
              <h4 className="pb-0 pt-4 font-bold">Outbound Links</h4>
              <ul>
                {selectedNode.outlinks.map((link) => (
                  <li key={link}>{link}</li>
                ))}
              </ul> */}
        {getNodeContent(selectedNode)}
      </CardBody>
    </Card>
    // </div>
  );
};

export default NodeInfoBox;
