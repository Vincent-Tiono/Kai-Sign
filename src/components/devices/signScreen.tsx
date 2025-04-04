import { Device } from "./device";

export const SignScreen = ({
  intent,
  type,
}: {
  intent: string;
  type: string;
}) => (
  <>
    <Device.OperationSummary type={type}>
      {`Sign ${type} to ${intent}?`}
    </Device.OperationSummary>
    <Device.SignButton />
  </>
);
