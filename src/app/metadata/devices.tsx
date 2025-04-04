import { Device } from "~/components/devices/device";
import { TitleScreen } from "~/components/devices/titleScreen";
import { InfoScreen } from "~/components/devices/infoScreen";
import { type Erc7730 } from "~/store/types";
import { MetadataInfoScreen } from "~/components/devices/metaDataScreen";

interface Props {
  metadata?: Erc7730["metadata"];
  address: string | null;
}

const Devices = ({ metadata, address }: Props) => {
  return (
    <Device.Frame>
      <MetadataInfoScreen
        owner={metadata?.owner ?? ""}
        info={metadata?.info}
        address={address ?? ""}
      />
    </Device.Frame>
  );
};

export default Devices;
