import Image from "next/image";

import flexBackArrow from "./assets/flex-back-arrow.svg";
import staxBackArrow from "./assets/stax-back-arrow.svg";
import { cn } from "~/lib/utils";
import { Device } from "./device";
import { type Erc7730 } from "~/store/types";

export const InfoScreen = ({
  address,
  info,
}: {
  address: string;
  info?: Erc7730["metadata"]["info"];
}) => {
  const isStax = false;

  return (
    <>
      <div className="border-light-grey relative border-b">
        <div
          className={cn(
            "absolute bottom-0 left-0 top-0 flex items-center justify-center",
            isStax ? "w-[44px]" : "w-[52px]",
          )}
        >
          {isStax ? (
            <Image
              className="inline-block w-4"
              src={staxBackArrow as string}
              alt="Back"
              width={16}
              height={16}
            />
          ) : (
            <Image
              className="inline-block w-5"
              src={flexBackArrow as string}
              alt="Back"
              width={20}
              height={20}
            />
          )}
        </div>
        <div
          className={cn(
            "py-[6px] text-center",
            isStax ? "px-[44px]" : "px-[52px]",
          )}
        >
          <Device.ActionText>Smart contract information</Device.ActionText>
        </div>
      </div>
      <div className="grow">
        <Device.Section>
          <Device.ActionText>Contract owner</Device.ActionText>
          <Device.ContentText>
            {info?.legalName ?? ""}
            <br />
            {info?.url ?? ""}
          </Device.ContentText>
        </Device.Section>
        <Device.Section>
          <Device.ActionText>Contract address</Device.ActionText>
          <Device.ContentText>{address}</Device.ContentText>
        </Device.Section>
      </div>
      <div></div>
    </>
  );
};
