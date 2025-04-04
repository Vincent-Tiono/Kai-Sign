"use client";

import { RotateCcw } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Erc7730StoreContext } from "~/store/erc7730Provider";
import { useContext } from "react";
import useFunctionStore from "~/store/useOperationStore";
import { useRouter } from "next/navigation";

const ResetButton = () => {
  const clearStorage = useContext(Erc7730StoreContext)?.persist;
  const { reset: resetFunctionStore } = useFunctionStore();
  const router = useRouter();

  const reset = async () => {
    clearStorage?.clearStorage();
    resetFunctionStore();
    router.push("/");
  };

  return (
    <Button variant={"outline"} className="rounded-full" onClick={reset}>
      <RotateCcw /> Reset
    </Button>
  );
};
export default ResetButton;
