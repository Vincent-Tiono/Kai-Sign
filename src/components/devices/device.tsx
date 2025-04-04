import { type ReactNode } from "react";
import Image from "next/image";
import flexInfo from "./assets/flex-info.svg";
import staxInfo from "./assets/stax-info.svg";
import flexSignButton from "./assets//flex-sign-button.svg";
import staxSignButton from "./assets//stax-sign-button.svg";
import { cn } from "~/lib/utils";
import { Stax } from "./stax";
import { Flex } from "./flex";

export const Device = {
  ActionText: ({ children }: { children: ReactNode }) => {
    const isStax = false;

    return (
      <div
        className={cn(
          "font-semibold",
          isStax ? "text-[12px] leading-[16px]" : "text-[14px] leading-[18px]",
        )}
      >
        {children}
      </div>
    );
  },
  ContentText: ({ children }: { children: ReactNode }) => {
    const isStax = false;

    return (
      <div
        className={cn(
          "break-words",
          isStax ? "text-[12px] leading-[16px]" : "text-[14px] leading-[18px]",
        )}
      >
        {children}
      </div>
    );
  },
  Frame: ({
    children,
    size = "normal",
  }: {
    children: ReactNode;
    size?: "small" | "normal";
  }) => {
    const isStax = false;
    const Component = isStax ? Stax : Flex;

    return (
      <Component.Bezel size={size}>
        <div
          className={cn(
            "flex w-full flex-col justify-between text-black antialiased",
            size === "small" && "items-center",
          )}
        >
          {children}
        </div>
      </Component.Bezel>
    );
  },
  HeadingText: ({ children }: { children: ReactNode }) => {
    const isStax = false;

    return (
      <div
        className={cn(
          "font-medium leading-[20px]",
          isStax ? "text-[16px]" : "text-[18px]",
        )}
      >
        {children}
      </div>
    );
  },
  InfoBlock: ({ owner }: { owner: string }) => {
    const isStax = false;

    return (
      <div
        className={cn(
          "flex items-center",
          isStax ? "gap-3 p-3" : "gap-4 px-4 py-3",
        )}
      >
        <div>
          <Device.ContentText>
            {`You're interacting with a smart contract from ${owner}.`}
          </Device.ContentText>
        </div>
        <div>
          <div className="border-light-grey flex h-[32px] w-[32px] items-center justify-center rounded-full border">
            {isStax ? (
              <Image
                src={staxInfo as string}
                alt="More info"
                width={16}
                height={16}
              />
            ) : (
              <Image
                src={flexInfo as string}
                alt="More info"
                width={20}
                height={20}
              />
            )}
          </div>
        </div>
      </div>
    );
  },
  Icon: ({ bg }: { bg: string }) => (
    <div
      className={cn(
        "h-[32px] w-[32px] self-center bg-contain bg-no-repeat",
        bg,
      )}
    />
  ),
  OperationSummary: ({
    children,
    type,
  }: {
    children: string;
    type: string;
  }) => {
    const isStax = false;
    const iconBg =
      type === "message"
        ? "bg-[url(/assets/scroll.svg)]"
        : "bg-[url(/assets/eth.svg)]";

    return (
      <div
        className={cn(
          "align-center border-light-grey flex grow flex-col justify-center gap-3 border-b",
          isStax ? "p-3" : "p-4",
        )}
      >
        <Device.Icon bg={iconBg} />
        <Device.HeadingText>
          <div className="text-center">{children}</div>
        </Device.HeadingText>
      </div>
    );
  },
  Pagination: ({ current, total }: { current: number; total: number }) => {
    const isStax = false;

    return isStax ? (
      <Stax.Pagination current={current} total={total} />
    ) : (
      <Flex.Pagination current={current} total={total} />
    );
  },
  Section: ({ children }: { children: ReactNode }) => {
    const isStax = false;

    return (
      <div
        className={cn(
          "border-light-grey flex flex-col border-b py-[14px] last:border-0",
          isStax ? "gap-[8px] px-3" : "gap-[6px] px-4",
        )}
      >
        {children}
      </div>
    );
  },
  SignButton: () => {
    const isStax = false;

    const Button = () =>
      isStax ? (
        <Image
          src={staxSignButton as string}
          alt="Sign"
          width={40}
          height={40}
        />
      ) : (
        <Image
          src={flexSignButton as string}
          alt="Sign"
          width={44}
          height={44}
        />
      );

    return (
      <div
        className={cn(
          "flex items-center justify-between",
          isStax ? "px-3 py-[10px]" : "p-4",
        )}
      >
        <Device.HeadingText>Hold to sign</Device.HeadingText>
        <div
          className={cn(
            "border-light-grey flex items-center justify-center rounded-full border",
            isStax ? "h-[40px] w-[40px]" : "h-[44px] w-[44px]",
          )}
        >
          <Button />
        </div>
      </div>
    );
  },
};
