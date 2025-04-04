"use client";

import * as CollapsiblePrimitive from "@radix-ui/react-collapsible";
import { cn } from "~/lib/utils";

const Collapsible = CollapsiblePrimitive.Root;

const CollapsibleTrigger = CollapsiblePrimitive.CollapsibleTrigger;

const CollapsibleContent = ({
  className,
  ...props
}: React.ComponentPropsWithoutRef<
  typeof CollapsiblePrimitive.CollapsibleContent
>) => {
  return (
    <CollapsiblePrimitive.CollapsibleContent
      className={cn(
        "data-[state=closed]:animate-collapsible-up data-[state=open]:animate-collapsible-down overflow-hidden px-1",
        className,
      )}
      {...props}
    />
  );
};

export { Collapsible, CollapsibleTrigger, CollapsibleContent };
