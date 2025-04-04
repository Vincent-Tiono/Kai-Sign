import { Device } from "./device";

export const TitleScreen = ({
  functionName,
  owner,
  type,
}: {
  owner: string;
  functionName: string;
  type: string;
}) => (
  <>
    <Device.OperationSummary
      type={type}
    >{`Review ${type} to ${functionName}`}</Device.OperationSummary>
    <Device.InfoBlock owner={owner} />
  </>
);
