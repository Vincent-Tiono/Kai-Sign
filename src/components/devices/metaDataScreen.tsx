import Image from "next/image";

import flexBackArrow from "./assets/flex-back-arrow.svg";
import { cn } from "~/lib/utils";
import { Device } from "./device";
import { type Erc7730 } from "~/store/types";

export const MetadataInfoScreen = ({
  address,
  info,
  owner,
}: {
  owner: string;
  address: string;
  info?: Erc7730["metadata"]["info"];
}) => {
  return (
    <>
      <div className="border-light-grey relative border-b">
        <div
          className={cn(
            "absolute bottom-0 left-0 top-0 flex items-center justify-center",
            "w-[52px]",
          )}
        >
          <Image
            className="inline-block w-5"
            src={flexBackArrow as string}
            alt="Back"
            width={20}
            height={20}
          />
        </div>
        <div className={cn("py-[14px] text-center")}>
          <Device.ActionText>
            {owner === "" ? <span>Contract owner name</span> : owner}
          </Device.ActionText>
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
