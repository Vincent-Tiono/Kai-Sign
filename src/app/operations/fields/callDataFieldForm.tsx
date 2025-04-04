import { FormDescription, FormLabel } from "~/components/ui/form";

const CallDataFieldForm = () => {
  return (
    <div>
      <FormLabel>Call data</FormLabel>
      <FormDescription>
        Data contains a call to another smart contract. To look for relevant
        ERC-7730 files matching this embedded calldata, use callee parameter and
        selector. If an ERC-7730 is not found or if embedded calldata are not
        supported by the wallet, it MAY display a hash of the embedded calldata
        instead, with target calleePath resolved to a trusted name if possible.
      </FormDescription>
      <FormDescription>
        This feature is in progress if you want to do it you can manually add it
        to the json
      </FormDescription>
    </div>
  );
};

export default CallDataFieldForm;
