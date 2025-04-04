import Image from "next/image";
import { type ReactNode } from "react";
import flexChevronLeft from "./assets/flex-chevron-left.svg";
import flexChevronRight from "./assets/flex-chevron-right.svg";
import { Device } from "./device";
import { cn } from "~/lib/utils";

// Dimensions of the area to display the fields: 480px x 464px
// Number of lines for tags & values: 9

export const Flex = {
  Bezel: ({
    children,
    size,
  }: {
    children: ReactNode;
    size: "small" | "normal";
  }) => (
    <div
      className={cn(
        "h-[416.5px] w-[301.5px] bg-[url(/assets/DeviceBezel-Flex.png)] bg-contain bg-no-repeat p-[29.5px]",
        size === "small" && "h-[41.6px] w-[30.1px] p-0",
      )}
    >
      <div
        className={cn(
          "flex h-[300px] w-[240px] overflow-hidden rounded-[8px]",
          size === "small" && "flex h-full w-full items-center",
        )}
      >
        {children}
      </div>
    </div>
  ),
  Pagination: ({ current, total }: { current: number; total: number }) => {
    const first = current === 1;
    const last = current === total;

    return (
      <div className="border-light-grey flex border-t">
        <div className="border-light-grey border-r px-[26.5px] py-[14px]">
          <Device.ActionText>Reject</Device.ActionText>
        </div>
        <div className="text-dark-grey flex w-full items-center justify-center gap-4 px-4">
          <Image
            src={flexChevronLeft as string}
            alt="left"
            className={cn("inline-block h-[15px]", { "opacity-15": first })}
          />
          <Device.ContentText>
            {current} of {total}
          </Device.ContentText>
          <Image
            src={flexChevronRight as string}
            alt="left"
            className={cn("inline-block h-[15px]", { "opacity-15": last })}
          />
        </div>
      </div>
    );
  },
};
