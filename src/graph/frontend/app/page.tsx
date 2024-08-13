"use client";

import { Link } from "@nextui-org/link";
import { Snippet } from "@nextui-org/snippet";
import { Code } from "@nextui-org/code";
import { button as buttonStyles } from "@nextui-org/theme";

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";

import ForceGraph from "@/components/ForceGraph";
import { useState, useEffect } from "react";
import NodeInfoBox from "@/components/NodeInfoBox";
import { Skeleton } from "@nextui-org/react";

export default function Home() {
  const [message, setMessage] = useState("");
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);

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
        setIsLoaded(true);
      })
      .catch((error) => {
        setMessage("Error fetching data from backend");
        console.error("Error fetching data: ", error);
      });
  }, []);

  return (
    <section className="relative flex items-center justify-center gap-4">
      <div
        className="relative inline-block text-center justify-center"
        style={{
          width: "100%",
          height: "100%",
          overflow: "hidden",
        }}
      >
        <Skeleton className="rounded-lg" isLoaded={isLoaded}>
          <ForceGraph
            nodesData={graph.nodes}
            linksData={graph.links}
            setSelectedNode={setSelectedNode}
          />
        </Skeleton>
      </div>
      {selectedNode && (
        <div className="absolute right-0 top-0">
          <NodeInfoBox node={selectedNode} />
        </div>
      )}
    </section>

    //
    //   <div className="inline-block max-w-lg text-center justify-center">
    //     <h1 className={title()}>Make&nbsp;</h1>
    //     <h1 className={title({ color: "violet" })}>beautiful&nbsp;</h1>
    //     <br />
    //     <h1 className={title()}>
    //       websites regardless of your design experience.
    //     </h1>
    //     <h2 className={subtitle({ class: "mt-4" })}>
    //       Beautiful, fast and modern React UI library.
    //     </h2>
    //   </div>

    //   <div className="flex gap-3">
    //     <Link
    //       isExternal
    //       className={buttonStyles({
    //         color: "primary",
    //         radius: "full",
    //         variant: "shadow",
    //       })}
    //       href={siteConfig.links.docs}
    //     >
    //       Documentation
    //     </Link>
    //     <Link
    //       isExternal
    //       className={buttonStyles({ variant: "bordered", radius: "full" })}
    //       href={siteConfig.links.github}
    //     >
    //       <GithubIcon size={20} />
    //       GitHub
    //     </Link>
    //   </div>

    //   <div className="mt-8">
    //     <Snippet hideCopyButton hideSymbol variant="bordered">
    //       <span>
    //         Get started by editing <Code color="primary">app/page.tsx</Code>
    //       </span>
    //     </Snippet>
    //   </div>
    // </section>
  );
}
