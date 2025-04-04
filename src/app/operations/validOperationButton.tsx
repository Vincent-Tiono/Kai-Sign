import { Check } from "lucide-react";
import { useState } from "react";
import { Button } from "~/components/ui/button";
import { useToast } from "~/hooks/use-toast";
import useOperationStore from "~/store/useOperationStore";
import { useRouter } from "next/navigation";
import { useErc7730Store } from "~/store/erc7730Provider";

interface Props {
  onClick: () => void;
  isValid: boolean;
}

const ValidOperationButton = ({ onClick, isValid }: Props) => {
  const [buttonState, setButtonState] = useState<
    "idle" | "validating" | "validated"
  >("idle");
  const { toast } = useToast();
  const router = useRouter();

  const setValidateOperation = useOperationStore(
    (state) => state.setValidateOperation,
  );

  const selectedOperation = useOperationStore(
    (state) => state.selectedOperation,
  );

  const handleSubmit = () => {
    setButtonState("validated");
    onClick();

    if (selectedOperation) setValidateOperation(selectedOperation);
    
    toast({
      title: "Operation validated",
      description: "The operation has been added to the final JSON.",
    });
    
    setTimeout(() => {
      setButtonState("idle");
    }, 1500);
  };

  return (
    <Button onClick={handleSubmit} disabled={!isValid}>
      {buttonState === "idle" && "Save operation"}
      {buttonState === "validated" && (
        <>
          Saved <Check />
        </>
      )}
    </Button>
  );
};

export default ValidOperationButton;
