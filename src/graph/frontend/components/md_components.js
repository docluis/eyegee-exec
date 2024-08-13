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
} from "@nextui-org/react";

export const md_components = {
  // code: ({ node, inline, className, children, ...props }) => {
  //   return <Code>{children}</Code>;
  // },
  h1: ({ node, inline, className, children, ...props }) => {
    return <h3 className="text-2xl font-bold">{children}</h3>;
  },
  // numbered lists
  ol: ({ node, inline, className, children, ...props }) => {
    return <ol className="list-decimal">{children}</ol>;
  },
  // bulleted lists with correct indentation
  ul: ({ node, inline, className, children, ...props }) => {
    return <ul className="list-disc">{children}</ul>;
  },
  // list items
  li: ({ node, inline, className, children, ...props }) => {
    return <li>{children}</li>;
  },
  // json code block with line formatting
  // mono-spaced text (exclude pre blocks)
  code: ({ node, inline, className, children, ...props }) => {
    return (
      <Code>
        <pre>{children}</pre>
      </Code>
    );
  },
  h3: ({ node, inline, className, children, ...props }) => {
    return <h3 className="text-lg font-bold">{children}</h3>;
  },
  h4: ({ node, inline, className, children, ...props }) => {
    return <h4 className="text-base font-bold">{children}</h4>;
  },
  p: ({ node, inline, className, children, ...props }) => {
    return <p className="text-base">{children}</p>;
  },
};
